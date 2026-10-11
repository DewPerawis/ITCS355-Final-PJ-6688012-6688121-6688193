# GitHub workflow evidence

The error log contains GitHub HTTP 404. Read-only checks confirmed repository access succeeds, but published workflows, repository variables, and environments are all empty. The local ci.yml is untracked. This is missing GitHub setup/publication, not a registry or Azure deployment failure.

The checker now reports a missing workflow as pending evidence, while repository access errors still fail. Notebook 21 has a user-run settings cell that creates staging, allows main, and sets exactly the five prepared repository variables. It does not commit, push, or dispatch workflows. Review and push the required source, workflow, dependencies, configuration, and public evidence, then save a successful run and a test failure that skips deployment for the same commit.

Registry version 1 and actual alert evidence already passed. Retry ci-evidence only after the GitHub steps. Earlier errors and notebook outputs were preserved. No GitHub settings were changed during this review.
