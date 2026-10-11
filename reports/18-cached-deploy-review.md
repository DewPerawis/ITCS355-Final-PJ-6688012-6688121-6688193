# Deployment retry

The reported traceback still calls run(phase) in the existing notebook kernel. That function can retain an imported version of the deployment module even after the source file changes. The source on disk no longer sends revisionSuffix. The latest failed activity returned during this review still identifies Revision Suffix; activity logs can lag, so this does not prove the latest request had no other issue.

The assets/deploy cell now launches a fresh Python process directly. It does not depend on the setup step function. The successful assets report is reused, with no rebuild or push. The earlier failed report and notebook were archived, and saved outputs/counts were preserved.

Run the updated assets/deploy cell, or use the direct retry code from chat. No cloud write was made during this review. A successful retry still needs actual Azure results.
