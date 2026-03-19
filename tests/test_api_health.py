"""
End-to-End API Health Check
===========================
Runs a lightweight smoke test against every API endpoint in the unified backend.
Does NOT trigger LLM generation or heavy processing — it only validates that each
route returns an expected HTTP status code and (where applicable) a valid JSON shape.

Usage:
    # Make sure the backend is running first:
    #   cd backend && conda run -n fastapi_env python main.py
    #
    # Then in a separate shell, from the project root:
    #   conda run -n fastapi_env python tests/test_api_health.py
    #
    # Or with pytest:
    #   conda run -n fastapi_env pytest tests/test_api_health.py -v

Requirements:  requests  (already available in fastapi_env via httpx/starlette deps)
"""

import sys
import json
import requests
from typing import Optional, List


BASE = "http://localhost:8010"

# ── Colour helpers ───────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

passed = []
failed = []


def check(label: str, method: str, path: str, *,
          expected_status: int = 200,
          json_body: Optional[dict] = None,
          check_keys: Optional[List[str]] = None,
          skip: bool = False,
          skip_reason: str = ""):
    """
    Make an HTTP request and assert the response meets expectations.
    Records pass/fail and prints a coloured result line.
    """
    if skip:
        print(f"  {YELLOW}⏭  SKIP{RESET}  {label}  ({skip_reason})")
        return

    url = BASE + path
    try:
        resp = requests.request(method, url, json=json_body, timeout=10)
    except requests.exceptions.ConnectionError:
        print(f"  {RED}✗  CONN{RESET}  {label}  — backend not reachable at {BASE}")
        failed.append(label)
        return

    ok = resp.status_code == expected_status

    # Optional key presence check
    if ok and check_keys:
        try:
            data = resp.json()
            for key in check_keys:
                if key not in data:
                    ok = False
                    break
        except Exception:
            ok = False

    status_str = f"HTTP {resp.status_code}"
    if ok:
        print(f"  {GREEN}✓  PASS{RESET}  [{status_str}]  {label}")
        passed.append(label)
    else:
        body_preview = resp.text[:120].replace("\n", " ")
        print(f"  {RED}✗  FAIL{RESET}  [{status_str} ≠ {expected_status}]  {label}")
        print(f"         {YELLOW}↳ {body_preview}{RESET}")
        failed.append(label)


# ════════════════════════════════════════════════════════════════════════════
# TESTS
# ════════════════════════════════════════════════════════════════════════════

def run_all():
    print(f"\n{BOLD}{CYAN}━━━  YL Unified App — API Health Check  ━━━{RESET}\n")

    # ── Root ─────────────────────────────────────────────────────────────────
    print(f"{BOLD}[ROOT]{RESET}")
    check("Root index",            "GET",  "/",           check_keys=["status"])
    check("OpenAPI docs reachable","GET",  "/docs",       expected_status=200)

    # ── Dutch ─────────────────────────────────────────────────────────────────
    print(f"\n{BOLD}[DUTCH]{RESET}")
    check("Dutch root",            "GET",  "/api/dutch/",       check_keys=["app"])
    check("Dutch health",          "GET",  "/api/dutch/health", check_keys=["status"])
    check("Dutch generate-theme",  "GET",  "/api/dutch/generate-theme", check_keys=["theme"])

    # Exercise generation calls LLM — skip in smoke test
    check("Dutch exercise (writing)", "GET", "/api/dutch/exercise/writing",
          skip=True, skip_reason="LLM call — use manually")
    check("Dutch exercise (listening)", "GET", "/api/dutch/exercise/listening",
          skip=True, skip_reason="LLM call — use manually")

    # Writing evaluate needs a valid body with user_answer
    check("Dutch evaluate writing",
          "POST", "/api/dutch/evaluate/writing",
          json_body={"exercise_type": "writing", "question": "Beschrijf je dag",
                     "user_answer": "Ik ga naar school.", "theme": "Dagelijkse routine"},
          skip=True, skip_reason="LLM call — use manually")

    check("Dutch TTS",             "GET",  "/api/dutch/tts?text=hallo",
          skip=True, skip_reason="TTS service — use manually")

    # ── The News ─────────────────────────────────────────────────────────────
    print(f"\n{BOLD}[THE NEWS]{RESET}")
    check("News root",             "GET",  "/api/news/",               check_keys=["app"])
    check("News items list",       "GET",  "/api/news/news-items",     expected_status=200)

    # Trigger generation is a background task — safe to call, won't block
    check("News trigger generate", "POST", "/api/news/generate",       check_keys=["status"])

    # Single item by ID — may 404 if DB empty, which is expected on first run
    # Since we can't guarantee data exists, we manually check for 200 or 404.
    r_item = requests.get(f"{BASE}/api/news/news-items/1", timeout=5)
    if r_item.status_code in (200, 404):
        print(f"  {GREEN}✓  PASS{RESET}  [HTTP {r_item.status_code}]  News item endpoint reachable")
        passed.append("News item endpoint")
    else:
        print(f"  {RED}✗  FAIL{RESET}  [HTTP {r_item.status_code}]  News item endpoint failed")
        failed.append("News item endpoint")

    # ── Graphics Generation ───────────────────────────────────────────────────
    print(f"\n{BOLD}[GRAPHICS GENERATION]{RESET}")
    check("Graphics history",      "GET",  "/api/graphics_generation/history",  expected_status=200)
    check("Graphics gallery",      "GET",  "/api/graphics_generation/gallery",  check_keys=["images"])
    check("Media Library alias",   "GET",  "/api/media_library",               check_keys=["images"])
    check("Graphics enhance-prompt",
          "POST", "/api/graphics_generation/enhance-prompt",
          json_body={"prompt": "a sunset over mountains"},
          skip=True, skip_reason="LLM call — use manually")
    check("Graphics generate",
          "POST", "/api/graphics_generation/generate",
          json_body={"original_prompt": "sunset", "improved_prompt": "sunset", "media_type": "image"},
          skip=True, skip_reason="ComfyUI call — use manually")
    check("Graphics status (fake ID)", "GET",
          "/api/graphics_generation/status/nonexistent-id",
          expected_status=200)   # service should return a status dict, not 500

    # ── Scheduler ────────────────────────────────────────────────────────────
    print(f"\n{BOLD}[SCHEDULER]{RESET}")
    check("Scheduler list jobs",   "GET",  "/api/scheduler/",        expected_status=200)

    # Create a job, capture ID, then delete it
    r = requests.post(f"{BASE}/api/scheduler/",
                      json={"task_type": "dutch", "schedule_time": "11:00 PM", "input_number": 1},
                      timeout=10)
    if r.status_code == 200:
        job = r.json()
        job_id = job.get("id", "")
        print(f"  {GREEN}✓  PASS{RESET}  [HTTP 200]  Scheduler create job  (id={job_id[:8]}…)")
        passed.append("Scheduler create job")

        # Delete it
        check(f"Scheduler delete job",
              "DELETE", f"/api/scheduler/{job_id}", expected_status=200)

        # Confirm it's gone — list should not contain it
        jobs_after = requests.get(f"{BASE}/api/scheduler/", timeout=10).json()
        if not any(j.get("id") == job_id for j in jobs_after):
            print(f"  {GREEN}✓  PASS{RESET}  [verification]  Scheduler job correctly removed from list")
            passed.append("Scheduler job removed from list")
        else:
            print(f"  {RED}✗  FAIL{RESET}  [verification]  Job still present after delete!")
            failed.append("Scheduler job removed from list")
    else:
        print(f"  {RED}✗  FAIL{RESET}  [HTTP {r.status_code}]  Scheduler create job")
        failed.append("Scheduler create job")

    check("Scheduler delete non-existent", "DELETE",
          "/api/scheduler/00000000-ffff-ffff-ffff-000000000000",
          expected_status=404)

    # ── Static media ─────────────────────────────────────────────────────────
    print(f"\n{BOLD}[STATIC MEDIA]{RESET}")
    # Just check that the /images mount responds (403 or 404 is fine — it's a directory)
    r_img = requests.get(f"{BASE}/images/", timeout=5)
    if r_img.status_code in (200, 403, 404):
        print(f"  {GREEN}✓  PASS{RESET}  [HTTP {r_img.status_code}]  /images static mount reachable")
        passed.append("Static /images mount")
    else:
        print(f"  {RED}✗  FAIL{RESET}  [HTTP {r_img.status_code}]  /images static mount unexpected response")
        failed.append("Static /images mount")

    # ── Summary ───────────────────────────────────────────────────────────────
    total = len(passed) + len(failed)
    print(f"\n{BOLD}━━━  Results: {GREEN}{len(passed)} passed{RESET}{BOLD}, "
          f"{RED}{len(failed)} failed{RESET}{BOLD}, {total} total  ━━━{RESET}")
    if failed:
        print(f"\n{RED}Failed checks:{RESET}")
        for f in failed:
            print(f"  • {f}")
    else:
        print(f"\n{GREEN}All checks passed! 🎉{RESET}")

    sys.exit(0 if not failed else 1)


# ── pytest compat ─────────────────────────────────────────────────────────────
def test_root():
    r = requests.get(f"{BASE}/", timeout=5)
    assert r.status_code == 200
    assert "status" in r.json()


def test_dutch_health():
    r = requests.get(f"{BASE}/api/health", timeout=5)
    assert r.status_code == 200


def test_dutch_generate_theme():
    r = requests.get(f"{BASE}/api/generate-theme", timeout=5)
    assert r.status_code == 200
    assert "theme" in r.json()


def test_news_list():
    r = requests.get(f"{BASE}/api/v1/news-items", timeout=5)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_news_trigger():
    r = requests.post(f"{BASE}/api/v1/generate", timeout=5)
    assert r.status_code == 200
    assert r.json().get("status") == "started"


def test_graphics_history():
    r = requests.get(f"{BASE}/api/graphics_generation/history", timeout=5)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_graphics_gallery():
    r = requests.get(f"{BASE}/api/graphics_generation/gallery", timeout=5)
    assert r.status_code == 200
    assert "images" in r.json()


def test_scheduler_crud():
    # Create
    r = requests.post(f"{BASE}/api/scheduler/",
                      json={"task_type": "dutch", "schedule_time": "10:00 PM", "input_number": 1}, timeout=5)
    assert r.status_code == 200
    job_id = r.json()["id"]

    # List — should contain our job
    r2 = requests.get(f"{BASE}/api/scheduler/", timeout=5)
    assert any(j["id"] == job_id for j in r2.json())

    # Delete
    r3 = requests.delete(f"{BASE}/api/scheduler/{job_id}", timeout=5)
    assert r3.status_code == 200

    # Confirm gone
    r4 = requests.get(f"{BASE}/api/scheduler/", timeout=5)
    assert not any(j["id"] == job_id for j in r4.json())


def test_scheduler_delete_missing():
    r = requests.delete(f"{BASE}/api/scheduler/00000000-ffff-ffff-ffff-000000000000", timeout=5)
    assert r.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    run_all()
