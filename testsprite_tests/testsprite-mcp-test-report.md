# TestSprite AI Testing Report(MCP)

---

## 1️⃣ Document Metadata
- **Project Name:** qml (Q-Care Detect / LAKSHYA UI)
- **Date:** 2026-09-10
- **Prepared by:** TestSprite AI Team
- **Scope:** 5 high-priority frontend tests against `http://127.0.0.1:8000` (FastAPI serving `stitchfrontend/dist`), production server mode, no login
- **TestSprite project:** [MCP test dashboard](https://www.testsprite.com/dashboard/mcp/tests/4d497a5f-748e-5e22-94ec-0830cea41048)

---

## 2️⃣ Requirement Validation Summary

### Requirement: Research disclaimer chrome
- **Description:** Header and footer keep the product framed as educational research only and not a medical device.

#### Test TC003 Recognize the research-only framing on load
- **Test Code:** [TC003_Recognize_the_research_only_framing_on_load.py](./TC003_Recognize_the_research_only_framing_on_load.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/4d497a5f-748e-5e22-94ec-0830cea41048/test/f442d4ab-afbb-4be3-a670-129847b35480
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** Home page load shows the header line “Research risk classification — not a medical device, not for clinical use.” and the footer research-environment banner. Chrome language matches the non-clinical product rule.

---

### Requirement: Header tab navigation
- **Description:** Header tabs switch the main research views and update visible content.

#### Test TC004 Switch from Story to Data and preserve tab state
- **Test Code:** [TC004_Switch_from_Story_to_Data_and_preserve_tab_state.py](./TC004_Switch_from_Story_to_Data_and_preserve_tab_state.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/4d497a5f-748e-5e22-94ec-0830cea41048/test/32ac5032-8309-4c79-ad06-857a51deb0e5
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** Story then Data opens the catalog (All 23 tables control visible). The generated script only checks that the Data button exists, not that it has an active/glow class; navigation still worked in the recording.

---

### Requirement: Public data library
- **Description:** Data view lists public tables and saved model names from the catalog API.

#### Test TC008 Open the public data library and see catalog resources
- **Test Code:** [TC008_Open_the_public_data_library_and_see_catalog_resources.py](./TC008_Open_the_public_data_library_and_see_catalog_resources.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/4d497a5f-748e-5e22-94ec-0830cea41048/test/8d5298cf-3e6d-4802-a07b-dec4f06409d1
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** Catalog filter “All 23 tables” and a QSVC model label were visible. The agent also asserted a card titled “ddd”; that is a weak locator and may be a placeholder or odd catalog title worth checking in the UI, not a test failure.

---

### Requirement: Cost latency dashboard
- **Description:** Cost view shows QSVC vs RBF comparison and fit-time tradeoff (not a “quantum is more accurate” claim).

#### Test TC010 View the cost comparison for quantum versus classical models
- **Test Code:** [TC010_View_the_cost_comparison_for_quantum_versus_classical_models.py](./TC010_View_the_cost_comparison_for_quantum_versus_classical_models.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/4d497a5f-748e-5e22-94ec-0830cea41048/test/992a571d-499f-4ce8-8448-5f9755f3ea61
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** Cost tab shows QSVC and RBF labels and the fit-time message that QSVC matches RBF on F1 on this split but takes far longer to fit (~477×). Aligns with pitching cost, not quantum accuracy.

---

### Requirement: Paste a record research score
- **Description:** User pastes `field: number` lines for one table and receives a research score (not a diagnosis).

#### Test TC002 Start a research score from pasted numeric table values
- **Test Code:** [TC002_Start_a_research_score_from_pasted_numeric_table_values.py](./TC002_Start_a_research_score_from_pasted_numeric_table_values.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/4d497a5f-748e-5e22-94ec-0830cea41048/test/0d987be6-52d5-4870-8f74-7818f40b8067
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** More → Paste a record, six `wisconsin_reduced` numeric lines, Score this table. Results area became visible; textarea retained the submitted numbers. No symptom free text was used.

---

## 3️⃣ Coverage & Matching Metrics

- **100.00%** of the five requested tests passed (5/5). Full generated plan had 21 cases; this run was limited to TC003, TC004, TC008, TC010, TC002.

| Requirement | Total Tests | ✅ Passed | ❌ Failed |
|--------------------|-------------|-----------|------------|
| Research disclaimer chrome | 1 | 1 | 0 |
| Header tab navigation | 1 | 1 | 0 |
| Public data library | 1 | 1 | 0 |
| Cost latency dashboard | 1 | 1 | 0 |
| Paste a record research score | 1 | 1 | 0 |

---

## 4️⃣ Key Gaps / Risks

This slice did **not** run locked PDF (TC006), missing-input validation (TC017–TC020), or symptom refusal (TC021). Those remain the highest residual UI risks if you expand coverage later.

Generated locators are brittle (CSS `.p-3 > div > .w-8` for the score panel; exact “ddd” text; “All 23 tables” count). Catalog size or copy changes will flake the tests without a product bug.

Cloud TestSprite reached the app through a tunnel to localhost:8000. Re-runs need uvicorn still serving the Vite `dist` build.
