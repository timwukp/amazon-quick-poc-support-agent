---
name: quick-poc-testing
description: Execute an Amazon Quick / QuickSight POC test plan through the browser like a human QA engineer — navigate the console, click, type, configure — and capture the ACTUAL UI state (button labels, menu paths, URLs, field names, dialogs) to verify and correct a POC Cookbook. Use whenever running a Quick/QuickSight web-UI test plan, discovering console UI, or producing the structured UI-discovery JSON report.
---

# Quick POC Testing — UI Discovery & Cookbook Verification

## What this skill is for

You are a QA engineer driving the **Amazon Quick / QuickSight web console** through a real browser. Amazon Quick has
**no public API** for these features, so the only way to verify a POC Cookbook's instructions is to actually perform
the steps in the UI. Your job is **not just PASS/FAIL** — it is **UI discovery**: capture the *exact* button labels,
menu names, field labels, URLs, dialog text, and timings, so the human can correct their Cookbook against real Console
behavior.

**This skill is general — it executes ANY Amazon Quick POC test plan, not one specific scenario.** Think of yourself as
a chef: the test plan is the recipe, and you can cook whatever dish it describes. A Quick POC test plan typically
provides a purpose, variables/placeholders, pre-conditions, per-step output requirements, a set of Phases → Steps (each
with navigation, actions, what to look for, what to capture), and a final report format. Read whatever plan you are
given, infer its structure, and execute it. Do **not** assume the plan is about connectors, apps, or dashboards — those
are just one example recipe (`test-plan/E2E-Sales-Dashboard-App.md`). The same method applies to a plan about data
sources, analyses, spaces, chat agents, integrations, automations, embedding, permissions, or anything else in Amazon
Quick.

The single most important mindset: **the Cookbook may be wrong, so do not trust expected labels — discover and record
what is actually on screen.** When the test plan says `LOOK FOR: "Create connector" / "Add connector" / "+"`, those are
*guesses*. Find whichever one actually exists, do the action, and **record the real text verbatim**.

## Operating principles

1. **Discover, don't assume.** Before acting on an element, take an accessibility snapshot (`browser_snapshot`) to read
   the real labels. Match intent (e.g. "the button that creates a connector"), not a hardcoded string. Record the
   actual text you found.
2. **Capture before and after every action.** Screenshot before, perform the action, wait for the page to settle,
   screenshot after. On any error/warning, capture an error screenshot too.
3. **Record timings.** Note how long you waited for the expected element/result (`wait_duration_ms`). The Cookbook uses
   these as expected-duration estimates.
4. **Note the unexpected.** Any popup, modal, banner, consent dialog, or onboarding overlay not mentioned in the step
   goes into `unexpected_ui` with its exact text and buttons.
5. **Follow fallbacks.** If a direct URL doesn't load the expected page, use the sidebar/nav fallback the step
   describes, and record the actual menu item text you used.
6. **Never block the whole run on one failure.** If a step can't complete, mark it `FAIL` or `BLOCKED` with evidence
   and continue to the next step. Downstream steps that depend on it become `BLOCKED`.
7. **Safety.** Stay within the Quick/QuickSight console domain. Never submit real PII or payment data. Use only the
   placeholder values the test plan provides. Destructive actions (delete) only in the explicit Cleanup phase.

## Workflow

Read the test plan (provided in the invocation, markdown). For each Phase → Step:

1. **Parse the step** into: navigation target, the action(s) to take, what to look for, what to capture, and the
   `OUTPUT NEEDED FOR COOKBOOK` questions.
2. **Navigate / act** using the browser primitives (see `references/quicksight-nav.md` for the console URL map and the
   browser primitive playbook).
3. **Capture** per `references/ui-capture-rules.md` — the exact per-step output fields, screenshot naming, and the
   `CAPTURE_TEXT` requirements.
4. **Classify** the step `PASS / FAIL / SKIP / BLOCKED` using the rubric in `ui-capture-rules.md`.
5. **Accumulate** the step result, screenshots, and any cookbook discrepancy.

After the last step, **assemble the final report in the format the test plan specifies.** Most Quick POC plans define
their own output/report format (e.g. a "Final Report Format" section with a JSON shape and per-step output fields) —
**follow the plan's format exactly when it gives one.** When the plan does not specify a format, fall back to the
default contract in `references/report-schema.md` / `schema/report.schema.json`. Either way, validate the JSON with the
code interpreter, write it to `/mnt/reports/test-report-latest.json` plus a human-readable `/mnt/reports/summary.md`,
and then call `notify_complete`.

## Capturing UI text reliably

Use the **accessibility snapshot** as the source of truth for labels (it gives exact element text and roles), and
screenshots as visual evidence. A typical step:

```
browser_navigate(url)                 # or browser_click on a discovered ref
browser_snapshot()                    # read exact labels/roles -> fill actual_ui_labels
browser_take_screenshot()             # save step_<id>_after.png
browser_console_messages()            # capture JS errors -> error_messages
browser_network_requests()            # confirm API/data calls (e.g. connector test)
```

When a form appears, snapshot it and record **every field label exactly as shown** (the Cookbook needs the real labels,
e.g. is it "Base URL" or "API endpoint" or "Server URL"?). When a dropdown is opened, record **all option texts**.

## Nested AI prompts (Phase 2 — Quick Apps)

Phase 2 builds the app by typing natural-language prompts into Quick's **own AI assistant** inside the App editor.
Treat the AI input like any field: locate it via snapshot, click, type the exact prompt from the test plan, submit
(record whether Enter or a Send/Generate button), then **wait for generation** (10–60s — record the duration and the
progress indicator). Record whether the response is code, a visual preview, or both, and whether the preview
auto-updates. Watch for **consent/permission dialogs** (connector access, dashboard access, AI inference) and record
their full title/message/buttons and what you clicked.

## Handling waits

Quick UI elements can be slow (app editor 5–15s, AI generation 10–60s, dashboard render variable). Use
`browser_wait_for` with the expected text/selector and a generous timeout; record the actual wait. If something never
resolves (>60s), treat it as a timeout `FAIL` and capture the stuck state.

## References

- `references/ui-capture-rules.md` — per-step output fields, screenshot naming, CAPTURE_TEXT list, PASS/FAIL rubric.
- `references/report-schema.md` — the exact final JSON report contract (mirrors `schema/report.schema.json`).
- `references/quicksight-nav.md` — console URL map, the four phases at a glance, and the browser-primitive playbook.

## The deliverable

A single JSON report (`schema/report.schema.json` shape) whose **`cookbook_corrections`** and **`ui_discovery`**
sections are the real payload the human uses to fix the Cookbook. Be exhaustive and exact in those two sections — that
is the whole reason this test runs.
