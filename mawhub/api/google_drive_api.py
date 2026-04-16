import io
import os
import json
import frappe
from frappe import _
from requests import post as http_post
from urllib.parse import quote
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from frappe.integrations.google_oauth import GoogleOAuth, is_valid_access_token
from frappe.utils import get_request_site_address, now_datetime

_OUR_CALLBACK = "/api/method/mawhub.api.google_drive_api.google_drive_callback"
_DRIVE_SCOPE = "https://www.googleapis.com/auth/drive"
_DRIVE_CONFIG = {
    "domain_callback_url": "mawhub.api.google_drive_api.google_drive_callback",
    "service_version": ("drive", "v3"),
}


def _get_google_oauth():
    return GoogleOAuth("drive", config=_DRIVE_CONFIG)


def _callback_url():
    return get_request_site_address(True) + _OUR_CALLBACK


@frappe.whitelist()
def authorize_google_drive():
    google_oauth = _get_google_oauth()
    state = json.dumps({"user": frappe.session.user, "redirect": "/app"})

    url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        "access_type=offline&response_type=code&prompt=consent&include_granted_scopes=true"
        f"&client_id={google_oauth.google_settings.client_id}"  # type: ignore[attr-defined]
        f"&scope={quote(_DRIVE_SCOPE, safe='')}"
        f"&redirect_uri={quote(_callback_url(), safe='')}"
        f"&state={quote(state, safe='')}"
    )
    return {"url": url}


@frappe.whitelist(allow_guest=True)
def google_drive_callback(state: str, code: str | None = None, error: str | None = None):
    """Direct OAuth callback — no dependency on Frappe's routing dict."""
    if error:
        frappe.log_error(f"Google Drive OAuth error: {error}", "Google Drive Callback")
        frappe.respond_as_web_page(_("Authorization Failed"), str(error), http_status_code=400)
        return

    state_dict = json.loads(state)
    user = state_dict.get("user")
    redirect = state_dict.get("redirect", "/app")

    google_oauth = _get_google_oauth()
    response = http_post(
        GoogleOAuth.OAUTH_URL,
        data={
            "code": code,
            "client_id": google_oauth.google_settings.client_id,  # type: ignore[attr-defined]
            "client_secret": google_oauth.google_settings.get_password(  # type: ignore[attr-defined]
                "client_secret", raise_exception=False
            ),
            "grant_type": "authorization_code",
            "scope": _DRIVE_SCOPE,
            "redirect_uri": _callback_url(),
        },
    ).json()

    if "error" in response:
        frappe.log_error(json.dumps(response), "Google Drive Token Exchange Error")
        frappe.respond_as_web_page(_("Authorization Failed"), str(response.get("error_description")), http_status_code=400)
        return

    frappe.db.set_value("User", user, "google_drive_token", json.dumps(response))
    frappe.db.commit()

    frappe.local.response["type"] = "redirect"
    frappe.local.response["location"] = redirect


def get_drive_service(user: str | None = None):
    if not user:
        user = frappe.session.user

    token_json = frappe.db.get_value("User", user, "google_drive_token")  # type: ignore[assignment]
    if not token_json:
        return None

    token_dict = json.loads(str(token_json))
    access_token = token_dict.get("access_token")
    refresh_token = token_dict.get("refresh_token")

    google_oauth = _get_google_oauth()

    if not is_valid_access_token(access_token):
        refreshed = google_oauth.refresh_access_token(refresh_token)
        if refreshed:
            token_dict.update(refreshed)
            access_token = token_dict["access_token"]
            frappe.db.set_value("User", user, "google_drive_token", json.dumps(token_dict))  # type: ignore[arg-type]

    return google_oauth.get_google_service_object(access_token, refresh_token)


_TAL_FOLDER_NAME = "tal_assistant"


def _get_or_create_tal_folder(service) -> str:
    """Return the Drive folder ID for 'tal_assistant', creating it if absent."""
    result = service.files().list(
        q=f"name='{_TAL_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        fields="files(id)",
        pageSize=1,
    ).execute()

    files = result.get("files", [])
    if files:
        return files[0]["id"]

    folder = service.files().create(
        body={"name": _TAL_FOLDER_NAME, "mimeType": "application/vnd.google-apps.folder"},
        fields="id",
    ).execute()
    return folder["id"]


@frappe.whitelist()
def upload_interview_to_drive(interview_id: str):
    """Upload interview data as a JSON file into the 'tal_assistant' Drive folder."""
    service = get_drive_service()
    if not service:
        return {"status": "unauthorized", "auth_url": authorize_google_drive().get("url")}

    folder_id = _get_or_create_tal_folder(service)

    interview = frappe.get_doc("Interview", interview_id)
    g = lambda f, default=None: getattr(interview, f, default)  # noqa: E731
    data = {
        "interview": interview_id,
        "job_applicant": g("job_applicant"),
        "job_opening": g("job_opening"),
        "interview_round": g("interview_round"),
        "status": g("status"),
        "scheduled_on": str(g("scheduled_on") or ""),
        "from_time": str(g("from_time") or ""),
        "to_time": str(g("to_time") or ""),
        "average_rating": g("average_rating"),
        "interview_summary": g("interview_summary"),
        "interview_details": [
            {
                "interviewer": getattr(row, "interviewer", None),
                "skill": getattr(row, "skill", None),
                "rating": getattr(row, "rating", None),
                "comments": getattr(row, "comments", None),
            }
            for row in (g("interview_details") or [])
        ],
    }

    file_name = f"Interview_{interview_id}_{now_datetime().strftime('%Y%m%d_%H%M%S')}.json"
    file_content = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")

    file_metadata = {"name": file_name, "parents": [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(file_content), mimetype="application/json")
    result = service.files().create(body=file_metadata, media_body=media, fields="id,webViewLink").execute()

    return {
        "status": "success",
        "file_id": result.get("id"),
        "file_url": result.get("webViewLink"),
        "file_name": file_name,
    }


@frappe.whitelist()
def upload_folder(folder_path):
    """Uploads a folder and its contents to Google Drive."""
    service = get_drive_service()
    if not service:
        return {
            "status": "unauthorized",
            "message": _("Google Drive not authorized."),
            "auth_url": authorize_google_drive().get("url"),
        }

    if not os.path.exists(folder_path):
        frappe.throw(_("Folder path {0} does not exist.").format(folder_path))

    if not os.path.isdir(folder_path):
        frappe.throw(_("{0} is not a directory.").format(folder_path))

    try:
        folder_id = upload_recursive(service, folder_path)
        return {"status": "success", "folder_id": folder_id, "message": _("Folder uploaded successfully.")}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Google Drive Upload Error"))
        frappe.throw(_("Failed to upload folder: {0}").format(str(e)))


def upload_recursive(service, local_path, parent_id=None):
    """Recursively uploads files and folders."""
    base_name = os.path.basename(local_path)

    folder_metadata = {"name": base_name, "mimeType": "application/vnd.google-apps.folder"}
    if parent_id:
        folder_metadata["parents"] = [parent_id]

    drive_folder = service.files().create(body=folder_metadata, fields="id").execute()
    drive_folder_id = drive_folder.get("id")

    for item in os.listdir(local_path):
        item_path = os.path.join(local_path, item)
        if os.path.isdir(item_path):
            upload_recursive(service, item_path, drive_folder_id)
        else:
            upload_file(service, item_path, drive_folder_id)

    return drive_folder_id


def upload_file(service, local_path, parent_id):
    """Uploads a single file to Drive."""
    file_metadata = {"name": os.path.basename(local_path), "parents": [parent_id]}
    media = MediaFileUpload(local_path, resumable=True)
    service.files().create(body=file_metadata, media_body=media, fields="id").execute()
