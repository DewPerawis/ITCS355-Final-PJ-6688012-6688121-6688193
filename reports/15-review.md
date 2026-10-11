# 15 review

The saved run failed before paid deployment: RequestDisallowedByAzure. The subscription policy rejects southeastasia.

Allowed regions: centralindia, indonesiacentral, japanwest, malaysiawest, indiasouthcentral. All seven service types list Central India. A separate read-only validation succeeded there. Live checks found 6 DSv2 dedicated cores, 20 regional cores, and one unused Container Apps environment slot. The revised cost plan is 88.89 THB, including an assumed 60 THB reserve. These are assistant checks, not a new notebook run.

The owned group already exists in southeastasia. Azure permits its resources in another region. Reuse it without deleting anything. The template location is explicit.

Notebook 15 now refreshes prices and quota in its first code cell, then checks policy and previews in its second. Run both cells again. Saved outputs are kept until the user reruns; the failed run and old reports are archived under reports/history/15-region-policy/. No paid template has been applied.

Read-only what-if also succeeded with 11 Create changes. No template deployment was started. Eleven targeted policy, ownership, preview/deploy, and quota tests passed in WSL.

The next saved attempt used old notebook code and southeastasia reports, so it stopped before validation. platform_preview now refreshes mismatched cost/quota reports itself. Rerun the existing preview code cell; no notebook reload is needed for this fix. Earlier outputs remain saved.
