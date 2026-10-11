# Study review

Reviewed the user's saved 02-04 results on 11 October 2026.

- Accepted/quarantined rows: 5,454 / 2.
- Split: train 3,817, validation 817, test 820. Duplicate groups across splits: 0.
- Selected model: K-Means, k=5, keep_zero, seed=42.
- Mean validation silhouette: 0.144827. Cross-seed validation ARI: 1.0.
- Test silhouette: 0.144515. Test cluster counts: 281, 86, 278, 35, 140.
- One GMM comparison: validation silhouette 0.095707; it converged.
- Validation uncertain share: 5.875%, using a training-distance percentile threshold.
- Bundle: abfd88e893ca. Saved artifact hash and reload predictions match.

The clusters overlap. ARI here measures agreement across seeds on the same validation rows; it does not prove stable future behavior. The GMM result is one configuration, not a full model comparison. Keeping zeros is a representation choice; zero meaning remains unknown. Distance is not a calibrated confidence probability.

One golden example is uncertain. That is an expected distance warning, not a load failure. Segment names are provisional and need profile review before promotion.

Next: record the saved work in local DVC/MLflow, check the local API, then review Docker/Azure readiness. Registry registration, deployment, real HTTP latency, alerts, cost, and failure recovery are not completed by these saved results.
