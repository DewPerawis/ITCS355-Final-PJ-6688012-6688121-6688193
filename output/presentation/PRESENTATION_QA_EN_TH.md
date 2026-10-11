# Presentation Q&A — English questions, Thai and English answers

คำถามด้านล่างเป็นคำถามที่คาดว่าอาจถูกถาม ไม่ใช่รายการคำถามที่อาจารย์ยืนยัน คำตอบอิงโค้ดและ saved evidence ของโปรเจกต์ ใช้ส่วนไทยเพื่อเข้าใจ แล้วซ้อมส่วน English answer ให้พูดด้วยคำของตัวเอง ไม่ต้องท่องทุกคำ

หากมีการรันใหม่ ให้ตรวจรายงานก่อนตอบตัวเลข โดยเฉพาะ latency และ cost บริการ cloud อาจถูก cleanup หลัง demo จึงไม่ควรตอบว่า online อยู่ตลอดเวลาโดยไม่ได้ตรวจ

**เริ่มอ่านก่อน:** Q1, Q8–Q10, Q14, Q17, Q21–Q23, Q28–Q30, Q32–Q37 และ Q40–Q42 เป็นแกนที่ช่วยอธิบายงานได้เกือบทั้งหมด

## A. Problem and data

### Q1. What does your project do, and who would use it?

**คำตอบไทย:** เราสร้าง API รับคะแนน 24 หมวดของ profile แล้วจัดเข้าหนึ่งในห้ากลุ่ม แพลตฟอร์มท่องเที่ยวอาจใช้เป็นส่วนหนึ่งของการแบ่งผู้ใช้ตามความสนใจ ผลมี segment, distance, uncertainty และ model version แต่ยังไม่ได้พิสูจน์ความหมายของกลุ่มหรือผลต่อผู้ใช้จริง

**English answer:** Our API groups 24-category travel-rating profiles into five segments. A travel platform could use it to group similar interests. We return the segment, distance, uncertainty, and model version. The segment names are provisional; we have not tested user benefit yet.

**เปิดหลักฐาน:** Slide 2; `docs/MODEL_CARD.md`; `service/app.py`

### Q2. Why is this an MLOps project rather than just a clustering notebook?

**คำตอบไทย:** เราไม่ได้หยุดที่ fit K-Means แต่มีข้อมูลที่เก็บเวอร์ชัน training ที่ทำซ้ำได้ registry/lineage API บน cloud CI/CD monitoring alert การทดลอง failure และ cost report วิชานี้ประเมินระบบรอบโมเดล ไม่ใช่แค่คะแนน clustering

**English answer:** We built the system around the model: versioned data, repeatable training, model registration, a cloud API, CI/CD, monitoring, a real alert, failure recovery, and a cost report. The notebook is only one part of the project.

**เปิดหลักฐาน:** Slide 3; `README.md`; `reports/finish-delivery.json`; course project brief

### Q3. Is this a recommendation system or a personality test?

**คำตอบไทย:** ตอนนี้เป็นบริการจัดกลุ่มคะแนน ไม่ได้เลือกสถานที่หรือจัดอันดับทริปให้ผู้ใช้ และไม่ได้พิสูจน์บุคลิกภาพจากคะแนน เราใช้ชื่อ Segment 1–5 ชั่วคราว เพื่อไม่ตีความความหมายของกลุ่มเกินหลักฐาน

**English answer:** It is a segmentation service. It does not rank places or infer personality. We use neutral names, Segment 1 to Segment 5, because the meaning of each group still needs review.

**เปิดหลักฐาน:** Slides 2/13; `reports/cluster-profiles.csv`; model card

### Q4. Where did the data come from, and can you legally use it?

**คำตอบไทย:** ใช้ UCI Travel Review Ratings ซึ่งมี 24 หมวดและ 5,456 แถว ใช้ CC BY 4.0 จึงใช้และดัดแปลงได้โดยให้เครดิต เราบันทึกแหล่งข้อมูล DOI license และ raw SHA-256 เพื่อระบุไฟล์ที่ใช้จริง [1]

**English answer:** We use the UCI Travel Review Ratings dataset under CC BY 4.0, with attribution. It has 24 rating categories and 5,456 raw rows. We recorded its source, licence, DOI, and file hash.

**เปิดหลักฐาน:** `reports/data-source.json`; Slide 4; แหล่ง UCI [1]

### Q5. What problems did you find in the raw data?

**คำตอบไทย:** พบสองแถวที่มีค่ามาในช่องเกินที่ไม่ควรมี จึง quarantine ไว้แทนการเดาซ่อม เหลือ 5,454 แถวสำหรับเตรียมข้อมูล นอกจากนี้พบศูนย์และ profiles ซ้ำ จึงตรวจนโยบายจัดการศูนย์และกันข้อมูลซ้ำข้ามชุด

**English answer:** Two rows had unexpected extra values. We quarantined them instead of guessing a repair, leaving 5,454 accepted rows. We also checked zero values and duplicate profiles before splitting the data.

**เปิดหลักฐาน:** `reports/data-audit.json` → invalid_rows; `src/data.py`

### Q6. What does a zero rating mean? Why did you keep it?

**คำตอบไทย:** ไม่ทราบความหมายศูนย์แน่ชัด หน้าแหล่งข้อมูลอธิบาย rating 1–5 แต่ไฟล์จริงมีศูนย์ เราเปรียบเทียบ keep_zero กับ zero_as_missing แล้ว keep_zero ถูกเลือกด้วย validation rule จึงเก็บตามเดิม ไม่ได้พิสูจน์ว่าศูนย์แปลว่าไม่ชอบจริง

**English answer:** We do not know the exact meaning of zero. We compared keeping zeros with treating them as missing values. Keeping zeros was selected by our validation rule, but this does not prove their real-world meaning.

**เปิดหลักฐาน:** `reports/selection.json` → zero_policy/zero_meaning; `configs/study.json`; UCI [1]

### Q7. Why did you exclude user IDs and keep duplicate profiles in one split?

**คำตอบไทย:** User ID ไม่ใช่ข้อมูลความชอบจึงไม่ใช้เป็น feature ส่วน profile ที่เหมือนกันทุกคะแนนถ้าอยู่ทั้ง train และ test จะทำให้ประเมินจากข้อมูลซ้ำ เราจึงแบ่งตาม profile hash ให้ข้อมูลเหมือนกันอยู่ชุดเดียวกัน

**English answer:** User IDs do not describe travel preferences. Identical profiles could make evaluation too easy if they appeared in both training and test data. We split by profile hash, so duplicates stay together.

**เปิดหลักฐาน:** `src/data.py` → split_profiles; `reports/prepared-data.json` → cross_split_duplicate_groups

### Q8. How did you split the data and prevent data leakage?

**คำตอบไทย:** ใช้ train 3,817 validation 817 test 820 แถว กัน duplicate ข้ามชุด fit imputation/scaling จาก train และใช้ validation เลือก settings ส่วน test ไม่ได้ใช้เลือก k หรือ zero policy จึงแยกการเรียนรู้ การเลือก และการประเมินไว้

**English answer:** We used 3,817 training rows, 817 validation rows, and 820 test rows. Duplicate profiles stay in one split. Preprocessing is fitted only on training data. Validation selects the settings, and test data is reserved for final evaluation.

**เปิดหลักฐาน:** Slide 4; `src/data.py`, `src/train.py`; `selection.json` → test_used_for_selection

## B. Model and reproducibility

### Q9. Why did you choose K-Means with five clusters?

**คำตอบไทย:** เปรียบเทียบ k=3–8 สาม seeds และสอง zero policies รวม 36 fits โดยมีเงื่อนไข ARI ≥0.8 และแต่ละ validation cluster ≥2% ก่อนเลือก mean silhouette สูงสุด ผลที่ผ่านและได้เลือกคือ keep_zero/k=5 ส่วน GMM ที่ลองมี validation silhouette ต่ำกว่า ไม่ได้เลือก 5 เพียงเพราะอยากให้มีห้าชื่อ

**English answer:** We compared six cluster counts, three seeds, and two zero policies. We required stable assignments and a minimum cluster size, then ranked by validation silhouette. K-Means with five clusters and retained zeros was selected. The GMM comparison scored lower.

**เปิดหลักฐาน:** `configs/study.json`; `reports/selection.json`, `study-summary.csv`; `src/train.py`

### Q10. Your silhouette score is only about 0.1445. Is the model good?

**คำตอบไทย:** ค่านี้สะท้อนว่ากลุ่มไม่ได้แยกกันชัดมาก จึงไม่อ้างว่ากลุ่มดีเยี่ยมหรือมีความหมายต่อผู้ใช้แน่นอน Validation K-Means ดีกว่า GMM ที่ทดลองตาม metric นี้ แต่ยังต้อง domain review/user study งานวิชาเน้นระบบปฏิบัติการของ ML ซึ่งไม่ได้ทำให้ข้อจำกัดโมเดลหายไป

**English answer:** The score suggests limited cluster separation, so we do not claim strong user segments. K-Means scored higher than the GMM we tested on validation data. We still need domain review and user testing. The course focuses on operations, but model limitations remain.

**เปิดหลักฐาน:** Slide 5; `selection.json`; `bundle-manifest.json` → test_metrics; metric definition [2]

### Q11. Does an ARI of 1.0 mean your model is 100% accurate?

**คำตอบไทย:** ไม่ใช่ ARI นี้เปรียบเทียบการจัดกลุ่มจาก seeds ต่างกันบน validation ผล 1.0 คือ assignments ตรงกันเมื่อคำนึงว่าหมายเลขกลุ่มอาจสลับ ไม่ได้เทียบกับ label จริงของผู้ใช้ และไม่รับประกันว่าจะเสถียรกับข้อมูลทุกชุด

**English answer:** No. Here ARI compares cluster assignments across the tested seeds. A value of 1.0 means those assignments agree, allowing for changed cluster numbers. It is not accuracy against real user labels.

**เปิดหลักฐาน:** `src/train.py` → adjusted_rand_score; `selection.json` → stability_ari

### Q12. Why do you use scaling and imputation if your API rejects missing fields?

**คำตอบไทย:** Scaler ทำให้การคำนวณระยะในแต่ละหมวดใช้สเกลที่เหมาะสม เราเก็บ imputer เป็นส่วนหนึ่งของ preprocessing โดยเฉพาะตอนเทียบ zero-as-missing แต่ contract ของ API เข้มงวดกว่า คือรับตัวเลขครบ 24 fields เท่านั้น ไม่ได้เติม field ที่ขาดให้ผู้ใช้

**English answer:** Scaling changes the feature scales used by the distance model. The imputer is part of the training pipeline, including the zero-as-missing comparison. Our API contract still requires all 24 numeric fields; it does not fill missing request fields.

**เปิดหลักฐาน:** `src/train.py` → make_pipeline; `src/bundle.py` → predict_profiles

### Q13. What does the distance mean, and how do you define uncertainty?

**คำตอบไทย:** Distance คือระยะ Euclidean ถึง centroid ของกลุ่มหลัง preprocessing ถ้าเกิน percentile 95 ของระยะ train ภายในกลุ่มนั้น จะ uncertain และ API ไม่ส่งชื่อ segment แต่ตอบ null มันไม่ใช่ calibrated confidence และไม่รับประกันว่า input ใหม่จะ flagged แค่ 5%

**English answer:** Distance is measured to the assigned centroid after preprocessing. We flag a profile if it exceeds its cluster's 95th-percentile training distance. The API then returns a null segment. This is a distance rule, not a calibrated probability.

**เปิดหลักฐาน:** `src/bundle.py`; `bundle-manifest.json` → threshold_rule/thresholds; `service/app.py`

### Q14. What is inside the model bundle, and how do you know the API uses the correct one?

**คำตอบไทย:** Bundle มี preprocessing/โมเดล ลำดับ features mapping thresholds และ version Startup ตรวจ hash กับ manifest ตรวจ package/schema และ golden predictions ก่อน ready ส่วน deployment report ระบุ image digest และ version จึงตามได้ว่าบริการใช้ไฟล์ใด

**English answer:** The bundle contains the pipeline, feature order, segment mapping, distance thresholds, and model version. Startup checks its hash, runtime versions, structure, and golden predictions. The deployment report records the image digest and model version.

**เปิดหลักฐาน:** Slide 5; `service/runtime.py`; `reports/bundle-manifest.json`, `ci-deploy-result.json`

### Q15. Why do you have registry version 1, a model version, a Git commit, and an image digest?

**คำตอบไทย:** เป็นรหัสคนละส่วน Registry version 1 ระบุรุ่นที่ลงทะเบียน model version ระบุ bundle ใน prediction Git commit ระบุ source ส่วน image digest ระบุ container ที่ deploy Image เปลี่ยนได้โดยยังใช้ model version เดิม เมื่อเปลี่ยนโค้ดรอบโมเดลแต่ bundle ไม่เปลี่ยน

**English answer:** They identify different objects: the registry entry, the model bundle, the source code, and the container image. A new image can keep the same model version when the surrounding code changes but the bundle does not.

**เปิดหลักฐาน:** `finish-training-registry.json`, `bundle-manifest.json`, `ci-runs.json`, `ci-deploy-result.json`

### Q16. What makes the training reproducible? Does every push retrain the model?

**คำตอบไทย:** เรา pin raw hash, settings, seed, code/dependency versions และมี DVC stages กับ reproduction script รวมทั้ง Azure job ที่ตรวจ fresh fit จริง แต่ GitHub workflow ปัจจุบันทดสอบและ deploy bundle ที่ตรวจไว้ ไม่ได้ retrain ทุก push และยังไม่มีหลักฐาน scheduled retraining ที่ทำงานต่อเนื่อง

**English answer:** We record data hashes, settings, seeds, source and dependency versions, and repeatable pipeline commands. Azure training also checks a fresh fit. Our current GitHub workflow tests and deploys the verified bundle; it does not retrain on every push.

**เปิดหลักฐาน:** `dvc.yaml`; `scripts/reproduce.py`; `.github/workflows/ci.yml`; `reports/azure-training-proof.json`

### Q17. Did Azure actually train a model, or did you only upload the local model?

**คำตอบไทย:** Azure command job fit ใหม่ตาม selected settings จริง แล้วตรวจ fresh-fit equivalence กับ canonical model ก่อน export canonical bundle เดิมเพื่อล็อก bytes ที่ผ่าน tests แล้ว proof แยก hash ของ retrained pipeline กับ canonical bundle จึงไม่ได้อ้างว่า serialize ใหม่มี bytes ตรงทุกตัว

**English answer:** Azure ran a fresh fit using the selected settings and checked equivalence. After that check, it exported the tested canonical bundle to preserve its bytes. The proof records separate hashes for the fresh serialized pipeline and the canonical bundle.

**เปิดหลักฐาน:** `scripts/train_selected.py`; `reports/azure-training-proof.json` → fresh_fit_equivalent/canonical_export; `finish-training-registry.json`

### Q18. What are golden profiles? Do they prove model quality?

**คำตอบไทย:** เป็น input ห้าตัวอย่างจาก train กลุ่มละหนึ่ง profile พร้อม expected outputs ใช้ตรวจ reload/runtime/mapping regression และ version ไม่ได้พิสูจน์ generalization หรือคุณภาพการจัดกลุ่มกับผู้ใช้ใหม่ทั้งหมด ยังต้องแยกจาก held-out metrics และ user study

**English answer:** They are five saved training profiles, one per cluster, with expected outputs. We use them to catch runtime and mapping regressions. They do not prove generalization or useful recommendations for new users.

**เปิดหลักฐาน:** `src/bundle.py` → golden; `reports/golden-profiles.json`; `service/runtime.py`

### Q19. How can a reviewer reproduce the project after cloud cleanup?

**คำตอบไทย:** ใช้ repo กับ environment/dependency files ดาวน์โหลด public UCI data ตาม source URL แล้วตรวจ raw hash ก่อนรัน reproduction script หลัง cleanup private Blob และ API จะหายไป จึงต้องมีวิธี local reproduce ตาม README และหลักฐานที่เก็บไว้ ไม่บอกว่าข้อมูล private remote ยังอยู่

**English answer:** The reviewer can use the repository, pinned environment files, and public UCI download. The audit checks the raw hash before local reproduction. Cleanup removes the private Blob remote and cloud API, so the README explains the public-data path and saved evidence.

**เปิดหลักฐาน:** `README.md` → Run locally; `reports/data-source.json`; `scripts/reproduce.py`

## C. Serving, CI/CD and security

### Q20. How does your API handle invalid or unexpected input?

**คำตอบไทย:** ตรวจ fields 24 ช่อง ชนิดตัวเลข finite/range และ batch 1–100 ข้อมูลขาดช่อง มี extra field เป็น string/boolean เกินช่วง หรือ batch 101 ได้ 422 ส่วน valid profile ที่ uncertain ได้ 200 และ segment null มันเป็นผลที่ออกแบบไว้ ไม่ใช่ API crash

**English answer:** We require 24 named finite numeric ratings in the range 0–5 and a batch size of 1–100. Invalid input returns 422. A valid but uncertain profile returns 200 with a null segment, rather than a forced label.

**เปิดหลักฐาน:** Slide 6; `service/app.py`, `src/bundle.py`; `tests/test_api.py`

### Q21. What is the difference between health, readiness, and the semantic canary?

**คำตอบไทย:** Health ดูว่า process ตอบได้ Ready ดูว่าโหลด bundle ผ่านจนพร้อมใช้ Canary ส่ง golden inputs แล้วเทียบความหมายของผล กรณี mapping ถูกสลับ health และ ready อาจยัง 200 แต่ canary 503 จึงตรวจปัญหาคนละระดับกัน

**English answer:** Health checks whether the process responds. Readiness checks whether the bundle loaded successfully. The semantic canary compares known predictions with expected outputs. A wrong segment mapping can pass readiness but fail the canary.

**เปิดหลักฐาน:** `service/app.py`; `tests/test_api.py` → test_semantic_canary_detects_staging_mapping_failure

### Q22. What exactly happens in your CI/CD workflow?

**คำตอบไทย:** Job tests ตรวจ portability และ contract/unit tests ก่อน Job deploy ต้องรอ tests ผ่าน แล้ว login/download model ตรวจ hash และ API/runtime tests ก่อน build/push image แบบ digest จากนั้น deploy และตรวจ real HTTP เงื่อนไข deploy จำกัด main และไม่ใช้ pull request เป็นทาง deploy

**English answer:** The tests job runs the audit and contract/unit tests. Deployment depends on it. The deploy job logs in, fetches and checks the model, runs model-based tests, builds an immutable image, deploys it, and checks real HTTP responses. Pull requests do not deploy.

**เปิดหลักฐาน:** Slide 7; `.github/workflows/ci.yml`; `cloudlayer/ci_fetch.py`, `ci_deploy.py`

### Q23. Is the intentional CI failure artificial? What does it actually prove?

**คำตอบไทย:** ใช่ เราตั้ง flag ให้ test หนึ่ง fail เพื่อแสดงเส้นทาง gate โดยควบคุมได้ สิ่งที่พิสูจน์คือเมื่อ tests job ล้มเหลว deploy skipped จริง ไม่ใช่พิสูจน์ว่าจับ bug ทุกชนิดได้ ส่วน meaningful tests อื่นตรวจ input contract bundle integrity และ mapping regression แยกต่างหาก

**English answer:** Yes, we deliberately fail one test to exercise the gate. It proves that a failed tests job skips deployment. It does not prove that every bug is detected. Separate tests check input validation, bundle integrity, and mapping regressions.

**เปิดหลักฐาน:** `tests/test_contract_ci.py` → test_demo_gate; `tests/test_api.py`; `reports/ci-runs.json`

### Q24. Why do you show a red workflow run in your presentation?

**คำตอบไทย:** รอบแดงเป็น deliberate failure ที่เราตั้งใจ ต้องมี tests failure และ deploy skipped ขณะที่รอบ normal ของ source commit เดียวกันต้อง success สีแดงนี้แสดง gate ไม่ใช่บอกว่าการ deploy ปกติล้มเหลว

**English answer:** That run is the deliberate gate demonstration. Tests should fail and deployment should be skipped. The normal run uses the same source commit and succeeds. The two runs show both paths of the workflow.

**เปิดหลักฐาน:** `reports/ci-runs.json`; Actions links ท้ายไฟล์

### Q25. Does CI evidence still apply after the final documentation commit?

**คำตอบไทย:** Applies ได้ถ้า CI inputs ไม่เปลี่ยน โค้ดที่ทดสอบคือ 9fea51a ส่วน commit ถัดมาเก็บ docs/reports/slides เราตรวจ ancestor และ diff ของ code/config/runtime inputs แล้วว่าตรง ถ้ามี source ที่เปลี่ยนหรือยังไม่ commit ต้องรัน CI ใหม่ ไม่ถือว่า pass จากรอบเก่า

**English answer:** Yes, while the CI inputs remain unchanged. The tested source is commit 9fea51a. Later commits saved documentation and evidence. Our check compares the relevant inputs. New or uncommitted source changes require new CI runs.

**เปิดหลักฐาน:** `cloudlayer/finish_ci.py` → CI_INPUTS/same_ci_source/check_runs; `finish-ci-evidence.json`

### Q26. Why use Docker and an image digest instead of a latest tag?

**คำตอบไทย:** Docker บรรจุ service dependencies และ bundle ไว้ด้วยกัน Digest ระบุ image contents ที่ deploy จริงได้แน่นอนกว่า tag ซึ่งอาจชี้ image ใหม่ภายหลัง เราเก็บ digest ใน deployment report เพื่อย้อนตรวจรุ่นได้

**English answer:** Docker packages the service, dependencies, and bundle together. An image digest identifies the deployed image contents, while a tag can later point to another image. We record the digest for traceability.

**เปิดหลักฐาน:** `Dockerfile`; `.github/workflows/ci.yml`; `reports/ci-deploy-result.json`

### Q27. How do you protect credentials? Is the API production-ready?

**คำตอบไทย:** Workflow ใช้ OIDC ไม่ใส่ password/token ถาวรใน source และ cloud identities มีสิทธิ์ตามหน้าที่ API ใช้ HTTPS แต่ endpoint coursework ยัง public ไม่มี user authentication/rate limit ที่เราตรวจไว้ การป้องกัน deployment credentials จึงไม่เท่ากับครบเรื่อง production API security ส่วน joblib ต้องโหลดจาก trusted bundle เท่านั้น

**English answer:** CI uses OIDC instead of a stored deployment password, with scoped permissions. The API uses HTTPS, but it is a public coursework endpoint. We have not added user authentication or verified rate limiting. Production use would need further security work, and model files must be trusted.

**เปิดหลักฐาน:** `.github/workflows/ci.yml`; `cloudlayer/finish_ci.py`; `service/runtime.py`; app ingress config

## D. Monitoring, failure and drift

### Q28. What do you monitor, and do you log user profiles?

**คำตอบไทย:** ติดตาม request status/duration/model version, จำนวน predictions/uncertain และ semantic failures ผ่าน Log Analytics Workbook ไม่ log คะแนน 24 ช่องเต็มใน request logs กราฟที่ใช้ใน presentation วาดจาก query output จริง แต่ไม่ใช่ Portal screenshot

**English answer:** We monitor request status, application latency, model version, prediction counts, uncertainty counts, and semantic failures. We do not log full rating profiles. The presentation graphs use saved log query results, not Portal screenshots.

**เปิดหลักฐาน:** Slide 9; `service/app.py` → middleware/prediction_batch; `reports/dashboard-workbook.json`

### Q29. Did an alert actually fire? Did it send an email?

**คำตอบไทย:** มี actual Azure alert record ว่า fired จาก semantic failure แล้วภายหลัง condition resolved แต่ email_notifications_configured เป็น false จึงยังไม่มีหลักฐาน email ส่งถึงทีม Rule ตรวจ logs ไม่ใช่ตัวที่เรียก canary เองอัตโนมัติ เราใช้ canary requests ในการทดลอง failure

**English answer:** Yes, Azure recorded a fired semantic-failure alert that later resolved. Email notifications are not configured. The alert rule evaluates logs; it does not itself call the canary. Canary requests were made during the failure experiment.

**เปิดหลักฐาน:** `reports/finish-alert.json`, `finish-monitor.json`; `cloudlayer/finish_monitor.py`

### Q30. What failure did you design, and why did you choose it?

**คำตอบไทย:** สลับ cluster-to-segment mapping ใน staging แยก เป็น failure ที่ระบบยังพร้อมและทำนายกลุ่มได้ แต่ชื่อผลผิด หากดูแค่ HTTP 200 จะพลาด Canary จึงต้องตรวจ output semantics เทียบ golden ซึ่งตรวจได้ด้วย 503 และ log event

**English answer:** We swapped two cluster-to-segment mappings in a separate staging app. The model could still run, but the returned meaning was wrong. This shows why HTTP success alone is insufficient. The semantic canary detected the mismatch and returned 503.

**เปิดหลักฐาน:** Slide 10; `service/app.py` → wrong_mapping; `reports/finish-failure.json`

### Q31. Was recovery automatic, and why did it take over seven minutes?

**คำตอบไทย:** ไม่ใช่ alert สั่ง rollback เองอัตโนมัติ เราใช้ config/script action และ retry คืนค่าแล้ว stop/start staging ก่อนตรวจ canary สองครั้ง ครั้งแรกที่พยายามกู้คืนยังไม่ผ่าน เวลารวมจากตรวจพบถึง confirmed recovery จึงประมาณ 7 นาที 16.4 วินาทีรวมการแก้ครั้งแรกที่ไม่สำเร็จ

**English answer:** Recovery was not triggered automatically by the alert. We restored configuration, restarted staging, and confirmed the canary twice. The first recovery attempt failed. The reported detection-to-confirmed-recovery time includes that attempt and is about seven minutes sixteen seconds.

**เปิดหลักฐาน:** `reports/finish-failure.json` → previous_errors/recovery_method/detected_at/recovered_at

### Q32. What did the failure teach you, and how did it improve your tests?

**คำตอบไทย:** Readiness ไม่ได้ตรวจทุก semantic regression หลัง startup เราจึงต้องมี canary และ regression test ที่จงใจสลับ mapping ใน staging แล้วตรวจว่า ready ยัง 200 แต่ canary 503 และมี test กันการ inject นอก staging บทเรียนถูกนำกลับไปตรวจใน CI

**English answer:** Readiness alone does not catch every semantic regression. We added a test where a swapped mapping passes readiness but fails the canary. We also test that failure injection is blocked outside staging. These checks are included in CI.

**เปิดหลักฐาน:** `tests/test_api.py`; `.github/workflows/ci.yml`; `service/app.py`

### Q33. How did you detect input drift?

**คำตอบไทย:** เทียบแต่ละ feature ด้วย two-sample KS และใช้ statistic สูงสุด มี reference 1,908 recent 200 calibration 100 รอบ Threshold ประมาณ 0.1257 Normal score 0.0994 ไม่ flagged ส่วนบวก 1.5 ในสี่ features แรกแล้ว clip 0–5 ได้ 0.7879 จึง flagged นี่คือ controlled offline test

**English answer:** We use the maximum feature-wise two-sample KS statistic. Training windows calibrate the threshold. A normal sample stayed below it, while a controlled shift in four features exceeded it. This is an offline experiment, not observed live drift.

**เปิดหลักฐาน:** Slide 11; `monitoring/drift.py`; `reports/input-drift.json`

### Q34. What is the difference between input drift and concept drift?

**คำตอบไทย:** Input drift คือการกระจาย features เปลี่ยน ส่วน concept drift คือความสัมพันธ์ input กับ outcome เปลี่ยน งานนี้ไม่มี labels/outcomes หรือ timestamps สำหรับตรวจความสัมพันธ์ตามเวลา จึงไม่อ้างว่าตรวจ concept drift หรือพิสูจน์ว่าคุณภาพโมเดลลดลงจาก drift score ได้

**English answer:** Input drift changes the feature distribution. Concept drift changes the relationship between inputs and outcomes. We do not have the outcome labels or time information needed to demonstrate concept drift. An input-drift flag alone does not prove quality loss.

**เปิดหลักฐาน:** `reports/input-drift.json` → limits; model card

### Q35. Is feature-drift monitoring live? Is it the same as your Azure alert?

**คำตอบไทย:** ยังไม่ live เป็น offline test ที่ดัดแปลงข้อมูลโดยรู้ว่าทำอะไร Azure alert จริงมาจาก semantic mapping failure คนละเรื่อง ไม่ได้ดึง features ผู้ใช้มาคำนวณ rolling window แล้วสั่ง retrain อัตโนมัติ

**English answer:** No. Feature drift was tested offline with a controlled shift. The real Azure alert came from a semantic mapping failure. We have not connected live feature windows or automatic retraining to the drift check.

**เปิดหลักฐาน:** `reports/input-drift.json`; `finish-alert.json`; `monitoring/drift.py`, `cloudlayer/finish_monitor.py`

## E. Latency, cost and limits

### Q36. What does p95 mean, and did you meet your latency target?

**คำตอบไทย:** p95 คือประมาณ 95% ของ samples ในรอบทดสอบไม่เกินเวลานี้ ไม่ใช่ mean Local ได้ 274.54 ms ผ่านเป้า 300 แต่ cloud 813.77 และ pooled-client 624.83 ms ยังไม่ผ่าน วัด 200 requests concurrency 10 batch 1 errors 0 เลข 300 เป็น target ทีม ไม่ใช่เลข fixed ใน brief

**English answer:** P95 means about 95% of measured samples are no slower than that value. Local p95 was 274.54 ms, but both cloud measurements exceeded our 300 ms target. Each warm test used 200 requests, concurrency ten, and batch size one, with zero errors.

**เปิดหลักฐาน:** Slide 8; local-load/azure-load/pooled-load reports; proposal targets

### Q37. Why is the cloud slower? Does connection pooling solve it?

**คำตอบไทย:** Client HTTPS รวม network และ parsing ในขณะที่ server logs วัดใน app เรายังไม่ได้แยก causal root cause ทั้งหมด Pooled client วัดได้ต่ำลงแต่เปลี่ยนวิธี client/warm-up และยังเกินเป้า จึงไม่บอกว่า Azure หรือ server เป็นสาเหตุทั้งหมดหรือแก้เสร็จแล้ว

**English answer:** Client HTTPS timing includes the network path and response parsing. We have not isolated every cause. The pooled-client result was lower, but the method also changed and still missed the target. Next we would separate client, network, and application timing.

**เปิดหลักฐาน:** `scripts/http_check.py`, `scripts/check_pooled_load.py`; `reports/pooled-load.json`; Slide 8

### Q38. How did you measure cold start? Is 3.82 seconds a cold-start p95?

**คำตอบไทย:** รอแล้วตรวจผ่าน ARM ว่า active revision มี zero replicas จริง จากนั้นจับเวลาหนึ่ง HTTPS readiness request ได้ประมาณ 3.82 วินาที รวม network และ scale activation ไม่ใช่ p95 และเป็นผลกับ image ที่ระบุใน cold report ไม่ได้วัด image ล่าสุดใหม่ทุกครั้ง

**English answer:** We confirmed zero replicas through Azure's resource state, then timed one HTTPS readiness request. It took about 3.82 seconds, including network and scale activation. It is one sample for the image recorded in the report, not a cold-start p95.

**เปิดหลักฐาน:** `reports/finish-cold.json`; `cloudlayer/finish_serve.py` → cold/revision checks

### Q39. Why did you use scale-to-zero? Can your system handle much higher traffic?

**คำตอบไทย:** ลด idle compute สำหรับ demo ที่ใช้งานเป็นช่วง ๆ แต่แลกกับ cold delay App จำกัดหนึ่ง replica และผล load 200 requests concurrency 10 ไม่ใช่หลักฐานรองรับ traffic สูงมาก แม้ batch 100 ผ่านก็ไม่เท่ากับทดสอบ throughput สูงทุก workload

**English answer:** Scale-to-zero reduces idle compute for a short demo, but adds cold-start delay. We cap the app at one replica. Our tests cover a limited workload, so we do not claim production-scale traffic capacity.

**เปิดหลักฐาน:** `cloudlayer/finish_serve.py` → app_body; `reports/azure-load.json`, `pooled-load.json`

### Q40. How did you calculate cost per 1,000 predictions?

**คำตอบไทย:** แผน 88.89 THB ÷ 10,000 ×1,000 =8.89 THB ส่วน reported จริงใช้ resource-group pre-tax cost 0.0012035014 USD ÷841 valid profiles ที่สังเกตในช่วงเดียวกัน ×1,000 ≈0.00143104 USD ไม่ใช้จำนวน request เพราะหนึ่ง batch อาจมีหลาย predictions และยังต้องระบุว่า provisional

**English answer:** Planned cost was 8.89 THB per 1,000 at 10,000 assumed predictions. For reported cost, we divided 0.0012035014 USD by 841 observed valid profiles in the same window, then multiplied by 1,000. This provisional figure is about 0.00143104 USD per 1,000.

**เปิดหลักฐาน:** Slide 12; `reports/cost-per-1000.json`; `docs/COST_REPORT.md`

### Q41. Why is the reported bill so small? Did you prove the 150 THB budget?

**คำตอบไทย:** ยังพิสูจน์ไม่ได้ เพราะ billing/telemetry อาจ lag และยอดอาจเป็นแค่บางส่วนของ usage การคิด grants/credits และสกุลเงินต้องดูข้อมูล provider ให้ครบด้วย เราไม่เรียกยอดนี้ final invoice หรือ before-credit full spend และต้อง reconcile เมื่อข้อมูลครบ

**English answer:** We have not proved the full 150 THB budget. Billing and telemetry may lag, and the reported amount may cover only part of the usage. Grants, credits, and currency also need review. We keep this provisional figure separate from the before-credit plan.

**เปิดหลักฐาน:** `cost-per-1000.json` → actual_limits; `docs/COST_REPORT.md`

### Q42. What are your main limitations, and what would another week improve?

**คำตอบไทย:** Cloud p95 ยังเกินเป้า บิลยังไม่ครบ labels ชั่วคราว ความหมายศูนย์ไม่ชัด drift ยัง offline และไม่มี user-quality study ต่อไปจะแยก latency scope/reconcile cost ทำ live windows และ review segment meaning ไม่อ้างว่าเพิ่มเวลาอีกอาทิตย์แล้วแก้ได้แน่นอนทุกข้อ

**English answer:** Our main limits are cloud latency, incomplete billing, provisional labels, unknown zero meaning, and offline drift testing. Next we would isolate latency, reconcile cost, add live feature windows, and review segment meaning with users.

**เปิดหลักฐาน:** Slide 13; model card; `reports/finish-delivery.json`

### Q43. Is the project similar to Lab 5? Do you need an LLM or a second cloud provider?

**คำตอบไทย:** คล้ายในส่วน pipeline, identity, cloud deployment, cost และ cleanup และใช้แนวคิดจาก Labs 1–4 ด้วย แต่ Capstone brief ไม่บังคับให้เพิ่ม LLM หรือ second provider เพียงเพราะ Lab 5 มี เราแยก provider code และตรวจ portability แต่ยังไม่อ้างว่ารันบน provider อื่นแล้ว

**English answer:** It overlaps with Lab 5 in cloud pipelines, identity, cost, and cleanup, and with earlier labs in testing and monitoring. The capstone brief does not require an LLM or a second provider. We separate provider code, but have not demonstrated another cloud deployment.

**เปิดหลักฐาน:** Course project brief; Lab 5; `scripts/portability_audit.py`; `cloudlayer/`

### Q44. Is the project fully finished, and what happens after the presentation?

**คำตอบไทย:** มี saved evidence ครบรายการหลักของ Capstone และ final source CI ผ่านทั้งทาง normal/deliberate failure แต่ยังต้องทำ live defense จริง อธิบาย targets ที่ไม่ผ่านและ cost provisional จากนั้นเก็บหลักฐานแล้ว cleanup ให้ตรวจผ่าน และอัปเดตต้นทุนเมื่อ billing ครบ Checklist ไม่รับประกันคะแนนเต็ม

**English answer:** The required system evidence is recorded, including final-source CI. We still need the live presentation, honest discussion of limits, verified cleanup, and cost reconciliation when billing settles. Completing the checklist does not guarantee full marks.

**เปิดหลักฐาน:** `reports/finish-delivery.json`; `docs/SUBMISSION_CHECKLIST.md`, `FINAL_STEPS.md`; course brief

### Q45. What would you do if the live demo failed during the presentation?

**คำตอบไทย:** ดูว่า network/timeout, readiness/model load หรือ invalid input ถ้าจงใจส่ง invalid แล้วได้ 422 ถือว่าถูกต้อง ถ้า canary/golden mismatch ห้ามฝืนบอกว่าผ่าน เก็บ response แล้วเปิด saved evidence โดยบอกตรง ๆ ว่าไม่ใช่ live result สำเร็จในรอบนี้

**English answer:** I would check whether the issue is connectivity, readiness, or invalid input. An expected 422 is correct behaviour. For a real failure, I would show the response and saved evidence, clearly stating that the live check did not succeed in that run.

**เปิดหลักฐาน:** คู่มือ `PROJECT_SUMMARY_TH.md` → 7.8; `output/presentation/evidence/api-demo.json`

### Q46. What did each team member actually do, and did you use AI tools?

**คำตอบไทย:** ข้อนี้แต่ละคนต้องตอบจากงานที่ทำจริง ไม่ใช้ roles ใน proposal เป็นหลักฐานว่าได้ทำทุกอย่างตามนั้น เราใช้ Codex ช่วยเตรียม/ตรวจโค้ดและเอกสาร ส่วนผู้ใช้รัน notebooks และตรวจระบบร่วมกัน ควรบอกการใช้เครื่องมือตามกติกาวิชา และอธิบาย code/results เองได้ ถ้าไม่รู้ implementation จุดใดให้บอกว่าต้องเปิดตรวจ ไม่แต่งความรับผิดชอบหรืออ้างว่าเขียนเองทั้งหมด

**English answer:** We used Codex to help prepare and review code and documents, and we ran the notebooks and checked the results. Each member should explain their actual work. We should disclose tool use according to course rules and be able to explain the system ourselves.

**เปิดหลักฐาน:** ประวัติงานและสิ่งที่แต่ละคนทำจริง; `README.md` ระบุสมาชิกแต่ไม่ได้พิสูจน์ contribution รายบุคคล

## F. ประโยคสั้นสำหรับกรณีไม่แน่ใจ

อย่าใช้เป็นข้ออ้างเพื่อเลี่ยงคำถามที่ตอบจาก report ได้ แต่ถ้าไม่มีหลักฐาน ควรพูดให้ตรง:

| English | ไทย |
|---|---|
| We measured this in a controlled test, not in live production. | เราวัดใน controlled test ยังไม่ใช่ production จริง |
| That is our target, not an achieved result. | นั่นเป็นเป้าหมาย ยังไม่ใช่ผลที่ทำได้ |
| The report supports this result, but not that stronger claim. | รายงานรองรับผลนี้ แต่ยังไม่รองรับข้อสรุปที่แรงกว่านั้น |
| I would need to check the report before giving an exact number. | ขอเปิดรายงานก่อนให้ตัวเลขที่แน่นอน |
| We have not implemented or tested that part yet. | ส่วนนั้นยังไม่ได้ทำหรือทดสอบ |
| This is saved evidence; the current live state needs a new check. | นี่เป็นหลักฐานที่บันทึกไว้ สถานะสดต้องตรวจใหม่ |

## G. หลักฐานที่ควรเปิดไว้

| ถ้าถูกถามเรื่อง | เปิดไฟล์ / หน้า |
|---|---|
| Data/split/leakage | Slide 4; data-audit.json, prepared-data.json |
| Model choice/uncertainty | selection.json, bundle-manifest.json, model card |
| Actual Azure training | azure-training-proof.json, finish-training-registry.json |
| API/invalid input | Notebook demo; api-demo.json; service/app.py |
| CI gate | Slide 7; Actions สองรอบ; ci-runs.json |
| Dashboard/actual alert | dashboard-workbook.json, finish-alert.json |
| Fault/recovery | Slide 10; finish-failure.json; tests/test_api.py |
| Drift scope | Slide 11; input-drift.json |
| Latency/cold | Slide 8; azure-load.json, pooled-load.json, finish-cold.json |
| Cost | Slide 12; cost-per-1000.json, docs/COST_REPORT.md |
| Cleanup/remaining work | finish-delivery.json, docs/FINAL_STEPS.md |

ไฟล์ JSON ในตารางอยู่ใต้ `reports/` ยกเว้น `api-demo.json` อยู่ใต้ `output/presentation/evidence/` ส่วนคำสั่ง live demo อยู่ใน `PROJECT_SUMMARY_TH.md` ไม่จำเป็นต้อง rerun training หรือ failure เพื่อเปิดหลักฐานเหล่านี้

**Actions links ที่ตรวจไว้:**

- [Normal tests and deployment](https://github.com/DewPerawis/MLOP-PJ/actions/runs/38173375457)
- [Intentional failure with skipped deployment](https://github.com/DewPerawis/MLOP-PJ/actions/runs/38173380800)

## H. Sources

คำตอบเรื่องระบบอิง source code, reports, model card, workflow และ course brief ที่ระบุใต้แต่ละข้อ ไม่ใช่การยืนยันสถานะ cloud ใหม่ขณะอ่านไฟล์นี้

[1] S. Renjith, “Travel Review Ratings,” UCI Machine Learning Repository, 2018, DOI: 10.24432/C5C31Q. [หน้า UCI](https://archive.ics.uci.edu/dataset/485/travel%2Breview%2Bratings)

[2] scikit-learn, “silhouette_score,” official documentation. [Metric definition](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html) คำอธิบายทั่วไปไม่เปลี่ยน package versions ที่ใช้ทำโปรเจกต์

Course sources: `docs/reference/course/project/project-brief.md` และ `docs/reference/course/labs/lab-05-cloud-mlops-and-cost.md` โดยแยก Capstone requirements กับรายละเอียดแต่ละ Lab ไว้ชัดเจน
