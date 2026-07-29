# UI Capture Rules

These mirror the test plan's "Output Requirements (Per Step)". For **every** step, capture all of the following.

## Per-step output fields

| Field | Meaning |
|---|---|
| `step_id` | e.g. "1.1" |
| `step_name` | short step title |
| `status` | `PASS` / `FAIL` / `SKIP` / `BLOCKED` |
| `duration_ms` | time the step took (integer) |
| `actual_url` | browser URL after navigation/action |
| `actual_page_title` | visible page heading/title text |
| `actual_ui_labels` | array of exact button/menu/field/tab texts seen in the action area |
| `action_taken` | what you actually clicked/typed |
| `wait_duration_ms` | how long you waited for the expected element/result |
| `unexpected_ui` | array of popups/modals/banners/overlays not mentioned in the step (with text) |
| `error_messages` | array of exact error/warning texts visible |
| `screenshots` | array of screenshot filenames captured for the step |
| `notes` | free-text observations (e.g. "Button grayed out for 2s before clickable") |

## Screenshot naming

| Type | When | Name |
|---|---|---|
| Before action | before clicking/typing | `step_<id>_before.png` |
| After action | after action completes + page settles | `step_<id>_after.png` |
| Error state | if any error/warning appears | `step_<id>_error.png` |
| Form/dialog | when a form or modal opens | `step_<id>_form.png` / `step_<id>_dialog.png` |
| Full page | at the end of each Phase | `phase_<n>_complete.png` |

Save all screenshots under `/mnt/reports/screenshots/` and list them in `screenshots_manifest`.

### Screenshots are run-local — never commit them

Captures of a real console **always** contain identifiers you cannot see while capturing:

- the **AWS account ID**, rendered in the account-alias dropdown in the top application bar of *every* screen;
- **real email addresses** typed into or listed by share/invite dialogs;
- **asset UUIDs** and account aliases inside URLs shown in success modals and address bars.

So the rules are:

1. **Do not commit raw captures to a repository.** They stay in `/mnt/reports/screenshots/` on the run host and
   are shared out-of-band if a human needs them. `.gitignore` excludes them.
2. **Distil instead.** Write what the capture *shows* — layout, rendering, state, which trap the dialog sets —
   into a text evidence file (`reports/ui-evidence.md` is the example). Text is greppable, diffable and
   reviewable; a PNG is none of those.
3. **Keep `screenshots_manifest` and the `screenshots` step field.** They are the index of what was captured and
   stay valid whether or not the files travel. A filename in the report is a pointer, not an attachment.
4. **Never rely on OCR as the redaction check.** If you must publish an image, OCR misses text dimmed by a modal
   overlay and misreads digits — a real run had OCR report the account ID as `521…` when the pixels read `321…`,
   and miss the top-bar occurrence entirely while catching the same ID in a URL below it. Mask by **position**
   (an unconditional band over the account-alias region), then verify **by eye**. Distilling to text avoids this
   problem rather than fighting it.

## CAPTURE_TEXT — always record the exact wording of

- All **button labels** in the current action area.
- All **menu item names** if a dropdown/menu was opened.
- All **field labels** in any form displayed.
- All **tab names** if tabs are visible.
- **Toast/notification** message text (exact wording).
- Any **error or warning** message text (exact wording).
- **Breadcrumb** text (if visible).
- **Left sidebar** navigation item names (if visible).

These feed the `ui_discovery` and `cookbook_corrections` sections — record them verbatim, not paraphrased.

## Status rubric

- **PASS** — the step's intended outcome was achieved and verified (element appeared / data loaded / success toast).
- **PARTIAL** (record as PASS with a note, or FAIL with a note, per the step's guidance) — outcome partially met
  (e.g. dashboard shows a placeholder instead of a live visual; table headers present but no rows).
- **FAIL** — intended outcome not achieved (error message, blank area, timeout >60s). Capture an error screenshot and
  the exact error text.
- **BLOCKED** — could not attempt because a prerequisite step failed. Record which step blocked it.
- **SKIP** — explicitly optional (e.g. Cleanup) and not performed.

## Cookbook discrepancy capture

Whenever the actual UI text differs from what the test plan / Cookbook expected, add an entry to `cookbook_corrections`:

```json
{
  "step_id": "1.2",
  "cookbook_says": "Click 'Create connector' button",
  "actual_ui": "Button text is 'Add new connector'",
  "correction_needed": true,
  "suggested_correction": "Change 'Create connector' to 'Add new connector'"
}
```

If the actual UI matches expectations, set `correction_needed: false` (or omit) — but still record the real label in
`ui_discovery`.

## Answer the OUTPUT NEEDED FOR COOKBOOK questions

Each step lists explicit questions (e.g. "What is the exact URL path for the Connectors page?"). Make sure every one of
those is answered by a concrete value somewhere in `ui_discovery`. Treat them as the acceptance criteria for the step's
discovery goal.

---

## Absence claims — the highest-risk output this agent produces

A discovery run naturally produces two kinds of statement:

- **"X is at Y, labelled Z"** — a positive finding. Bounded by what you saw; safe.
- **"X does not exist"** — an absence claim. **Unbounded, and almost always wrong when based on UI observation
  alone.**

Absence claims are what downstream readers act on ("there is no way to restrict this, so we need a different
control"). A wrong one propagates into customer-facing designs. Two real failures from actual runs:

1. A run swept seven admin surfaces, found no web-search toggle, and recorded *"no account-level web-search
   control exists."* **Four such controls existed** — documented, on a surface the sweep never reached.
2. Having caught that, the same run then explained the miss as *"the feature is disabled in this account."*
   **Also wrong** — the feature was enabled and usable. The controls simply lived on a *different admin
   surface* whose location was undocumented.

Both errors share one root cause: **an unverified inference written down as a finding.** The first was "we did
not see it, so it does not exist." The second was "we did not see it, so the feature must be off." Neither was
checked before being recorded.

### Rules

1. **Scope every absence claim to what you actually enumerated.** Not *"there is no region setting"* but
   *"none of the N surfaces enumerated below contains a region setting; here is the list."* State N.
2. **Never explain a miss with an unverified cause.** If you did not find something, the finding is *"not found
   on the surfaces reached"* — full stop. "Because the feature is disabled" / "because this account lacks
   permission" / "because it is not released yet" are **hypotheses**. Either test them (open the feature and
   see) or label them as untested hypotheses.
3. **Enumerate structurally, not by guessed text.** Absence by link-text search is not absence — see
   *Enumerate by `href`* in `quicksight-nav.md`. Attach the enumeration (the full anchor/href list) as evidence.
4. **Cross-check against the documentation before asserting absence.** If the official docs name a control you
   could not find, the finding is **"documented to exist; we could not locate its surface"** — not "absent".
   That phrasing is both true and actionable; "absent" is neither.
5. **Distinguish "not observed" from "does not exist" in the report.** Use `NOT_FOUND_ON_SURFACES_REACHED`, not
   `NOT_PRESENT`, unless you enumerated exhaustively and can say what "exhaustively" means.
6. **When UI text and documentation disagree, record an open question — do not pick a side.** A single UI label
   is not sufficient evidence of scope, and neither is a single doc page. Report both verbatim and flag it for
   the service team.

### Report fields

Add these to any step that produces an absence claim:

```json
{
  "claim_type": "absence",
  "surfaces_enumerated": ["/admin/permissions", "/admin/asset-management", "..."],
  "enumeration_method": "all a[href] on the admin nav, matched by path (not link text)",
  "enumeration_count": 34,
  "doc_cross_check": "admin-controls.html names this control but gives no navigation path",
  "status": "NOT_FOUND_ON_SURFACES_REACHED",
  "untested_hypotheses": ["control may live on a separate Quick Suite admin surface"]
}
```

If you cannot fill `surfaces_enumerated` and `enumeration_method`, **you do not yet have an absence finding** —
you have an observation. Record it as one.
