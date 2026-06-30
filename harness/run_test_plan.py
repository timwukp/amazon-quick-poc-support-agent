#!/usr/bin/env python3
"""Human-in-the-loop orchestrator for the Amazon Quick POC UI agent (AgentCore Harness).

Runs a Quick/QuickSight POC test plan through InvokeHarness and handles the inline-function
pause/resume contract so a human can complete the QuickSight IAM Identity Center SSO login via
the AgentCore Browser **Live View** mid-run, then the agent continues in the same authenticated
session.

Because this is driven turn-by-turn from a chat (non-interactive stdin), it works in two phases
and persists pause-state to a JSON file between invocations:

  start   - begin the run; stream until the agent calls a human tool (request_human_login /
            request_human_review) or finishes. On a human tool, save state and print guidance.
  resume  - send the human's result back (e.g. "login done") and continue streaming until the
            next pause or completion.
  status  - print the saved pause state.

Inline-function contract (per the AgentCore dev guide): the stream ends with stopReason "tool_use";
capture toolUseId/name/input; resume by re-invoking the SAME runtimeSessionId with the assistant
toolUse message followed by the user toolResult message (both required).

Usage:
  python run_test_plan.py start  --harness-arn <ARN> --plan test-plan/E2E-Sales-Dashboard-App.md
  python run_test_plan.py resume --result "Human completed SSO login and released control."
  python run_test_plan.py status
"""
import argparse
import json
import os
import secrets
import sys
import uuid

REGION = os.environ.get("AWS_REGION", "us-east-1")
STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".run_state.json")
BROWSER_ID = "aws.browser.v1"
HUMAN_TOOLS = {"request_human_login", "request_human_review"}


def _signal_bucket():
    """Resolve the S3 bucket used for the login-done signal; fail clearly if unset."""
    b = os.environ.get("QUICKPOC_SIGNAL_BUCKET")
    if not b:
        sys.exit("ERROR: QUICKPOC_SIGNAL_BUCKET is not set. Export it to the S3 bucket used for the "
                 "login-done signal, e.g.\n  export QUICKPOC_SIGNAL_BUCKET=quick-poc-agent-skills-<your-account-id>")
    return b


def _client(svc):
    import boto3
    from botocore.config import Config
    # Long read timeout: agent turns include long sleeps / browser waits with quiet gaps in the
    # event stream; the default 60s read timeout would kill the connection mid-run.
    cfg = Config(read_timeout=1800, connect_timeout=60, retries={"max_attempts": 2, "mode": "standard"})
    return boto3.client(svc, region_name=REGION, config=cfg)


def _load():
    with open(STATE, encoding="utf-8") as f:
        return json.load(f)


def _save(st):
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(st, f, indent=2)


def find_browser_live_view():
    """Best-effort: find an active browser session and any live-view info to guide the human."""
    try:
        d = _client("bedrock-agentcore")
        resp = d.list_browser_sessions(browserIdentifier=BROWSER_ID, maxResults=20)
        items = resp.get("items") or resp.get("browserSessionSummaries") or resp.get("sessionSummaries") or []
        active = [x for x in items if str(x.get("status", "")).upper() in ("ACTIVE", "READY", "RUNNING")] or items
        out = []
        for x in active[:5]:
            sid = x.get("sessionId") or x.get("browserSessionId")
            info = {"sessionId": sid, "status": x.get("status")}
            try:
                gs = d.get_browser_session(browserIdentifier=BROWSER_ID, sessionId=sid)
                streams = gs.get("streams", {})
                lv = streams.get("liveViewStream") or streams.get("automationStream") or {}
                if isinstance(lv, dict):
                    info["liveView"] = lv.get("streamEndpoint") or lv.get("endpoint")
            except Exception:
                pass
            out.append(info)
        return out
    except Exception as e:  # noqa: BLE001
        return [{"error": str(e)[:200]}]


def _stream(resp, transcript):
    """Process an InvokeHarness stream. Returns (pending_tool or None).

    A single assistant turn can contain MULTIPLE tool-use content blocks. The Converse stream
    emits one contentBlockStart (carrying toolUseId + name) per tool call, followed by that
    call's input as partial-JSON deltas, then a contentBlockStop. If we accumulated every block's
    input deltas into one shared buffer, the JSON fragments of different calls would concatenate
    into invalid JSON (the old ``{"_raw": ...}`` fallback). So we RESET the input buffer and
    re-capture the toolUseId/name on EACH contentBlockStart that carries a toolUse — keeping only
    the most recent (pending) tool call's input, which is the one the harness is waiting on.
    """
    tool_use_id = tool_name = None
    tool_input = ""
    for event in resp["stream"]:
        if "contentBlockStart" in event:
            start = event["contentBlockStart"].get("start", {})
            if "toolUse" in start:
                # A new tool call begins here: reset the input buffer so we never mix the
                # partial-JSON of a previous tool call into this one's input.
                tool_use_id = start["toolUse"].get("toolUseId")
                tool_name = start["toolUse"].get("name")
                tool_input = ""
        if "contentBlockDelta" in event:
            delta = event["contentBlockDelta"].get("delta", {})
            if "text" in delta:
                sys.stdout.write(delta["text"]); sys.stdout.flush()
                transcript.append(delta["text"])
            if "toolUse" in delta:
                tool_input += delta["toolUse"].get("input", "")
        if "runtimeClientError" in event:
            print(f"\n[runtimeClientError] {event['runtimeClientError'].get('message')}")
    if tool_use_id and tool_name:
        try:
            parsed = json.loads(tool_input) if tool_input.strip() else {}
        except json.JSONDecodeError:
            parsed = {"_raw": tool_input}
        return {"toolUseId": tool_use_id, "name": tool_name, "input": parsed}
    return None


def _handle_pending(harness_arn, session_id, pending):
    """Given a tool_use, decide: human-required (save+stop), or auto-handle (notify_complete)."""
    name = pending["name"]
    # request_human_review can be auto-answered for unattended runs (UI discovery: record + continue).
    if name == "request_human_review" and os.environ.get("QUICKPOC_AUTO_REVIEW"):
        judgment = ("Auto-review (unattended run): you cannot get a human judgment right now. Record exactly what "
                    "the DOM/labels/iframe state show as the finding for this step, mark the step PARTIAL with that "
                    "evidence and the reason you asked, and DO NOT block — continue the test plan and finish with "
                    "notify_complete. For sandboxed/cross-origin preview iframes you cannot read, note that as a "
                    "cookbook finding (preview not verifiable via automation; needs visual check of the screenshot).")
        print(f"\n[auto-review answered for step {pending.get('input',{}).get('step_id','?')}]")
        return _resume_after(harness_arn, session_id, pending, judgment)
    if name in HUMAN_TOOLS:
        st = {"harnessArn": harness_arn, "runtimeSessionId": session_id, "pending": pending}
        _save(st)
        print("\n\n" + "=" * 70)
        if name == "request_human_login":
            print("PAUSED — the agent needs a HUMAN to complete the QuickSight SSO login.")
            print(f"  reason: {pending['input'].get('reason','(n/a)')}")
            print(f"  login URL the agent is on: {pending['input'].get('current_url','(n/a)')}")
            print("\nActive AgentCore Browser session(s) for Live View login:")
            for s in find_browser_live_view():
                print("   ", json.dumps(s))
            print("\nHuman steps:")
            print("  1. AWS Console -> Amazon Bedrock AgentCore -> Built-in tools -> Browser -> Sessions")
            print("  2. On the active session, open 'View live session' (Live View)")
            print("  3. \u26a0\ufe0f  Do NOT click 'Take control'. Complete the IAM Identity Center SSO + MFA login")
            print("     DIRECTLY in the Live View. Clicking Take control / Release control tears down the")
            print("     agent's automation context (see aws/bedrock-agentcore-sdk-python#518) and the run breaks.")
            print("  4. Tell the operator: run  `resume --result \"login done\"`  — the agent then RECONNECTS")
            print("     (re-reads the page) rather than reusing the pre-login handle; the auth carries over.")
        else:  # request_human_review
            print("PAUSED — the agent requests HUMAN REVIEW (visual judgment).")
            print(f"  step: {pending['input'].get('step_id')}  reason: {pending['input'].get('reason')}")
            print(f"  screenshot: {pending['input'].get('screenshot_filename')}")
            print("  Resume with: resume --result \"<your judgment>\"")
        print("=" * 70)
        return "PAUSED_HUMAN"
    if name == "notify_complete":
        print("\n\n" + "=" * 70)
        print("COMPLETE — agent signalled notify_complete:")
        print("  ", json.dumps(pending["input"]))
        print("=" * 70)
        # auto-ack so the agent can finish cleanly, and drain the ack stream so the connection closes
        ack = _resume_call(harness_arn, session_id, pending, "Acknowledged. Report received.")
        try:
            for _ in ack.get("stream", []):
                pass
        except Exception:  # noqa: BLE001
            pass
        if os.path.exists(STATE):
            os.remove(STATE)
        return "COMPLETE"
    # any other unexpected tool_use: auto-ack with a neutral result and continue
    print(f"\n[auto-ack unexpected tool_use: {name}]")
    return _resume_after(harness_arn, session_id, pending, "ok")


def _resume_call(harness_arn, session_id, pending, result_text):
    client = _client("bedrock-agentcore")
    return client.invoke_harness(
        harnessArn=harness_arn,
        runtimeSessionId=session_id,
        messages=[
            {"role": "assistant", "content": [{"toolUse": {
                "toolUseId": pending["toolUseId"], "name": pending["name"], "input": pending["input"]}}]},
            {"role": "user", "content": [{"toolResult": {
                "toolUseId": pending["toolUseId"], "content": [{"text": result_text}], "status": "success"}}]},
        ],
    )


def _resume_after(harness_arn, session_id, pending, result_text):
    transcript = []
    resp = _resume_call(harness_arn, session_id, pending, result_text)
    nxt = _stream(resp, transcript)
    if nxt:
        return _handle_pending(harness_arn, session_id, nxt)
    print("\n\n[stream ended — no further tool calls]")
    if os.path.exists(STATE):
        os.remove(STATE)
    return "DONE"


def cmd_start(args):
    with open(args.plan, encoding="utf-8") as f:
        plan = f.read()
    session_id = args.session_id or f"quickpoc-{uuid.uuid4()}-{secrets.token_hex(4)}"
    prompt = ("Execute the following Amazon Quick / QuickSight POC test plan end to end using the "
              "quick-poc-testing skill. Discover and capture the ACTUAL UI; if you hit a login/SSO "
              "page, call request_human_login and wait. Produce the final JSON report per the plan, "
              "write it to /mnt/reports/test-report-latest.json, then call notify_complete.\n\n"
              "=== TEST PLAN ===\n" + plan)
    print(f"session: {session_id}\n--- streamed response ---")
    client = _client("bedrock-agentcore")
    resp = client.invoke_harness(harnessArn=args.harness_arn, runtimeSessionId=session_id,
                                 messages=[{"role": "user", "content": [{"text": prompt}]}])
    transcript = []
    pending = _stream(resp, transcript)
    if pending:
        return _handle_pending(args.harness_arn, session_id, pending)
    print("\n\n[stream ended — no tool calls; check output above]")
    return "DONE"


def cmd_resume(args):
    st = _load()
    return _resume_after(st["harnessArn"], st["runtimeSessionId"], st["pending"], args.result)


def cmd_live(args):
    """Single uninterrupted turn: open ONE browser session, wait IN-SESSION for a human to log in
    via Live View (poll loop, no pause/resume, no new session), then run the full plan."""
    with open(args.plan, encoding="utf-8") as f:
        plan = f.read()
    SIGNAL_BUCKET = _signal_bucket()
    session_id = args.session_id or f"quickpoc-live-{uuid.uuid4()}-{secrets.token_hex(4)}"
    signal_key = f"signals/{session_id}.flag"
    prompt = (
        "Execute the Amazon Quick / QuickSight POC test plan below using the quick-poc-testing skill.\n\n"
        "LOGIN HANDLING — READ CAREFULLY (avoid breaking the browser context):\n"
        "- Open exactly ONE browser session and KEEP IT OPEN the whole run. Never open a second session.\n"
        f"- Make ONE browser navigate to: {args.start_url}\n"
        "- You land on a sign-in page. DO NOT enter credentials and DO NOT call request_human_login.\n"
        "- Print the browser session id now.\n"
        "- A human will complete the SSO+MFA login directly in Live View WITHOUT clicking 'Take control'.\n"
        "  While they are logging in you MUST NOT touch the browser (no navigate/evaluate/snapshot/new_tab) —\n"
        "  concurrent access (and the Take control / Release control toggle) DESTROYS the automation context.\n"
        "  Instead wait for a LOGIN-DONE signal using the SHELL tool only (never the browser).\n"
        "- Poll loop, up to ~60 iterations: run this SHELL command and read its output —\n"
        f"    python3 -c \"import boto3; boto3.client('s3',region_name='us-east-1').head_object(Bucket='{SIGNAL_BUCKET}',Key='{signal_key}'); print('LOGIN_DONE')\" 2>/dev/null || echo WAITING\n"
        "  If it prints WAITING, use the code interpreter to sleep ~20 seconds, then run the shell check again.\n"
        "  Keep looping while WAITING. As soon as it prints LOGIN_DONE, the human has finished and released control.\n"
        "- ONLY after LOGIN_DONE: the page/context you had BEFORE the human took control is likely dead. Do NOT\n"
        "  just reuse the old page handle. RECONNECT first: re-initialize / re-open the browser session (call the\n"
        "  browser tool's init/start again), then navigate to the start URL and read the page. If a call errors\n"
        "  with 'context/page/browser has been closed' or 'not initialized', RETRY the re-initialize up to 4 times,\n"
        "  sleeping ~15s (code interpreter) between tries, to re-establish a working automation connection to the\n"
        "  session. Once you can read a page: if it is the authenticated Quick console, proceed with the FULL plan;\n"
        "  if it is the sign-in page, the authenticated state did NOT carry over to automation — record that exact\n"
        "  finding (and whether re-init produced a fresh unauthenticated session) and stop. Safety cap: if ~20\n"
        "  minutes pass with no LOGIN_DONE, summarize and stop.\n\n"
        "After login, execute the FULL test plan end to end (discover and capture ACTUAL UI per the skill), "
        "write the JSON report to /mnt/reports/test-report-latest.json and a summary to /mnt/reports/summary.md, "
        "then call notify_complete.\n\n=== TEST PLAN ===\n" + plan
    )
    print(f"session: {session_id}")
    print("SIGNAL when human login is done + control released:")
    print(f"  python harness/run_test_plan.py signal --session-id {session_id}")
    print("--- streamed response ---")
    client = _client("bedrock-agentcore")
    resp = client.invoke_harness(harnessArn=args.harness_arn, runtimeSessionId=session_id,
                                 messages=[{"role": "user", "content": [{"text": prompt}]}])
    transcript = []
    pending = _stream(resp, transcript)
    if pending:
        return _handle_pending(args.harness_arn, session_id, pending)
    print("\n\n[stream ended]")
    return "DONE"


def cmd_signal(args):
    """Write the login-done flag to S3 so the waiting agent proceeds immediately."""
    session_id = args.session_id
    key = f"signals/{session_id}.flag"
    SIGNAL_BUCKET = _signal_bucket()
    s3 = _client("s3")
    s3.put_object(Bucket=SIGNAL_BUCKET, Key=key, Body=b"login-done")
    print(f"OK  wrote signal s3://{SIGNAL_BUCKET}/{key} — the agent's next poll (~20s) will proceed.")


def cmd_status(_args):
    if not os.path.exists(STATE):
        print("no pending state — nothing paused.")
        return
    print(json.dumps(_load(), indent=2))


def main():
    ap = argparse.ArgumentParser(description="Quick POC harness human-in-the-loop orchestrator")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start"); s.add_argument("--harness-arn", required=True)
    s.add_argument("--plan", required=True); s.add_argument("--session-id"); s.set_defaults(fn=cmd_start)
    r = sub.add_parser("resume"); r.add_argument("--result", required=True); r.set_defaults(fn=cmd_resume)
    lv = sub.add_parser("live"); lv.add_argument("--harness-arn", required=True)
    lv.add_argument("--plan", required=True); lv.add_argument("--start-url", required=True)
    lv.add_argument("--session-id"); lv.set_defaults(fn=cmd_live)
    sg = sub.add_parser("signal"); sg.add_argument("--session-id", required=True); sg.set_defaults(fn=cmd_signal)
    st = sub.add_parser("status"); st.set_defaults(fn=cmd_status)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
