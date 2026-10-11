# CI custom role fix

Azure has the intended limited custom role at the project group scope, but its returned GUID differs from the UUID previously calculated by the script. The assignment used the calculated UUID, so Azure reported RoleDefinitionDoesNotExist.

The script now looks up the existing role by project name and scope, verifies its exact actions and scope, and uses the role ID returned by Azure. New role creation also uses the returned ID. A bounded retry handles role-definition propagation only; authorization errors are not retried. No permission broadening or role deletion is needed.

The failed report and notebook are archived. Rerun only the ci-setup cell in Notebook 21. No package install or image rebuild is needed. This review reads existing Azure resources; assigning the corrected role is still run by the user.
