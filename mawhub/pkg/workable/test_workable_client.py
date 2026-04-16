"""
Workable API integration tests
================================
Calls every client method against the live API and saves each response as a
.txt file under  mawhub/pkg/workable/responses/.

Run with the bench Python interpreter:
    /path/to/frappe-bench/env/bin/python -m pytest mawhub/pkg/workable/test_workable_client.py -v
or just:
    /path/to/frappe-bench/env/bin/python mawhub/pkg/workable/test_workable_client.py
"""

from __future__ import annotations

import json
import sys
import time
import unittest
from pathlib import Path

# ---------------------------------------------------------------------------
# Bootstrap: load client without going through the Frappe package __init__
# ---------------------------------------------------------------------------
import importlib.util

_PKG_DIR = Path(__file__).parent

def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

_load_module("mawhub.pkg.workable.workable_types", _PKG_DIR / "workable_types.py")
_wc = _load_module("mawhub.pkg.workable.workable_client", _PKG_DIR / "workable_client.py")
WorkableApiClient = _wc.WorkableApiClient

# ---------------------------------------------------------------------------
# Config — override via env vars if needed
# ---------------------------------------------------------------------------
SUBDOMAIN = "lucidya"
API_TOKEN = "BexiVhSqQG0InFOVf2LGFGldTAZon5yuHlfHD9PHc5s"

RESPONSES_DIR = _PKG_DIR / "responses"
RESPONSES_DIR.mkdir(exist_ok=True)

# A published job shortcode discovered during list_jobs — populated at runtime
_PUBLISHED_SHORTCODE: str = ""
_INTERVIEW_CANDIDATE_ID: str = ""
_INTERVIEW_CANDIDATE_SHORTCODE: str = ""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _save(filename: str, data: object) -> None:
    """Pretty-print *data* to responses/<filename>.txt"""
    out = RESPONSES_DIR / filename
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  saved → {out.relative_to(_PKG_DIR)}")


# ---------------------------------------------------------------------------
# Test suite
# ---------------------------------------------------------------------------

class TestWorkableApiClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = WorkableApiClient(subdomain=SUBDOMAIN, api_token=API_TOKEN)

    def setUp(self):
        # Workable rate-limits aggressively; a short pause keeps us well under.
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.client.close()

    # ------------------------------------------------------------------
    # 1. Stages
    # ------------------------------------------------------------------

    def test_01_list_stages(self):
        stages = self.client.list_stages()

        self.assertIsInstance(stages, list)
        self.assertGreater(len(stages), 0, "Expected at least one stage")

        first = stages[0]
        self.assertIn("slug", first)
        self.assertIn("name", first)
        self.assertIn("kind", first)
        self.assertIn("position", first)

        _save("01_list_stages.txt", stages)

    # ------------------------------------------------------------------
    # 2. Jobs
    # ------------------------------------------------------------------

    def test_02_list_jobs_all(self):
        jobs = self.client.list_jobs(limit=10)

        self.assertIsInstance(jobs, list)
        self.assertGreater(len(jobs), 0)

        first = jobs[0]
        for field in ("id", "title", "shortcode", "state"):
            self.assertIn(field, first, f"Missing field: {field}")

        _save("02_list_jobs_all.txt", jobs)

    def test_03_list_jobs_published(self):
        global _PUBLISHED_SHORTCODE
        jobs = self.client.list_jobs(state="published", limit=5)

        self.assertIsInstance(jobs, list)
        for job in jobs:
            self.assertEqual(job["state"], "published")

        if jobs:
            _PUBLISHED_SHORTCODE = jobs[0]["shortcode"]

        _save("03_list_jobs_published.txt", jobs)

    def test_04_list_jobs_archived(self):
        jobs = self.client.list_jobs(state="archived", limit=5)

        self.assertIsInstance(jobs, list)
        for job in jobs:
            self.assertEqual(job["state"], "archived")

        _save("04_list_jobs_archived.txt", jobs)

    def test_05_list_jobs_with_description(self):
        jobs = self.client.list_jobs(state="published", limit=3, include_description=True)

        self.assertIsInstance(jobs, list)
        # At least one job should have a description when include_fields is set
        has_description = any(j.get("description") or j.get("full_description") for j in jobs)
        self.assertTrue(has_description, "Expected description fields to be populated")

        _save("05_list_jobs_with_description.txt", jobs)

    def test_06_list_jobs_updated_after(self):
        jobs = self.client.list_jobs(updated_after="2026-01-01T00:00:00Z", limit=10)

        self.assertIsInstance(jobs, list)

        _save("06_list_jobs_updated_after.txt", jobs)

    def test_07_get_job_detail(self):
        shortcode = _PUBLISHED_SHORTCODE
        if not shortcode:
            self.skipTest("No published shortcode available — run test_03 first")

        job = self.client.get_job(shortcode)

        self.assertIsInstance(job, dict)
        self.assertEqual(job["shortcode"], shortcode)
        for field in ("title", "department", "employment_type", "location"):
            self.assertIn(field, job, f"Missing field in job detail: {field}")

        _save("07_get_job_detail.txt", job)

    # ------------------------------------------------------------------
    # 3. Candidates
    # ------------------------------------------------------------------

    def test_08_list_candidates_global(self):
        candidates = self.client.list_candidates(limit=5)

        self.assertIsInstance(candidates, list)
        self.assertGreater(len(candidates), 0)

        first = candidates[0]
        for field in ("id", "name", "email", "stage", "job"):
            self.assertIn(field, first, f"Missing field: {field}")

        _save("08_list_candidates_global.txt", candidates)

    def test_09_list_candidates_updated_after(self):
        candidates = self.client.list_candidates(
            updated_after="2026-01-01T00:00:00Z", limit=10
        )

        self.assertIsInstance(candidates, list)

        _save("09_list_candidates_updated_after.txt", candidates)

    def test_10_list_job_candidates(self):
        global _INTERVIEW_CANDIDATE_ID, _INTERVIEW_CANDIDATE_SHORTCODE
        shortcode = _PUBLISHED_SHORTCODE
        if not shortcode:
            self.skipTest("No published shortcode available")

        candidates = self.client.list_job_candidates(shortcode, limit=5)

        self.assertIsInstance(candidates, list)
        for c in candidates:
            self.assertEqual(c["job"]["shortcode"], shortcode)

        _save("10_list_job_candidates.txt", candidates)

    def test_11_list_job_candidates_interview_stage(self):
        global _INTERVIEW_CANDIDATE_ID, _INTERVIEW_CANDIDATE_SHORTCODE
        shortcode = _PUBLISHED_SHORTCODE
        if not shortcode:
            self.skipTest("No published shortcode available")

        candidates = self.client.list_job_candidates(shortcode, stage="interview", limit=5)

        self.assertIsInstance(candidates, list)
        for c in candidates:
            self.assertIn(c["stage_kind"], ("interview",))

        if candidates:
            _INTERVIEW_CANDIDATE_ID = candidates[0]["id"]
            _INTERVIEW_CANDIDATE_SHORTCODE = shortcode

        _save("11_list_job_candidates_interview_stage.txt", candidates)

    def test_12_get_candidate_detail(self):
        shortcode = _INTERVIEW_CANDIDATE_SHORTCODE or _PUBLISHED_SHORTCODE
        if not shortcode:
            self.skipTest("No published shortcode available")

        # Fall back to any candidate if no interview-stage one found
        cid = _INTERVIEW_CANDIDATE_ID
        if not cid:
            candidates = self.client.list_job_candidates(shortcode, limit=1)
            if not candidates:
                self.skipTest("No candidates found for job")
            cid = candidates[0]["id"]
            shortcode = candidates[0]["job"]["shortcode"]

        candidate = self.client.get_candidate(shortcode, cid)

        self.assertIsInstance(candidate, dict)
        self.assertEqual(candidate["id"], cid)
        for field in ("name", "email", "stage", "education_entries", "experience_entries"):
            self.assertIn(field, candidate, f"Missing field in candidate detail: {field}")

        _save("12_get_candidate_detail.txt", candidate)

    # ------------------------------------------------------------------
    # 4. Activities
    # ------------------------------------------------------------------

    def test_13_get_candidate_activities(self):
        shortcode = _INTERVIEW_CANDIDATE_SHORTCODE or _PUBLISHED_SHORTCODE
        cid = _INTERVIEW_CANDIDATE_ID
        if not shortcode or not cid:
            self.skipTest("No candidate available — run test_11 or test_12 first")

        activities = self.client.get_candidate_activities(shortcode, cid)

        self.assertIsInstance(activities, list)
        if activities:
            first = activities[0]
            for field in ("id", "action", "created_at"):
                self.assertIn(field, first, f"Missing field in activity: {field}")

        _save("13_get_candidate_activities.txt", activities)

    # ------------------------------------------------------------------
    # 5. Subscriptions
    # ------------------------------------------------------------------

    def test_14_list_subscriptions(self):
        subs = self.client.list_subscriptions()

        self.assertIsInstance(subs, list)
        if subs:
            first = subs[0]
            for field in ("id", "event", "target", "created_at"):
                self.assertIn(field, first, f"Missing field in subscription: {field}")

        _save("14_list_subscriptions.txt", subs)

    # ------------------------------------------------------------------
    # 6. Pagination
    # ------------------------------------------------------------------

    def test_15_pagination_fetches_more_than_one_page(self):
        # Fetch with a tiny page size to force multiple pages
        jobs = self.client.list_jobs(limit=3, paginate=True)

        self.assertIsInstance(jobs, list)
        self.assertGreater(len(jobs), 3, "paginate=True should return more than one page worth")

        _save("15_pagination_all_jobs.txt", {"total": len(jobs), "sample": jobs[:5]})


# ---------------------------------------------------------------------------
# Entry point — run directly without pytest
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main(verbosity=2)
