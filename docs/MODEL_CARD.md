# Model card: Travel Style Segmentation

**Version:** abfd88e893ca · **Model:** K-Means, k=5 · **Owner:** ITCS355 team 6688012/6688121/6688193.

**Use.** Group 24-category travel-rating profiles for a coursework preference service. Segment names are provisional. This is not a personality test or a high-stakes recommendation system.

**Data.** UCI Travel Review Ratings, DOI 10.24432/C5C31Q, CC BY 4.0. Raw SHA-256: c07e7751f429ebe6225a77a32e61770dbb7197fd253f667e0434424adbaf7a33. The audit accepted 5,454 rows and quarantined two malformed rows. Identical profiles stay in one split: 3,817 training, 817 validation, 820 test. User IDs are excluded from model features.

**Training.** Keep zeros as supplied, then median imputation, standard scaling, and K-Means with seed 42 and n_init=10. Preprocessing is fitted on training data. Validation chooses the configuration; the test set is reserved. Azure training re-fits the selected model and checks equivalence before exporting the tested canonical bundle.

**Observed local quality.** Validation silhouette 0.1448; seed stability ARI 1.0. Held-out silhouette 0.1445, Davies–Bouldin 1.9914. Cluster sizes: 281, 86, 278, 35, 140. GMM validation silhouette was 0.0957. These are clustering metrics, not prediction accuracy.

**Input/output.** Exactly 24 finite numeric ratings in [0,5], batch size 1–100. Invalid input returns 422. A profile above its cluster's training-distance 95th percentile is marked uncertain and returns a null segment with HTTP 200. Distance is not a probability.

**Limits.** The meaning of zeros is unknown. The dataset may not represent current users. Segment names need domain review. There is no causal claim, calibrated confidence, or fairness result. Input drift alone does not prove concept drift.

**Operations.** The bundle includes preprocessing, feature order, centers, mapping, thresholds, and versions. Hash and golden checks gate startup. A semantic canary detects mapping regressions; the staging failure is restored and covered by a regression test. Logs contain derived counts, status, latency, and model version, not full profiles.

**Lineage.** Bundle SHA-256: 71f3ba41b4b964f5beb31e3d6e13b835b1dd2538aa663741d8837301be9dff13. Cloud registry/run/image and deployment evidence are recorded in reports/finish-training-registry.json, finish-assets.json, and finish-deploy.json. Only completed runs support those claims.
