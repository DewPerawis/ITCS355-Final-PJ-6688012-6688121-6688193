# 12 and 13 review

- User status from 12 at 13:52 UTC has no errors. The CLI finds containerapp 1.3.0b5 and ml 2.45.0. Microsoft.App is still Registering.
- User run 13 completed and saved prices. Priced subtotal: 31.90 THB. Extra-services reserve: 60 THB. Planned total: 91.90 THB before credits and free grants.
- The exchange rate and reserve are assumptions. Storage, logs, alerts, disks, network, and taxes are not individually priced. This is not a spending cap or a bill.
- Notebook 14 is prepared for control-plane permissions and service quota. Three new regression tests passed.
- A separate assistant read-only check at 13:57 UTC found all requested control-plane actions, AML dedicated regional quota 20 cores, AML DSv2 quota 6 cores, and one Container Apps environment slot available. It did not write a user report or notebook output.
- Final app environment CPU quota, policies, data access, complete costs, and deployment remain open.
- Provider registration runs per region; the global Registering state does not block this read-only preparation step.

[Provider registration](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/resource-providers-and-types)
