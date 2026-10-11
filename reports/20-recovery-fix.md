# Staging recovery check

Saved evidence confirms semantic failure detection (503), followed by an unsuccessful recovery check (503). Read-only review found the requested fault setting cleared in Azure, while the live app still failed its semantic canary. A ready response alone does not prove correct mapping.

The fix restores an explicit off setting, uses the supported stop/start operations on the failure app only, and polls for two consecutive passing semantic checks with the expected model version. Detection also waits for the semantic failure instead of accepting a generic unavailable response. The actual runtime cause of the stale mapping is not established by the control-plane state alone.

The recovery phase reuses the saved failure evidence and updates the final report only after recovery passes. The original error and notebook are archived. Rerun Notebook 20 setup and its final failure/alert cell; it chooses recovery only when failure was already detected. No image rebuild or new failure injection is needed for this retry. No cloud writes were performed during this fix.
