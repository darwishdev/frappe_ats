import json
import re
from typing import List, NotRequired, TypedDict

from mawhub.app.job.agent.document_parser_agent import ParsedDocumentFinalEvent
from mawhub.sqltypes.table_models import ParsedDocument, ParsedDocumentSection

class ParsedSection(TypedDict, total=False):
    name: str
    description: NotRequired[str]
    bullet_points: NotRequired[List[str]]
    footer: NotRequired[List[str]]

class ParsedDocumentSectionDTO(TypedDict, total=False):
    title: str
    description: NotRequired[str]
    bullet_points: NotRequired[List[str]]

class ParsedDocumentDTO(TypedDict, total=False):
    file_path: str
    file_hash: str
    meta_data: dict[str,str]
    request_id: str
    sections: List[ParsedDocumentSectionDTO]
class ParsedDocumentOutput(TypedDict, total=False):
    meta_data: dict[str,str]
    sections: List[ParsedDocumentSectionDTO]
class ParsedDocumentParseRequest(TypedDict, total=False):
    path: str
    parent_type: str
    parent_id: str
# This inherits all fields from ParsedDocument and adds 'sections'
class ParsedDocumentWithSections(ParsedDocument):
    sections: NotRequired[List[ParsedDocumentSection]]
def parsed_document_dto_to_sql(dto: ParsedDocumentDTO) -> ParsedDocumentWithSections:
    """
    Converts ParsedDocumentDTO (client-side format)
    to ParsedDocumentWithSections (Frappe-compatible format).
    """
    # Create a copy to avoid mutating the original input unexpectedly
    adapted_data: ParsedDocumentWithSections = dict(dto) # type: ignore
    meta_data = adapted_data.get('meta_data')
    if isinstance(meta_data , dict):
        adapted_data['meta_data'] = json.dumps(meta_data)
        # setattr(adapted_data , "meta_data" , meta_data)
    sections = adapted_data.get("sections", [])

    for section in sections:
        points = section.get("bullet_points")
        section["bullet_points"] = json.dumps(points)

    return adapted_data
def parsed_document_agent_to_dto(
    final_event_data: ParsedDocumentFinalEvent,
    path: str,
    file_hash: str,
    request_id: str,
) -> ParsedDocumentDTO:
    """
    Adapts the Workflow's Final Event data into a ParsedDocumentDTO.
    """
    # Map the sections from ParsedSectionEvent to ParsedDocumentSectionDTO
    dto_sections: List[ParsedDocumentSectionDTO] = []
    for section in final_event_data["sections"]:
        dto_sections.append({
            "title": section.get("title") or "Untitled Section",
            "description": section.get("description") or "",
            "bullet_points": section.get("bullet_points") or []
        })

    return {
        "file_path": path,
        "file_hash": file_hash,
        "meta_data": final_event_data["metadata"],
        "sections": dto_sections,
        "request_id": request_id
    }


def parse_to_sections(raw_text:str)->List[ParsedSection]:

    lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
    sections = []

    # Initialize state
    current_section = None
    state = "START" # START, HEADER, DESCRIPTION, BULLETS, FOOTER

    bullet_regex = r"^[●○•\-\*]|^\d+[\.\)]"

    for i in range(len(lines)):
        line = lines[i]

        # --- 1. Detect if this line is a NEW HEADER ---
        # Logic: Short, no period, and NOT a bullet
        is_new_header = (len(line) < 55 and
                         not line.endswith(('.', ':', ';')) and
                         not re.match(bullet_regex, line))

        if is_new_header:
            if current_section:
                sections.append(current_section)

            current_section = {"name": line, "description": "", "bullet_points": [], "footer": ""}
            state = "HEADER"
            continue

        # If we haven't even found the first header yet, skip or put in a 'General' section
        if not current_section:
            current_section = {"name": "General", "description": line, "bullet_points": [], "footer": ""}
            state = "DESCRIPTION"
            continue

        # --- 2. State Management ---

        # Is it a bullet?
        if re.match(bullet_regex, line):
            clean_bullet = re.sub(r"^[●○•\-\*]|^\d+[\.\)]\s*", "", line).strip()
            current_section["bullet_points"].append(clean_bullet)
            state = "BULLETS"

        # If not a bullet, where does it go?
        else:
            if state in ["HEADER", "DESCRIPTION"]:
                # Still in description phase
                if current_section["description"]:
                    current_section["description"] += " " + line
                else:
                    current_section["description"] = line
                state = "DESCRIPTION"

            elif state == "BULLETS":
                # Text appearing after bullets started is either a continuation or Footer
                # If it's short and the previous line didn't end in a period, it's a continuation
                prev_line = lines[i-1] if i > 0 else ""
                if not prev_line.endswith('.'):
                    current_section["bullet_points"][-1] += " " + line
                else:
                    # It's a Footer
                    if current_section["footer"]:
                        current_section["footer"] += " " + line
                    else:
                        current_section["footer"] = line
                    state = "FOOTER"

            elif state == "FOOTER":
                current_section["footer"] += " " + line

    if current_section:
        sections.append(current_section)

    return sections
