from __future__ import annotations

from pathlib import Path

from fpdf import FPDF, XPos, YPos


OUTPUT_DIR = Path(__file__).resolve().parent
MEMBERS = ("Member 1", "Member 2", "Member 3", "Member 4", "Member 5")
ROLES = {
    "Member 1": "Team Lead; backend app/main.py and integration",
    "Member 2": "Memory grid and app/services",
    "Member 3": "PDF processing",
    "Member 4": "worker/ and tests/",
    "Member 5": "frontend/",
}

DAY_PLANS = [
    {
        "day": 1,
        "phase": "Foundations (Days 1-7)",
        "title": "Repository setup and kickoff",
        "goal": "Establish a runnable repository, agree on module ownership, and record the first project baseline.",
        "tasks": [
            "Confirm Python/tooling setup, inspect repository conventions, and define the backend entry point.",
            "Review the existing memory-grid structure and list setup requirements for its first node.",
            "Inspect PDF dependencies and define the input/output contract for extracted text.",
            "Check the worker and test layout; add a test-running baseline for the team.",
            "Confirm the frontend package starts and document the current application entry point.",
        ],
        "outputs": [
            "Environment and backend startup notes; named tasks and owners.",
            "Memory-grid setup notes and agreed module boundaries.",
            "PDF dependency and extraction contract.",
            "Baseline test command and worker/test ownership notes.",
            "Frontend startup confirmation and entry-point notes.",
        ],
    },
    {
        "day": 2,
        "phase": "Foundations (Days 1-7)",
        "title": "Contracts and skeletons",
        "goal": "Agree on the request, response, and module interfaces before implementation.",
        "tasks": [
            "Define API request/response schemas and record endpoint behavior for prompt and PDF requests.",
            "Define memory-node key/value, capacity, and routing contracts.",
            "Define PDF upload validation and extraction result contracts.",
            "Define process_prompt inputs, outputs, and the initial unit-test layout.",
            "Define the prompt form fields and the API response shape the UI will display.",
        ],
        "outputs": [
            "Documented API contracts and schema skeletons.",
            "Documented grid interfaces and initial node skeleton.",
            "PDF processing contract and sample acceptance cases.",
            "Worker interface and passing baseline test.",
            "UI/API contract agreed with backend.",
        ],
    },
    {
        "day": 3,
        "phase": "Foundations (Days 1-7)",
        "title": "Prompt identity and deterministic routing",
        "goal": "Create stable prompt keys and predictable node selection.",
        "tasks": [
            "Expose and document the prompt request model used by backend routes.",
            "Implement deterministic prompt hashing and GridRouter route selection.",
            "Specify PDF-derived prompt keys and ensure normalized text can be routed.",
            "Add tests for worker input normalization and request identifiers.",
            "Sketch prompt submission states and stable request/response rendering.",
        ],
        "outputs": [
            "API prompt contract remains compatible with routing.",
            "Deterministic route helper with focused tests.",
            "Normalized PDF text/key expectations documented.",
            "Worker input and identifier tests.",
            "Prompt form behavior and display states documented.",
        ],
    },
    {
        "day": 4,
        "phase": "Foundations (Days 1-7)",
        "title": "LRU policy and component review",
        "goal": "Validate bounded memory behavior and confirm all modules are ready for integration.",
        "tasks": [
            "Review health and prompt route behavior; prepare a clean integration point for grid calls.",
            "Implement or verify LRU eviction and bounded node capacity.",
            "Add PDF extraction tests for valid input, invalid files, and empty extracted text.",
            "Test worker success, failure, and timeout paths.",
            "Verify frontend startup and identify loading/error states needed by the prompt form.",
        ],
        "outputs": [
            "Backend route checklist and reviewed integration points.",
            "LRU behavior with eviction tests.",
            "PDF parsing edge-case tests.",
            "Worker outcome tests pass.",
            "Frontend state checklist.",
        ],
    },
    {
        "day": 5,
        "phase": "Foundations (Days 1-7)",
        "title": "Day 5 assignment - skeletons and first runnable UI",
        "goal": "All module skeletons work, the backend /health endpoint is live, and React renders.",
        "tasks": [
            "Finish app/main.py with the FastAPI app; make GET /health return {\"status\":\"ok\"}. Add POST /api/prompt and POST /api/pdf/today route stubs, calling Members 2 and 3 modules when ready (a 501 placeholder is acceptable meanwhile). Run `pip install -r requirements.txt`, `uvicorn app.main:app --reload`, and `curl http://localhost:8000/health`. Collect status from Members 2-5 (done/blocked), review and merge their PRs, resolve conflicts, keep main green, and tag day5.",
            "Implement the MemoryNode TTL skeleton in app/services and report whether it is done or blocked.",
            "Implement extract_pdf_text with pypdf and report whether it is done or blocked.",
            "Create the process_prompt skeleton in worker/, add a basic test, and report whether it is done or blocked.",
            "Build and render the React prompt form; report whether it is done or blocked.",
        ],
        "outputs": [
            "main runs and /health returns OK; PRs from all five members are merged. Collect a 2-line status note from each Member 2-5 for the daily report.",
            "MemoryNode TTL skeleton is available in app/services.",
            "extract_pdf_text works with pypdf or clearly reports a blocker.",
            "process_prompt skeleton and its test are present.",
            "React prompt form renders in the frontend.",
        ],
    },
    {
        "day": 6,
        "phase": "Foundations (Days 1-7)",
        "title": "Routing and memory-node integration",
        "goal": "Connect the deterministic router to memory nodes and verify request placement.",
        "tasks": [
            "Wire backend dependencies for route-to-node selection without changing API contracts.",
            "Verify GridRouter selection is stable and nodes expose a usable lookup interface.",
            "Check PDF-derived text can be normalized and passed to grid-facing services.",
            "Add integration tests for route selection and memory lookup.",
            "Review the prompt submission contract against backend response fields.",
        ],
        "outputs": [
            "Backend can access a configured grid.",
            "Router/node integration cases pass.",
            "PDF-to-grid handoff documented and exercised.",
            "Routing and lookup integration tests.",
            "Frontend and backend prompt contract confirmed.",
        ],
    },
    {
        "day": 7,
        "phase": "Foundations (Days 1-7)",
        "title": "Foundation checkpoint",
        "goal": "Complete the setup phase with reviewed module skeletons and a stable foundation branch.",
        "tasks": [
            "Run backend smoke checks and resolve API contract issues before implementation.",
            "Review grid components and document routing, capacity, and expiration behavior.",
            "Review PDF extraction behavior and list unsupported input cases.",
            "Run the full existing test suite and identify integration gaps.",
            "Confirm the frontend can render and record remaining API wiring work.",
        ],
        "outputs": [
            "Backend smoke-check report and phase-one blockers.",
            "Reviewed grid design and component interfaces.",
            "PDF processing limitations documented.",
            "Green baseline test report or explicit blocker list.",
            "Frontend baseline and implementation backlog.",
        ],
    },
    {
        "day": 8,
        "phase": "Implementation (Days 8-14)",
        "title": "GridRouter and LRU implementation",
        "goal": "Implement and verify GridRouter-backed LRU cache placement.",
        "tasks": [
            "Expose grid cache lookup/store behavior to the prompt route while preserving response shape.",
            "Complete GridRouter and LRU integration across configured memory nodes.",
            "Prepare extracted PDF text as a stable key/value for grid storage.",
            "Test cache hit, cache miss, node selection, and eviction behavior.",
            "Display cache state from backend responses when available.",
        ],
        "outputs": [
            "Backend uses the grid integration seam.",
            "GridRouter routes to LRU-managed nodes.",
            "PDF text can be handed to the grid.",
            "Cache routing and eviction tests pass.",
            "Frontend supports cache result display.",
        ],
    },
    {
        "day": 9,
        "phase": "Implementation (Days 8-14)",
        "title": "Memory services and TTL",
        "goal": "Make memory service behavior predictable under expiration and repeated requests.",
        "tasks": [
            "Integrate memory service calls into backend request handling.",
            "Enforce TTL on memory entries and remove stale values on lookup.",
            "Harden PDF text normalization and extraction failure reporting.",
            "Add TTL expiration and service-level regression tests.",
            "Show clear UI states for cache retrieval and expired/missing results.",
        ],
        "outputs": [
            "API request path uses the service layer.",
            "Expired entries are not served.",
            "Normalized extraction output and explicit errors.",
            "TTL/service tests pass.",
            "Frontend handles cache miss and expiration outcomes.",
        ],
    },
    {
        "day": 10,
        "phase": "Implementation (Days 8-14)",
        "title": "Worker integration",
        "goal": "Run prompts through the worker and store successful responses in the memory grid.",
        "tasks": [
            "Call process_prompt from the prompt API and return its status and response.",
            "Support cache lookup before worker execution and cache successful worker output.",
            "Define how PDF-derived text enters worker processing when applicable.",
            "Test worker success, worker failure, timeout, and API response behavior.",
            "Render worker response, status, and errors in the prompt UI.",
        ],
        "outputs": [
            "Prompt route returns worker results.",
            "Repeated prompts return a grid cache hit.",
            "PDF/worker boundary is documented.",
            "Worker/API integration tests pass.",
            "Frontend shows response and failure states.",
        ],
    },
    {
        "day": 11,
        "phase": "Implementation (Days 8-14)",
        "title": "Frontend prompt UI wiring",
        "goal": "Connect the React prompt form to the backend prompt endpoint.",
        "tasks": [
            "Confirm the API response contract and local development URL for the frontend.",
            "Review cache response fields and coordinate any service changes with Member 1.",
            "Provide clear errors for invalid or unreadable PDF requests.",
            "Add API tests for prompt request validation and response fields.",
            "Wire form submission to the API; show loading, result, cache status, and errors.",
        ],
        "outputs": [
            "Stable prompt endpoint contract.",
            "Memory/cache response contract confirmed.",
            "PDF error handling integrated with UI needs.",
            "Prompt endpoint tests pass.",
            "End-to-end prompt submission in React.",
        ],
    },
    {
        "day": 12,
        "phase": "Implementation (Days 8-14)",
        "title": "PDF extraction path",
        "goal": "Complete the PDF processing module and prepare it for the today-match route.",
        "tasks": [
            "Confirm route inputs and response structure for PDF uploads.",
            "Connect extracted PDF text to the service/grid layer as required.",
            "Complete pypdf extraction and validation of uploaded PDF files.",
            "Test extraction, malformed PDFs, and date-match inputs.",
            "Add upload controls and display PDF processing results.",
        ],
        "outputs": [
            "Documented /api/pdf/today contract.",
            "PDF-to-service handoff works.",
            "PDF extractor validates inputs and returns text.",
            "PDF processor tests pass.",
            "Frontend can upload a PDF and display results.",
        ],
    },
    {
        "day": 13,
        "phase": "Implementation (Days 8-14)",
        "title": "/api/pdf/today end-to-end",
        "goal": "Run a real PDF upload through /api/pdf/today and display matching date entries.",
        "tasks": [
            "Wire POST /api/pdf/today to the PDF processor and return match results.",
            "Verify the grid/service path for extracted content where needed.",
            "Validate date matching across supported formats and clear upload failures.",
            "Add end-to-end API tests for PDF upload and expected matches.",
            "Connect PDF upload and result rendering to the frontend.",
        ],
        "outputs": [
            "/api/pdf/today handles a valid upload end-to-end.",
            "Extracted content handoff is verified.",
            "Date matching and validation behavior documented.",
            "End-to-end PDF route tests pass.",
            "UI displays PDF matches and errors.",
        ],
    },
    {
        "day": 14,
        "phase": "Implementation (Days 8-14)",
        "title": "Implementation integration checkpoint",
        "goal": "Stabilize GridRouter LRU, worker, prompt UI, and PDF endpoint before the final integration phase.",
        "tasks": [
            "Run prompt and PDF API flows together and fix contract mismatches.",
            "Run grid routing, LRU, and TTL tests together.",
            "Run PDF extraction and /api/pdf/today integration tests.",
            "Run worker/API end-to-end tests and fix regressions.",
            "Verify both prompt and PDF workflows in the frontend.",
        ],
        "outputs": [
            "Prompt and PDF API flows pass.",
            "Grid, LRU, and TTL tests pass.",
            "PDF integration tests pass.",
            "Worker integration suite is green.",
            "Frontend can demonstrate both workflows.",
        ],
    },
    {
        "day": 15,
        "phase": "Integration and demo (Days 15-20)",
        "title": "Full-stack integration",
        "goal": "Run the complete system locally with frontend, API, worker, PDF processor, and memory grid.",
        "tasks": [
            "Document the exact local startup sequence and verify all API routes.",
            "Verify all memory nodes are initialized and cache behavior is observable.",
            "Test representative PDFs and provide known input/output examples.",
            "Run the full test suite and report integration failures.",
            "Validate frontend configuration against the running backend.",
        ],
        "outputs": [
            "Reproducible local startup and endpoint check.",
            "Grid status and cache behavior verified.",
            "PDF demo samples/results documented.",
            "Full test report with blockers resolved or assigned.",
            "Frontend communicates with the local API.",
        ],
    },
    {
        "day": 16,
        "phase": "Integration and demo (Days 15-20)",
        "title": "Observability and reliability",
        "goal": "Make requests, failures, and cache behavior understandable during a demo.",
        "tasks": [
            "Check health, validation, and failure responses across public routes.",
            "Review cache/node statistics and identify stale-state risks.",
            "Verify PDF processing failures are reported without hiding the cause.",
            "Test timeout, failure, and repeated-request behavior; record results.",
            "Show useful status, loading, and failure feedback in the interface.",
        ],
        "outputs": [
            "Health and error responses are consistent.",
            "Node/cache state can be inspected.",
            "PDF failures are visible and actionable.",
            "Reliability regression tests pass.",
            "UI surfaces status and errors clearly.",
        ],
    },
    {
        "day": 17,
        "phase": "Integration and demo (Days 15-20)",
        "title": "UX polish and validation",
        "goal": "Polish the workflows and confirm invalid inputs fail clearly.",
        "tasks": [
            "Verify empty prompt, malformed request, and unavailable dependency responses.",
            "Review grid limits and TTL defaults for demo readiness.",
            "Review supported PDF formats and user-facing validation messages.",
            "Add regression coverage for issues found in the integrated workflow.",
            "Polish form validation, accessibility, and responsive behavior.",
        ],
        "outputs": [
            "API invalid-input cases behave as documented.",
            "Grid configuration suitable for the demo.",
            "PDF constraints are user-visible.",
            "Regression tests cover recent fixes.",
            "Accessible and responsive UI for both flows.",
        ],
    },
    {
        "day": 18,
        "phase": "Integration and demo (Days 15-20)",
        "title": "Release candidate and documentation",
        "goal": "Prepare a stable release candidate with clear setup and demo documentation.",
        "tasks": [
            "Review API documentation and verify examples against live endpoints.",
            "Review grid design notes, node configuration, and cache behavior.",
            "Document PDF endpoint usage and prepare a safe sample input.",
            "Run and record the release-candidate test suite.",
            "Document frontend setup and the prompt/PDF demo steps.",
        ],
        "outputs": [
            "Verified API usage documentation.",
            "Grid design and configuration notes.",
            "PDF usage instructions and demo sample.",
            "Release-candidate test report.",
            "Frontend setup and demo guide.",
        ],
    },
    {
        "day": 19,
        "phase": "Integration and demo (Days 15-20)",
        "title": "Demo rehearsal and fixes",
        "goal": "Rehearse the complete demo, fix remaining defects, and confirm a clean main branch.",
        "tasks": [
            "Rehearse health, prompt cache miss/hit, and PDF endpoint flows.",
            "Monitor node stats and verify the prompt cache hit is repeatable.",
            "Rehearse PDF date extraction and record expected output.",
            "Run all tests after fixes and help resolve cross-module defects.",
            "Rehearse the end-user flow and report usability issues.",
        ],
        "outputs": [
            "Backend demo sequence runs cleanly.",
            "Repeatable grid cache-hit evidence.",
            "PDF demo output matches expectations.",
            "Green test suite on the candidate branch.",
            "Frontend demo flow and issue list.",
        ],
    },
    {
        "day": 20,
        "phase": "Integration and demo (Days 15-20)",
        "title": "Final demo and handoff",
        "goal": "Present the integrated MemoryGrid application and hand off code, tests, and operating notes.",
        "tasks": [
            "Demonstrate /health, prompt processing/cache behavior, and API documentation.",
            "Summarize grid routing, LRU/TTL behavior, and node statistics.",
            "Demonstrate PDF extraction and /api/pdf/today results.",
            "Confirm all tests pass and provide final worker/test handoff notes.",
            "Present the complete prompt and PDF user experience and hand off frontend notes.",
        ],
        "outputs": [
            "Backend runbook and API handoff.",
            "Grid implementation and verification summary.",
            "PDF processing and endpoint handoff.",
            "Final test report and known limitations.",
            "Frontend demo and setup handoff.",
        ],
    },
]


def sanitize_text(value: str) -> str:
    replacements = {
        "\u2014": "-",
        "\u2013": "-",
        "\u201c": '"',
        "\u201d": '"',
        "\u2019": "'",
        "\u2018": "'",
        "\u00a0": " ",
    }
    for source, target in replacements.items():
        value = value.replace(source, target)
    return value.encode("latin-1", "replace").decode("latin-1")


def add_heading(pdf: FPDF, heading: str) -> None:
    pdf.set_font("Helvetica", "B", 13)
    pdf.ln(2)
    pdf.multi_cell(
        0,
        8,
        sanitize_text(heading),
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.set_font("Helvetica", size=10)


def add_bullet(pdf: FPDF, text: str) -> None:
    pdf.multi_cell(
        0,
        6,
        sanitize_text(f"- {text}"),
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )


def generate_daily_pdf(plan: dict) -> Path:
    pdf = FPDF()
    pdf.set_margins(18, 16, 18)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    day_number = plan["day"]
    pdf.set_font("Helvetica", "B", 20)
    pdf.multi_cell(
        0,
        11,
        sanitize_text(f"Day {day_number:02d} Assignment"),
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.set_font("Helvetica", "B", 15)
    pdf.multi_cell(
        0, 9, sanitize_text(plan["title"]), new_x=XPos.LMARGIN, new_y=YPos.NEXT
    )
    pdf.set_font("Helvetica", "I", 10)
    pdf.multi_cell(
        0, 7, sanitize_text(plan["phase"]), new_x=XPos.LMARGIN, new_y=YPos.NEXT
    )
    pdf.set_font("Helvetica", size=10)

    add_heading(pdf, "Day goal")
    add_bullet(pdf, plan["goal"])

    add_heading(pdf, "Per-member assignments and expected outputs")
    for index, member in enumerate(MEMBERS):
        add_heading(pdf, f"{member} - {ROLES[member]}")
        add_bullet(pdf, f"Assignment: {plan['tasks'][index]}")
        add_bullet(pdf, f"Expected output: {plan['outputs'][index]}")

    add_heading(pdf, "GitHub push and review")
    if day_number == 5:
        steps = (
            "Create the branch: git checkout -b member1-day5",
            "Stage the backend and integration test: git add app/main.py tests/test_day5_integration.py",
            'Commit: git commit -m "day5: FastAPI app + /health + route stubs"',
            "Push: git push origin member1-day5",
            "Open a PR; review and merge member2-day5, member3-day5, member4-day5, and member5-day5.",
            "Member 1 resolves conflicts, self-reviews the changes, and merges only after checks pass.",
            "Confirm main is green, then tag and push: git tag day5 && git push origin day5",
        )
    else:
        steps = (
            f"Create a feature branch: git checkout -b member<N>-day{day_number}",
            "Stage only your completed files: git add <files>",
            f'Commit: git commit -m "day{day_number}: <describe your change>"',
            "Push the branch: git push origin <branch>",
            "Open a PR with a summary and test results.",
            "Member 1 reviews each PR, resolves conflicts, and merges only after checks pass.",
            "Confirm main remains green; tag the completed day when the team agrees.",
        )
    for step in steps:
        add_bullet(pdf, step)

    add_heading(pdf, "End-of-day checklist")
    checklist = [
        f"All five members posted a done/blocked status for day {day_number}.",
        "Each expected output is present or has an explicit blocker and owner.",
        "Relevant tests and local smoke checks pass.",
        "Changes are pushed, reviewed, and merged through PRs; main is green.",
        "Record the day summary and remaining follow-up work.",
    ]
    for item in checklist:
        add_bullet(pdf, f"[ ] {item}")

    output_path = OUTPUT_DIR / f"day_{day_number:02d}.pdf"
    pdf.output(str(output_path))
    return output_path


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    generated = [generate_daily_pdf(plan) for plan in DAY_PLANS]
    print(f"Generated {len(generated)} daily assignment PDFs in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
