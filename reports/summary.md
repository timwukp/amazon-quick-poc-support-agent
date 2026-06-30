# Quick POC Test Run — Summary

**Test case:** E2E-SALES-DASHBOARD-APP-001 (v2.0)
**Agent:** AWS Bedrock Harness AgentCore Browser UI
**Region/Account:** us-east-1 / QuickSight-Workshop-<WORKSHOP_ACCOUNT_ID>-us-east-1-1781365531
**Overall status:** PARTIAL — 12 PASS · 6 PARTIAL · 1 FAIL · 2 SKIP (21 steps)

## Headline findings (fix the Cookbook)
1. **Connectors URL is wrong.** `/sn/quicksight-connectors` → *Not Found*. Real path: `/sn/account/{account}/start/integrations?tab=action`, opened from the **Connectors** sidebar item. Page heading **"Connectors"**, subtitle "Connect Quick to other applications", tabs **Available / Create for your team**.
2. **No "Create connector" button.** You pick the **"REST API connection"** card → dialog **"REST API connection details"**, wizard **Connect → Review → Publish**.
3. **Connector field labels:** Name ("Enter name"), "+ Add Description", **Connection type** (Public network), **OAuth Configuration** (Custom OAuth app / Service-to-Service OAuth / **None**), **Base URL** (placeholder `https://mydomain.com`).
4. **Connector actions are auto-generated, NOT configurable.** Review step lists fixed **Delete/Get/Patch/Post/Put** (cols Action/Type/Description). The Cookbook's manual *"GetProducts GET /products"* read action **does not exist**. → 1.4 PARTIAL.
5. **Final connector step is "Publish"**, not Save/Test (access scope: "Everyone in your organization" / "Specific groups"). No test step in the wizard.
6. **App is built by the editor's AI assistant.** App opens as *Untitled App* at `/sn/account/{account}/apps/{app-id}/edit`, auto-renamed from the prompt ("Sales Dashboard"). Chat input placeholder **"Ask Apps to make changes"**, submitted with **Enter** (Send button also present). One prompt produced the table, chart and AI summary as code components.
7. **Consent = per-asset checkboxes.** Dialog **"Confirm use of assets"** lists each asset (e.g. *AI Inference — Read-only access*, *Sales API Connector — Read/Write*) **each with its own checkbox**. Buttons **Deny all / Confirm**. ⚠️ Clicking **Confirm** while an asset checkbox is **unchecked** = that asset is **DENIED** (this happened first pass; recovered via the "Re-approve Sales API Connector" suggestion).
8. **Separate runtime permission dialog** (at preview/run time): options **"Allow one time"** (used once then removed) / **"Allow on this app"** (persists until revoked); buttons **Do not allow / Continue**.
9. **Preview runs in a cross-origin sandboxed iframe** (srcdoc, sandbox=`allow-scripts allow-modals`, title **"Sandbox Error"**). Automation cannot read its DOM → table/chart/AI render must be checked **visually by a human**. → Steps 3.1–3.4 PARTIAL.
10. **Publish flow:** "Publish" → dialog **"Publish your app"** (shows Changes summary; Cancel/Publish) → success dialog **"Your app has been published"** with the **/view/app** URL and buttons **Dismiss / Open**. Status Private → Published. → 4.1 PASS.
11. **Cannot share with an external email.** "Share this app" search placeholder **"Search for name, alias or email"**; permission levels **Viewer / Co-owner**. Typing `pilot-user@example.com` → **"No results found"** and the **Share button stays disabled**. → 4.4 FAIL. Viable sharing = existing directory user, **"Share with all"**, or **"Copy link"**.

## Per-phase result
| Phase | Result |
|---|---|
| 1 — REST API Connector | PASS (1.4 PARTIAL: actions not customizable) |
| 2 — Build App via AI | PASS (consent is per-asset checkbox) |
| 3 — Preview & Verify | PARTIAL (sandboxed iframe, human visual check needed) |
| 4 — Publish & Share | Publish PASS; Share with external email FAIL |
| Cleanup | SKIP (optional; evidence preserved) |

## Artifacts
- Report: `/mnt/reports/test-report-latest.json`
- Screenshots: `/mnt/reports/screenshots/` (20 captured; see screenshots_manifest)
- Human visual review requested for `step_3.1_sandbox_error.png` (preview render).
