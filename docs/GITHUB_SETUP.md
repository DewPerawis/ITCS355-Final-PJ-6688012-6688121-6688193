# GitHub setup

**Historical operations guide.** The demo has finished, cloud cleanup is verified, and the deployment workflow is disabled. The steps below describe the original setup; do not rerun them for final review. Use [LOCAL_REVIEW.md](LOCAL_REVIEW.md) and [FINAL_SUBMISSION.md](FINAL_SUBMISSION.md).

Run Group 4 in Notebook 21 first. The Azure identity uses OIDC, so there is no password to save in GitHub.

After ci-setup, run the new GitHub settings cell in Notebook 21. It creates the staging environment, limits deployment to main, and sets the five repository variables. It does not commit or push. If that cell passes, skip manual steps 1-2 and continue at step 3.

1. In DewPerawis/ITCS355-Final-PJ-6688012-6688121-6688193, open Settings > Environments. Create `staging`. Allow the `main` branch to deploy.
2. Open Settings > Secrets and variables > Actions > Variables. Add these repository variables using the values in your local `tmp/github-variables.json`: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `STORAGE_ACCOUNT`, `CONTAINER_REGISTRY`. Use Variables, as the workflow reads `vars`. Keep the local JSON out of Git.
3. Review the changed files and staged files in GitHub Desktop. Include source, tests, workflow, dependency files, DVC pointers, public reports, and docs. Keep cloud.env, tmp, credentials, raw data, binary models, local rules, and PLAN out. Do not use a blind `git add .`. Commit and push the reviewed work to main yourself.
4. Open Actions > Test and deploy. The push should start a normal run. Wait for tests and deploy to succeed. Save its link. A failure needs the actual job log; do not mark it passed.
5. Open Run workflow on main. Set `demo_failure` to true. This intentionally fails a test. Check that tests failed and deploy was skipped. Save its link. Both runs must use the same commit for the evidence checker.
6. The final notebook cell reads those runs using `gh`. In WSL, check `gh --version` and `gh auth status`. If it is missing, install the Ubuntu GitHub CLI with `sudo apt update` then `sudo apt install gh`, and use `gh auth login` with browser login. Do not paste tokens into a notebook. This setup is run by you.
7. Run Group 5. `ci_evidence_ready: true` means a successful workflow and a test failure that blocked deployment were found for the current commit.

If you use the website without gh, you can inspect and save both links manually, but the automated checker will remain incomplete until gh is available. The deliberate failed run is expected; it is not a production failure demo.
