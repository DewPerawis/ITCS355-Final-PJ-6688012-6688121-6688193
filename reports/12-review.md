# Notebook 12 setup fix

## Timeout follow-up

- The next user report showed a 180-second install timeout, followed by failed status reads. It is kept in `reports/history/12-timeout/`.
- A fast az version read now finds containerapp 1.3.0b5 and ml 2.45.0. No reinstall was performed by the assistant.
- A diagnostic stack showed a status command importing many ML packages. A normal provider read took 89.09 seconds, beyond the old 60-second check limit.
- Setup now reads extension metadata with az version. Core account/provider calls use an empty extension directory for that process only. Login and installed extensions are unchanged.
- A separate status-only check finished in 2.83 seconds with no errors. Microsoft.App was still Registering. It did not replace the user's report.
- All 25 tests passed. Rerun only the notebook's final status cell and save. Continue to 13 while provider registration is pending.
- The existing Container Apps extension also loaded `containerapp show --help` successfully in 22.62 seconds using a temporary extension link. No cloud write or package install was made.

## Earlier install flag fix

- The user run failed to install containerapp. Microsoft.App registration started successfully.
- Azure CLI 2.90.0 lists all available containerapp extension versions as preview. The stable-only install flag was incorrect.
- The script now allows preview and pins extension 1.3.0b5, listed as compatible with this CLI. This does not select preview cloud features.
- Repeat only the setup code cell, then the status cell. A pending or registered provider is not registered again.
- The original notebook, report, and script are kept in `reports/history/12-error/`. Saved outputs are unchanged.
- The installation has not been rerun by the assistant. Keep the same WSL kernel; no project package changes are needed.
- Four setup tests passed after the fix. A separate read-only check still showed Microsoft.App as Registering; it did not replace the user's report.

[Extension install options](https://learn.microsoft.com/en-us/cli/azure/extension?view=azure-cli-latest#az-extension-add)
