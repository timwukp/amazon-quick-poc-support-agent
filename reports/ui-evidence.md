# UI Evidence — distilled from the validated run

The screenshots from the validated run are **deliberately not committed**. They were captured in a temporary
workshop account and contained a real AWS account ID and a real personal email address rendered in the browser
chrome and in dialog fields. Rather than mask them, the useful content is distilled into text here — which is
also more useful to a reader than a PNG, because it is greppable, diffable, and reviewable.

**Policy:** raw captures stay in `/mnt/reports/screenshots/` on the run host and are shared out-of-band if
needed. See "Screenshots are run-local" in `skills/quick-poc-testing/references/ui-capture-rules.md`.

Everything below was read off the captures of run `E2E-SALES-DASHBOARD-APP-001` (v2.0), `us-east-1`. Exact UI
strings for each step are in `test-report-latest.json` (`steps[].actual_ui_labels`); this file records what was
only visible *visually* — layout, rendering, and state that no label list conveys.

## Authenticated shell (`authenticated_home`, `reconnect_check`)

Top application bar, left → right: `☰ Explore` · Amazon Quick logo + wordmark · breadcrumb (`Apps` › asset
name) · then right-aligned: the account-alias dropdown, `?` help, `✕` close. The account alias renders as
`QuickSight-Workshop-<WORKSHOP_ACCOUNT_ID>-us-east-1-<suffix>` — **this is where the account ID appears in every
capture**, which is why none are committed.

`reconnect_check` was taken immediately after the S3 `LOGIN_DONE` signal and confirms the authenticated shell
survived the human Live-View login: same alias, same breadcrumb, no sign-in redirect.

## App editor layout (`step_2.1_*`, `step_2.x_build_complete`)

Three regions:

| Region | Contents |
|---|---|
| Left / centre | the rendered app — heading `Sales Dashboard`, subtitle *"Real-time product data from Sales API"*, an `🤖 AI Sales Insights` card containing a dark `Generate AI Summary` button, then the chart |
| Right rail | the AI assistant's file list as generated code, e.g. `components/AISummary.tsx` — *AI inference component*, `lib/highcharts-setup.ts` — *Highcharts initialization*; a `Published` marker with a live thumbnail; a `2 integrations` chip; suggestion chips `Add interactive filters and sorting`, `Add a data export feature`, `Add a refresh button and last-updated timestamp` |
| Bottom right | chat input `Ask Apps to make changes` with `+` and send affordances; footer *"Usage is subject to AWS Responsible AI Policy"* |

**The app is generated as source files, not as a QuickSight dashboard.** The right rail naming its output
`.tsx` / `.ts` files is the clearest evidence of this and is easy to miss from labels alone.

## Chart rendering (`step_2.x_build_complete`, `step_3.1_preview*`)

A Highcharts **column chart**: y-axis `Revenue ($)` gridlined `0 · 100k · 200k · 300k · 400k`; x-axis
categories `beauty · fragrances · furniture · groceries`; single amber series with legend `Revenue` below the
plot. Bars render at visibly different heights (furniture tallest, beauty near-zero), so the connector data did
reach the chart. This is the visual confirmation the sandboxed iframe (below) prevented the agent from asserting
programmatically.

## The sandbox blocker (`step_3.1_sandbox_error`)

The preview renders inside a **cross-origin sandboxed iframe** — `srcdoc`, `sandbox="allow-scripts
allow-modals"`, iframe `title="Sandbox Error"`. The DOM is unreadable from automation, which is why steps
3.1–3.4 are `PARTIAL` and `request_human_review` was called. The chart described above renders correctly inside
it; the agent simply cannot prove that from the DOM.

**This is a structural limit, not a defect** — any browser agent testing Quick Apps preview hits it. Verify the
preview visually, or drive the published `/view/app` URL instead.

## Consent dialogs — two distinct ones (`step_2.2_*`, `step_3_runtime_permission`)

Build-time `Confirm use of assets` lists each asset on its **own row with its own checkbox** — *AI Inference ·
Read-only access*, *Sales API Connector · Read/Write* — with `Deny all` / `Confirm`.

> ⚠️ The trap: `Confirm` with a row **unchecked** silently **denies** that asset. It reads as "confirm
> everything". This happened on the first pass and was recovered via the assistant's *Re-approve Sales API
> Connector* suggestion — `step_2.2_consent_reapprove` shows the same dialog with the checkbox ticked.

Run-time permission is a **separate** dialog: `Allow one time` (*"Permission is used once and then removed"*) /
`Allow on this app` (*"Permission persists until you revoke it"*), buttons `Do not allow` / `Continue`.

## Publish success (`step_4.1_*`)

`Publish your app` → success modal `Your app has been published` containing a live preview pane, `App name:
Sales Dashboard`, the full view URL, and buttons `Dismiss` / `Open`. The published URL has the form:

```
https://us-east-1.quicksight.aws.amazon.com/sn/account/QuickSight-Workshop-<WORKSHOP_ACCOUNT_ID>-us-east-1-<suffix>/apps/<APP_ID>/view/app
```

The modal renders **over** the still-live editor, and the app status badge flips `Private` → `✓ Published`.

## External-share failure (`step_4.3_*`)

`Share this app`: search field placeholder `Search for name, alias or email`, a role dropdown defaulting to
`Viewer` (other value `Co-owner`), and a **disabled** `Share` button. Typing a non-directory email opens a
single-row dropdown reading `No results found` — and `Share` **stays disabled**, so there is no way to force
the invite.

Below it, `Shared with` lists the existing directory principal (`WSParticipantRole/Participant`) marked
`Owner`; then a `Share with all` toggle (*"Everyone in this account can use this app"*, off) and `Copy link`.

**This is real product behaviour, not an agent defect** — the only working share paths are an existing directory
user, `Share with all`, or `Copy link`. Recorded as step 4.4 `FAIL` plus a cookbook correction.

## What the captures did *not* show

No region selector, data-residency notice, or inference-location setting appeared on any surface in this run.
Per the absence-claim rules in `ui-capture-rules.md`, that is scoped as **not found on the surfaces this run
reached** — the run enumerated the connector, apps, preview, publish and share surfaces only, and is not
evidence about the product as a whole.
