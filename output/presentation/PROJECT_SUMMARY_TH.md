# คู่มือทำความเข้าใจโปรเจกต์และสไลด์ — ภาษาไทย

ไฟล์นี้ใช้สำหรับอ่านเตรียมตัว ไม่ใช่ข้อความที่ต้องอ่านทั้งหมดบนเวที สไลด์จริงยังเป็นภาษาอังกฤษ 15 หน้า ใช้เวลาพูด 8 นาที และตอบคำถามอีก 5 นาที คำอธิบายด้านล่างอิงโค้ดและผลที่บันทึกไว้ในโปรเจกต์ ไม่ได้รัน cloud หรือวัดประสิทธิภาพใหม่เพื่อเขียนคู่มือนี้

อ่านตามลำดับ: **ภาพรวม → สิ่งที่ทำในแต่ละส่วน → อธิบายสไลด์ → ขั้นตอน live demo** แล้วใช้ `PRESENTATION_QA_EN_TH.md` ซ้อมตอบคำถาม

## 1. โปรเจกต์เราทำอะไรในหนึ่งประโยค

เราทำบริการที่รับคะแนนความชอบด้านการท่องเที่ยว 24 หมวด แล้วใช้โมเดลจัดผู้ใช้เข้ากลุ่ม พร้อมสร้างระบบรอบโมเดลให้ฝึกซ้ำ ตรวจสอบเวอร์ชัน deploy บน Azure ตรวจข้อผิดพลาด และติดตามค่าใช้จ่ายได้

ชื่อโปรเจกต์คือ **Travel Style Segmentation & Drift Monitoring** คำว่า segmentation หมายถึงการแบ่งกลุ่มจากรูปแบบข้อมูล ส่วน drift หมายถึงการตรวจว่าการกระจายของข้อมูลเปลี่ยนไปจากข้อมูลอ้างอิงหรือไม่

สมมติผู้ใช้คนหนึ่งให้คะแนนแต่ละหมวด เช่น พิพิธภัณฑ์ ร้านอาหาร และชายหาด เรามองคะแนนทั้ง 24 หมวดรวมกันเป็นหนึ่ง **profile** โมเดลจะดูว่ารูปแบบคะแนนนี้ใกล้กับกลุ่มไหน แล้วตอบกลับเป็น `Segment 1` ถึง `Segment 5` ชื่อเหล่านี้ยังเป็นชื่อชั่วคราว เราไม่ได้สรุปว่า Segment 1 คือสายกิน หรือ Segment 2 คือสายธรรมชาติ เพราะยังไม่ได้ให้ผู้เชี่ยวชาญตรวจความหมายของแต่ละกลุ่ม

บริการนี้อาจเป็นส่วนหนึ่งของระบบท่องเที่ยวในอนาคต แต่สิ่งที่ทำจริงตอนนี้คือ **บริการจัดกลุ่ม** ยังไม่ได้สร้างหน้าเว็บผู้ใช้ ระบบแนะนำสถานที่เฉพาะแห่ง หรือทดสอบความพึงพอใจของผู้ใช้

วิชานี้เน้น **MLOps** คือการทำให้โมเดลกลายเป็นระบบที่ใช้งานและตรวจสอบได้ อาจารย์จึงให้ความสำคัญกับ pipeline, deployment, CI/CD, monitoring, failure handling และ cost มากกว่าการแข่งคะแนนโมเดล

## 2. ข้อมูลเข้าระบบ แล้วอะไรออกมา

ข้อมูลมาจาก **UCI Travel Review Ratings** ซึ่งรวบรวมค่าเฉลี่ยคะแนนรีวิวจาก Google ใน 24 หมวดสถานที่ท่องเที่ยวในยุโรป มี 5,456 แถว และใช้สัญญาอนุญาต CC BY 4.0 จึงใช้และดัดแปลงได้โดยให้เครดิตแหล่งข้อมูล [1]

ชื่อคอลัมน์ที่โค้ดใช้คือ `Category 1` ถึง `Category 24` ตัวอย่างความหมายตามลำดับของ UCI คือ Category 1 = churches, Category 2 = resorts, Category 6 = museums และ Category 9 = restaurants ไม่ควรเปลี่ยนชื่อคอลัมน์ใน request เอง เพราะ API ตรวจชื่อทั้ง 24 ช่อง

หน้า UCI อธิบายคะแนนรีวิวว่าอยู่ในช่วง 1–5 แต่ไฟล์จริงมีศูนย์ด้วย เราจึงไม่เดาว่าศูนย์แปลว่าไม่ชอบหรือไม่ได้รีวิว และกำหนดให้ API รับตัวเลขในช่วง **0–5** ตามข้อมูลที่ตรวจพบ [1]

| สิ่งที่ส่งเข้า | สิ่งที่ตอบกลับ | ความหมาย |
|---|---|---|
| หนึ่ง profile ที่มีคะแนนครบ 24 หมวด | `cluster_id` | หมายเลขกลุ่มภายในโมเดล เริ่มที่ 0 |
| profile เดียวกัน | `segment` | ชื่อกลุ่ม เช่น Segment 1 หรือ `null` เมื่อไม่แน่ใจ |
| profile เดียวกัน | `distance` | ระยะจาก profile ถึงจุดศูนย์กลางกลุ่ม หลัง preprocessing |
| profile เดียวกัน | `uncertain` | ไกลจากกลุ่มมากกว่าค่า threshold ที่กำหนดหรือไม่ |
| profile เดียวกัน | `model_version` | ใช้โมเดลเวอร์ชันใดตอบ request นี้ |

ตัวอย่างที่ตรวจจริงจาก API: `cluster_id = 0`, `segment = Segment 1`, `distance ≈ 4.1435`, `uncertain = false`, `model_version = abfd88e893ca`

อย่าอ่าน distance 4.1435 ว่าเป็นคะแนนความมั่นใจ 4.1435 หรือความถูกต้องกี่เปอร์เซ็นต์ มันเป็นระยะทางในพื้นที่ข้อมูลที่ผ่านการปรับสเกลแล้ว ต้องเทียบกับ threshold ของกลุ่มนั้น

## 3. ห้าส่วนใหญ่ที่เราทำ

| ส่วน | สิ่งที่ทำจริง | ทำไปเพื่ออะไร |
|---|---|---|
| ข้อมูล / training / registry | ตรวจ CSV, แบ่งข้อมูล, เลือก K-Means, บันทึก bundle, tracking และฝึกบน Azure ML | ให้รู้ว่าโมเดลมาจากข้อมูลและ settings ชุดไหน |
| Live API | ทำ FastAPI, Docker และ deploy บน Azure Container Apps | ให้เครื่องอื่นส่ง request มาขอผลได้จริง |
| CI/CD | GitHub Actions ทดสอบก่อน build และ deploy | ป้องกันโค้ดที่ทดสอบไม่ผ่านถูกส่งขึ้นระบบ |
| Monitoring / failure / recovery | Dashboard, semantic canary, alert และทดลอง mapping ผิดใน staging | ตรวจจับระบบที่ยังตอบได้แต่ตอบผิด และพิสูจน์การกู้คืน |
| Delivery evidence | Load/cold reports, drift test, cost report, model card และ presentation | ให้ตรวจงานและอธิบายผลกับข้อจำกัดได้ |

### 3.1 ตรวจและเตรียมข้อมูล: ไม่ใช่ดาวน์โหลดแล้ว train ทันที

เราตรวจว่าไฟล์ที่ดาวน์โหลดเป็นเวอร์ชันที่ต้องการด้วย **SHA-256** ซึ่งเหมือนลายนิ้วมือของไฟล์ หากข้อมูลเปลี่ยน ลายนิ้วมือจะเปลี่ยน และ pipeline จะหยุดให้ตรวจ

ผล audit พบ 5,456 แถว ใช้ได้ 5,454 แถว อีก 2 แถวมีค่าเกินมาในช่องที่ไม่ควรมี เราแยกแถวเหล่านี้ไว้ใน **quarantine** แทนการเดาว่าควรซ่อมข้อมูลอย่างไร และไม่เอา user ID เข้าโมเดล เพราะ ID ไม่ใช่คะแนนความชอบ

จากนั้นแบ่งเป็น train 3,817 แถว, validation 817 แถว และ test 820 แถว ใกล้เคียงสัดส่วน 70/15/15 โดยใช้ profile ที่เหมือนกันทุกช่องเป็นกลุ่มเดียวกันในการแบ่ง ข้อมูลซ้ำจึงไม่หลุดไปอยู่ทั้ง train และ test แล้วทำให้การประเมินดูง่ายเกินจริง

หน้าที่ของแต่ละชุดคือ:

- **Train:** ให้โมเดลเรียนรู้ และให้ preprocessing เรียนค่า median/ค่าเฉลี่ย/ส่วนเบี่ยงเบนมาตรฐาน
- **Validation:** เปรียบเทียบ settings แล้วเลือกแบบที่เหมาะสม
- **Test:** ประเมินแบบที่เลือกแล้ว ไม่ใช้เลือก k

**Git** เก็บโค้ดและไฟล์ข้อความ ส่วน **DVC** เก็บตัวชี้เวอร์ชันข้อมูล โดยไฟล์ข้อมูลจริงอยู่ใน Azure Blob เราทดลองดึงข้อมูลในที่เก็บใหม่ที่ไม่มี cache เดิม แล้วตรวจ hash ตรงกัน จึงมีหลักฐานว่าไม่ได้อ่านได้เพราะมีไฟล์ค้างอยู่ในเครื่องเดียว

หลักฐาน: `reports/data-source.json`, `data-audit.json`, `prepared-data.json`, `finish-assets.json`; โค้ด `src/data.py`; pipeline `dvc.yaml`

### 3.2 เลือกโมเดลและป้องกันข้อมูลรั่ว

เราใช้ **K-Means** จัด profile ให้อยู่ใกล้จุดศูนย์กลางกลุ่มเดียวกัน ไม่มี label ว่าคนนี้เป็นนักท่องเที่ยวประเภทใด จึงเป็น unsupervised clustering ไม่ใช่การทำนาย class ที่มีเฉลยอยู่แล้ว

ก่อนเข้า K-Means มีขั้นตอน median imputation และ StandardScaler สำหรับข้อมูลที่มี missing value ตัว imputer เตรียมใช้ median ส่วน scaler ปรับแต่ละหมวดให้เปรียบเทียบกันในสเกลที่เหมาะสม ข้อมูล accepted ที่ตรวจแล้วไม่มีค่าหายไป แต่เก็บ imputer เป็นส่วนหนึ่งของ pipeline ไว้ ส่วน API ปัจจุบันยังต้องรับครบ 24 ช่อง ไม่ได้รับ missing field แล้วเติมให้เอง

เรา fit preprocessing จาก train เท่านั้น แล้วนำค่าเดิมมาใช้กับ validation, test และ request ใหม่ ถ้า fit scaler จากข้อมูลทุกชุดก่อนแบ่ง จะเอาข้อมูล test มาใช้ระหว่างเตรียมโมเดล ซึ่งเป็น leakage

การศึกษาเปรียบเทียบ:

- k = 3, 4, 5, 6, 7, 8
- random seed = 42, 43, 44
- เก็บศูนย์ตามเดิม เทียบกับมองศูนย์เป็น missing value
- รวม 36 การ fit K-Means และมี GMM เป็นโมเดลเปรียบเทียบเพิ่มเติม

เลือกจาก validation โดยต้องมี seed stability ARI อย่างน้อย 0.8 และแต่ละกลุ่มมีอย่างน้อย 2% ของ validation ก่อนจัดอันดับด้วย mean silhouette ผลที่เลือกคือ **keep_zero, K-Means k=5** และใช้ seed 42, `n_init=10` สำหรับ bundle

Silhouette ใช้ดูว่ากลุ่มแยกกันมากน้อยแค่ไหน โดยเทียบความใกล้ภายในกลุ่มกับกลุ่มอื่น ค่าสูงกว่าเหมาะกว่าในความหมายของ metric นี้ ค่าใกล้ศูนย์หมายถึงกลุ่มคาบเกี่ยวกันมาก [2] ผล validation ของ K-Means ≈ 0.1448 เทียบกับ GMM ≈ 0.0957 และ test ของ K-Means ≈ 0.1445 จึงพูดได้ว่า K-Means ดีกว่า GMM ที่ลองตาม metric นี้ แต่ **ไม่ใช่ accuracy 14.45% และไม่ใช่หลักฐานว่ากลุ่มมีความหมายเชิงธุรกิจชัดเจน**

ARI = 1.0 ในการเปรียบเทียบ seeds หมายถึงผลจัดกลุ่มบน validation ตรงกันในรอบที่ลอง เมื่อคำนึงว่าหมายเลขกลุ่มอาจสลับกันได้ ไม่ได้แปลว่าถูกต้องเทียบกับคนจริง 100%

หลักฐาน: `configs/study.json`, `reports/selection.json`, `study-summary.csv`, `bundle-manifest.json`; โค้ด `src/train.py`

### 3.3 Bundle, registry และ lineage: สามอย่างนี้ต่างกัน

**Bundle** คือไฟล์ที่บรรจุสิ่งที่ต้องใช้ร่วมกัน ไม่ได้มีเฉพาะ K-Means แต่มี preprocessing, ลำดับ features, mapping ของกลุ่ม, thresholds และ version ด้วย ถ้าเซฟโมเดลโดยไม่เซฟ scaler หรือสลับลำดับคอลัมน์ ผล prediction อาจผิดทั้งที่โปรแกรมยังรันได้

**Registry** คือรายการโมเดลที่ลงทะเบียนไว้ ส่วน **lineage** คือข้อมูลที่บอกย้อนกลับได้ว่าโมเดลนั้นมาจาก raw data, code, settings และ training job ใด เรามี local MLflow สำหรับติดตามการทดลอง และมี Azure ML training job ที่ Completed พร้อมลงทะเบียน `travel-style` เวอร์ชัน `1`

Azure job ไม่ได้แค่อัปโหลดไฟล์เดิม มัน fit โมเดลใหม่ตาม settings ที่เลือก แล้วตรวจความเทียบเท่ากับโมเดลที่ทดสอบไว้ หลังผ่านจึง export **canonical bundle** เดิม เพื่อรักษา bytes และ hash ของไฟล์ที่ผ่าน tests แล้ว ไฟล์ serialize ของโมเดลที่ fit ใหม่อาจมี hash ต่างกัน จึงแยกคำว่า fresh-fit equivalent ออกจาก byte-identical ให้ชัด

ตัวเลข version ในงานมีหลายชนิด:

| ชื่อ | ค่า / ตัวอย่าง | ใช้อ้างถึงอะไร |
|---|---|---|
| Registry version | `travel-style:1` | ลำดับรุ่นใน Azure ML registry |
| Model version | `abfd88e893ca` | รหัสที่บริการใส่ไว้ใน prediction |
| Bundle SHA-256 | เริ่ม `71f3ba41b4b964f5…` | ไฟล์ bundle ที่ผ่านการตรวจ |
| Git commit | `9fea51a` | โค้ดที่ CI สองรอบทดสอบ |
| Image digest | `sha256:…` ใน ci-deploy-result | Docker image ที่ deploy จริง |

อย่าเอา registry version 1 ไปบอกว่าต้องเท่ากับ Git commit หรือ model version มันระบุคนละสิ่ง และ image ใหม่สามารถใช้ model version เดิมได้เมื่อเปลี่ยนโค้ดรอบโมเดล

ก่อน API พร้อมใช้งาน เราตรวจ bundle hash, Python/package versions, schema, mapping และ **golden predictions** คือ input ตัวอย่าง 5 profile ที่บันทึกผลที่คาดหวังไว้ กลุ่มละหนึ่ง profile สิ่งนี้จับ regression ได้ แต่ไม่ได้แทนการประเมินความถูกต้องกับผู้ใช้ใหม่ทั้งหมด

หลักฐาน: `reports/bundle-manifest.json`, `golden-profiles.json`, `azure-training-proof.json`, `finish-training-registry.json`; โค้ด `src/bundle.py`, `service/runtime.py`, `scripts/train_selected.py`

### 3.4 API และ Docker: เปลี่ยนไฟล์โมเดลให้เรียกใช้งานได้

**API** คือช่องทางที่โปรแกรมอื่นเรียกบริการเรา ส่วน **endpoint** คือเส้นทางสำหรับงานแต่ละแบบ เช่น `/predict` การรันใน Notebook เป็นการเรียกโมเดลจากเครื่องเรา แต่การเรียก Azure URL คือส่ง HTTPS request ไปหาแอปบน cloud จริง

| Endpoint | หน้าที่ | คำตอบที่สำคัญ |
|---|---|---|
| `GET /health` | เช็คว่าโปรแกรมตอบได้ | 200 เมื่อ process ยังตอบได้ |
| `GET /ready` | เช็คว่าโหลดและตรวจ bundle ผ่านจนพร้อมใช้งาน | 200 พร้อม model version หรือ 503 หากไม่พร้อม |
| `POST /predict` | รับ profile แล้วจัดกลุ่ม | 200 สำหรับข้อมูลถูกต้อง; 422 สำหรับข้อมูลผิดรูปแบบ |
| `GET /canary` | ใช้ golden profiles ตรวจความหมายของผล | 200 หากตรง หรือ 503 เมื่อ semantic check ไม่ผ่าน |

Request ต้องเป็นตัวเลขจริง ไม่ใช่ string หรือ boolean มีชื่อครบ 24 ช่อง ค่า finite อยู่ในช่วง 0–5 และหนึ่ง batch มี 1–100 profiles ข้อมูลขาดช่อง เกินช่วง หรือมี profile 101 รายการจะถูกปฏิเสธด้วย 422

**Invalid** ต่างจาก **uncertain**: invalid คือข้อมูลไม่ผ่านกติกา จึงตอบ 422; uncertain คือข้อมูลถูกต้อง แต่ไกลจาก centroid ของกลุ่มมากเกิน threshold จึงตอบ 200 โดย `uncertain=true` และ `segment=null` เราไม่บังคับให้ชื่อกลุ่มที่ดูมั่นใจเกินข้อมูล

Threshold ใช้ระยะของ train ภายในแต่ละกลุ่มที่ percentile 95 ไม่ใช่ probability หรือ confidence ที่ calibrated แล้ว และไม่ได้รับประกันว่าผู้ใช้ใหม่จะ uncertain แค่ 5%

**Docker image** บรรจุโค้ด dependencies และ bundle สำหรับรันบริการ เก็บ image ใน **Azure Container Registry (ACR)** แล้วให้ **Azure Container Apps** รัน ใช้ image digest เพื่อระบุรุ่นแบบชัดเจน แทนการอ้าง tag ที่เปลี่ยนเนื้อหาได้

การคุมต้นทุนตั้ง app ให้ minReplicas=0 และ maxReplicas=1 คือว่างแล้วลดเหลือศูนย์ instance ได้ แต่มี cold start เมื่อเรียกครั้งใหม่ และไม่ใช่ระบบที่พิสูจน์ว่ารับงานปริมาณมากได้แล้ว

หลักฐาน: `reports/ci-deploy-result.json`, `output/presentation/evidence/api-demo.json`; โค้ด `service/app.py`, `src/bundle.py`, `Dockerfile`

### 3.5 CI/CD: ทำไมเราแสดง Actions สีแดงด้วย

**CI** คือการทดสอบอัตโนมัติเมื่อเปลี่ยนโค้ด ส่วน **CD** ในงานนี้คือ build/push image และ deploy อัตโนมัติเมื่อผ่าน tests บน main ตามเงื่อนไข workflow

ลำดับจริง: ตรวจ portability และ tests ที่ไม่ต้องใช้ cloud model → job deploy ที่ต้องรอ tests ผ่าน → login Azure → ดาวน์โหลด bundle และตรวจ hash → API/runtime tests ด้วย bundle จริง → build/push image → deploy → real HTTP smoke check

เราแสดงสอง Actions runs ที่ทดสอบ source commit เดียวกัน `9fea51a`:

- รอบปกติ: tests success และ deploy success
- รอบ `demo_failure=true`: ตั้งใจให้ test หนึ่งล้มเหลว แล้ว deploy ต้อง skipped

สีแดงของรอบที่สองจึงเป็นผลที่เราตั้งใจให้เกิด เพื่อพิสูจน์ว่า gate ทำงาน ไม่ใช่อ้างว่า workflow ทุกอันผ่าน และไม่ใช่การทำให้ production API ล่ม

การ login ใช้ GitHub OIDC แลก token สำหรับ Azure และสิทธิ์ที่จำกัด ไม่ฝัง password ใน workflow แต่ API สำหรับ coursework ยังเป็น public endpoint ไม่มีระบบยืนยันตัวตนผู้ใช้หรือ rate limit ที่เราพิสูจน์ไว้ จึงไม่ควรเรียกว่าพร้อมเป็น production เต็มรูปแบบ

หลักฐาน: `.github/workflows/ci.yml`, `reports/ci-runs.json`, `finish-ci-evidence.json`; tests `tests/test_contract_ci.py`, `tests/test_api.py`

### 3.6 Monitoring, deliberate failure และ recovery

เราบันทึก request ID, path, status, duration, model version และจำนวน profiles/uncertain โดยไม่บันทึกคะแนนครบ 24 ช่องของผู้ใช้ลง request log แล้วใช้ Log Analytics ทำ Workbook ชื่อ **MLOP Travel Style** ซึ่งดู requests/errors, latency, profile counts และ semantic failures ได้

สิ่งที่จงใจทำผิดคือสลับ mapping ของ cluster 0 กับ 1 ใน **แอป staging แยกต่างหาก** ชื่อ `failure-492ea24d` จุดศูนย์กลางโมเดลไม่ได้ถูกเปลี่ยน แต่ชื่อ segment ที่ตอบอาจผิด เช่น cluster 0 ถูกผูกกับ Segment 2 แทน Segment 1

นี่เป็นตัวอย่างว่า HTTP 200 และ `/ready` อย่างเดียวไม่รับประกันว่าความหมายของผลถูกต้อง เราใช้ `/canary` ส่ง golden profiles แล้วเทียบ cluster, segment, distance และ uncertainty เมื่อ mapping ผิด canary ตอบ 503 และเขียน event `semantic_canary_failed`

Azure alert ตรวจ event นี้และมีหลักฐานว่า fired จริง แล้วภายหลัง resolved แต่ **ยังไม่ได้ตั้ง email notification** การมี alert event จึงไม่เท่ากับมี email ส่งถึงทีม และ semantic canary ในงานนี้ไม่ได้พิสูจน์ว่ามีระบบเรียกตรวจตลอดเวลาโดยอัตโนมัติ

เรากู้คืนด้วยการคืน configuration แล้ว stop/start staging และตรวจ canary ผ่านสองครั้ง ความพยายามกู้คืนรอบแรกไม่สำเร็จ จึงนับเวลาตั้งแต่ตรวจพบจนยืนยันการกู้คืนได้จริงรวมประมาณ **7 นาที 16.4 วินาที** ห้ามตัดเวลาลองผิดครั้งแรกออกแล้วบอกว่ากู้คืนเร็วมาก

บทเรียนคือให้ health/readiness ตรวจความพร้อม และมี semantic check ตรวจผลที่ระบบตอบด้วย เราเพิ่ม regression test สำหรับ mapping failure กลับเข้า tests แล้ว

หลักฐาน: `reports/finish-monitor.json`, `dashboard-workbook.json`, `finish-alert.json`, `finish-failure.json`; โค้ด `cloudlayer/finish_monitor.py`, `service/app.py`, `tests/test_api.py`

### 3.7 Drift ในชื่อโปรเจกต์ทำถึงไหนแล้ว

เราทำ **offline controlled input-drift test** โดยเทียบการกระจายคะแนนแต่ละ feature ด้วย two-sample KS statistic แล้วใช้ค่ามากที่สุดใน 24 features เป็น score

ใช้ reference 1,908 แถวจาก train, recent sample 200 แถว และ calibration 100 รอบจากข้อมูล train เพื่อได้ threshold ≈ 0.1257 ข้อมูลปกติได้ score ≈ 0.0994 จึงไม่ flagged ส่วนข้อมูลที่ตั้งใจเปลี่ยนโดยบวก 1.5 ในสี่ features แรก แล้วจำกัดให้อยู่ 0–5 ได้ score ≈ 0.7879 จึงตรวจพบ

การ calibration ช่วยตั้งจุดเตือนจากพฤติกรรมข้อมูลอ้างอิง แต่ไม่ได้รับประกัน false alarm 5% สำหรับการใช้งานในอนาคตทุกแบบ โดยเฉพาะเมื่อกระจายข้อมูลจริงเปลี่ยน

อย่าสับสน **semantic alert ที่เกิดจาก mapping ผิดบน Azure** กับ **drift flag จากข้อมูลที่ดัดแปลง offline** มันเป็นคนละการทดสอบ ข้อมูลชุดนี้ไม่มีเวลาหรือ outcome labels ที่ใช้พิสูจน์ temporal/concept drift และเรายังไม่ได้ต่อ rolling-window feature monitor บนข้อมูลผู้ใช้จริง

หลักฐาน: `monitoring/drift.py`, `reports/input-drift.json`

## 4. ผลที่ต้องจำ และอ่านอย่างไรให้ถูก

| ผลที่บันทึก | ตัวเลข | ขอบเขต / ข้อจำกัด |
|---|---|---|
| K-Means validation silhouette | 0.1448 | ค่าเฉลี่ยใน study; ไม่ใช่ accuracy |
| K-Means test silhouette | 0.1445 | Test ที่ไม่ได้ใช้เลือก settings |
| GMM validation silhouette | 0.0957 | โมเดลเปรียบเทียบที่ลอง; ไม่ใช่ทุก GMM setting |
| Local warm p95 | 274.54 ms | Real HTTP ที่ local; ผ่านเป้า 300 ms ในการวัดนี้ |
| Azure warm p95 เดิม | 813.77 ms | WSL → Azure HTTPS รวม network; ยังไม่ผ่านเป้า |
| Azure pooled-client p95 | 624.83 ms | Client reuse connection และ warm-up ต่างจากเดิม; ยังไม่ผ่าน |
| Cold readiness request | 3.82 วินาที | หนึ่ง sample หลังยืนยัน zero replicas; ไม่ใช่ p95 |
| Warm load tests | 200 requests, concurrency 10, batch 1, errors 0 | ไม่ได้เท่ากับทดสอบทุก workload หรือรับประกันไม่มี error ในอนาคต |
| Detection → confirmed recovery | 7 นาที 16.4 วินาที | รวม recovery ครั้งแรกที่ไม่สำเร็จ |
| Planned total cost | 88.89 THB | สมมติฐานและ reserve; ก่อน credits |
| Planned cost / 1,000 predictions | 8.89 THB | สมมติรวม 10,000 predictions |
| Reported cost / 1,000 predictions | 0.00143104 USD | ยอดชั่วคราวจาก provider และ observed valid profiles ในช่วงเดียวกัน |

**p95** หมายถึงประมาณ 95% ของตัวอย่างในชุดทดสอบมี latency ไม่เกินค่านี้ ไม่ใช่ค่าเฉลี่ย และไม่ได้แปลว่าทุก request ตอบภายในเวลานี้ Client latency รวม network และการรับ/อ่านคำตอบ ส่วน latency ใน server log วัดอยู่ภายในแอป จึงไม่ควรเอาสองค่านี้มาเทียบตรง ๆ

ผล pooled-client ต่ำกว่าเดิม แต่เราเปลี่ยน client และ warm-up method จึงยังสรุปเชิงเหตุผลไม่ได้ว่า server เร็วขึ้นเท่าใด การวัดนี้ชี้ว่าฝั่ง client มีผลกับเวลาที่เห็น และควรแยก network/app timing หากจะปรับต่อ

ต้นทุนชั่วคราวคำนวณจาก **0.0012035014 USD ÷ 841 valid profiles × 1,000 = 0.00143104 USD** หนึ่ง request อาจมี 100 profiles จึงนับ predictions จาก profiles ที่ประมวลผลสำเร็จ ไม่ใช้จำนวน HTTP requests แทน ค่าใช้จ่ายรวมระดับ resource group ซึ่งรวมองค์ประกอบของโปรเจกต์ ไม่ใช่เฉพาะ serving app

ยอด reported นี้ต่ำมากและอาจมี billing/telemetry lag จึงไม่ใช่ final invoice ไม่พิสูจน์ว่า full demo อยู่ในงบ 150 THB และไม่ควรแปลง USD ด้วยอัตราสมมติในแผนแล้วเรียกว่าบิลเงินบาทจริง

## 5. Notebook ที่เราเคยรันทำอะไรไปบ้าง

ตารางนี้ช่วยเชื่อมว่าตอนกดรันแต่ละไฟล์ กำลังทำส่วนใดของงาน เป็นคำอธิบายย้อนหลัง **ไม่ใช่คำสั่งให้รันทุกไฟล์ใหม่** รายงานล่าสุดเป็นแหล่งสถานะหลัก ข้อความเก่าในบาง Notebook/README อาจยังอธิบายช่วงที่ระบบไม่เสร็จ

| Notebook | สิ่งที่ทำ |
|---|---|
| 00 | ตรวจ Python kernel และ packages ว่าใช้ environment ของโปรเจกต์ |
| 01 | ดาวน์โหลดและ audit ข้อมูล เก็บ hash ตรวจแถวผิด ศูนย์ และข้อมูลซ้ำ |
| 02 | แยก quarantine และแบ่ง train/validation/test แบบกัน duplicate ข้ามชุด |
| 03 | เปรียบเทียบ zero policies, k, seeds และ GMM บน validation |
| 04 | สร้าง bundle ตรวจโหลดกลับ ประเมิน test และเก็บ golden profiles |
| 05 | Tracking ด้วย local MLflow และ versioning/registry ภายในเครื่อง |
| 06 | ทดสอบ API ภายใน process ยังไม่ใช่การเรียก Azure URL |
| 07 | ตรวจ Docker/Azure tools และ login ก่อนสร้าง cloud |
| 08 | Build Docker ทดสอบ real local HTTP และ load |
| 09 | ตรวจการวัด HTTP หลังแก้ repeated client setup |
| 10 | ตรวจ serving code ที่ปรับแล้วและผล local p95 |
| 11–15 | ตรวจ providers, tools, region, quota, permissions, ราคา และ preview infrastructure |
| 16 | สร้าง/ตรวจ platform Azure ที่จะใช้ |
| 17 | อัปโหลด pinned data/model ลง Blob แล้วตรวจ hash |
| 18 | ตรวจ assets, build/push image, deploy API และวัด cloud latency/cold |
| 19 | Submit Azure ML training และตรวจ job/registry |
| 20 | สร้าง monitoring/alert ทดลอง staging failure และ recovery; ตรวจ drift |
| 21 | ตั้ง CI identity/GitHub configuration และเตรียม workflow |
| 22 | รวมการตรวจ registry, alert, CI evidence, cold และ delivery |

ดังนั้นงานไม่ได้มีแค่ training แล้ว deploy แต่ครอบคลุมการเก็บเวอร์ชันข้อมูล โมเดลที่ตรวจซ้ำได้ การส่งระบบอัตโนมัติ และการรู้ว่าระบบเริ่มตอบผิดเมื่อใด

## 6. อ่านสไลด์ทีละหน้า

อธิบายตาม `MLOP-PJ_Presentation.pptx` และ `slide_sources.json` เวลารวม 480 วินาที สคริปต์ไทยด้านล่างใช้ซ้อมความเข้าใจ สามารถพูดอังกฤษโดยปรับจาก Q&A ได้ ไม่จำเป็นต้องอ่านทุกย่อหน้า

### Slide 1 — Travel Style Segmentation & Drift Monitoring (15 วินาที)

**หน้านี้บอกอะไร:** ชื่อโปรเจกต์และทีม แนะนำว่าทำ service จัดกลุ่ม travel-rating profiles โดยเน้นระบบ MLOps

**เราทำอะไรไป:** ต่อข้อมูล โมเดล API และระบบตรวจสอบเข้าด้วยกัน ไม่ใช่แค่แสดงผล K-Means ใน Notebook

**พูดแบบเข้าใจง่าย:** “โปรเจกต์ของเรารับคะแนนความชอบด้านการท่องเที่ยว แล้วจัดเป็นกลุ่ม เราทำตั้งแต่จัดการข้อมูลจนถึงบริการบน Azure พร้อม CI/CD และการตรวจจับข้อผิดพลาดครับ”

**ชี้ตรงไหน:** ชื่อโปรเจกต์และชื่อทีม แล้วไปหน้า 2 ไม่ต้องบอกว่างานทำวันไหนหรือแต่งประวัติการทำงาน

**หลักฐาน:** `README.md` และชื่อทีมในสไลด์จริง

### Slide 2 — ONE PROFILE, A SIMPLE TRAVEL SEGMENT (45 วินาที)

**หน้านี้บอกอะไร:** Input คือคะแนน 24 หมวด และ output คือ segment, distance, uncertainty และ version

**เราทำอะไรไป:** กำหนดโจทย์ที่มีขอบเขตชัด ให้บริการจัดกลุ่ม profile หนึ่งชุดได้ ยังไม่สร้าง recommender เต็มระบบ

**พูดแบบเข้าใจง่าย:** “เรารวมคะแนน 24 หมวดเป็นหนึ่ง profile แล้วดูว่าใกล้กับกลุ่มไหน ผลตอบกลับมีชื่อกลุ่มและข้อมูลที่ช่วยตรวจสอบผล เช่น version และ uncertainty ชื่อกลุ่มยังเป็นชื่อชั่วคราว เพราะยังไม่ได้ยืนยันความหมายกับผู้ใช้จริงครับ”

**ชี้ตรงไหน:** เส้นทาง input → output และชื่อแต่ละ field ให้ผู้ฟังรู้ว่าระบบทำงานให้ใคร ก่อนเล่า infrastructure

**ระวัง:** ไม่เรียกว่า personality test และไม่อ้างว่าแนะนำทริปที่ตรงใจแล้ว

**หลักฐาน:** `docs/MODEL_CARD.md`, `reports/bundle-manifest.json`; แหล่งข้อมูล [1]

### Slide 3 — FROM VERSIONED DATA TO A MONITORED API (40 วินาที)

**หน้านี้บอกอะไร:** สถาปัตยกรรมจากข้อมูลไปถึงบริการและ monitoring

**เราทำอะไรไป:** ใช้ Git/DVC + Blob เก็บเวอร์ชัน, Azure ML training/registry, Actions ทดสอบและ deploy, ACR เก็บ image, Container Apps รัน API และ Azure Monitor/Log Analytics ตรวจ logs

**พูดแบบเข้าใจง่าย:** “ทางซ้ายเป็นข้อมูลที่มีเวอร์ชัน จากนั้นฝึกและลงทะเบียนโมเดล ก่อนสร้าง image ต้องผ่าน tests แล้วจึงรัน API บน Container Apps ส่วน logs และ alert ช่วยดูว่าบริการทำงานถูกต้องหรือเริ่มมีปัญหาครับ”

**ชี้ตรงไหน:** อ่านตามลูกศรทีละกล่อง ไม่ต้องอ่านชื่อบริการทุกตัวแบบรายการจำศัพท์ แยก code ของ cloud อยู่ใน `cloudlayer` เพื่อไม่ให้ logic โมเดลผูกกับ Azure ทุกจุด

**ระวัง:** เรามี portability separation/audit แต่ยังไม่ได้พิสูจน์ deployment บน cloud เจ้าอื่น

**หลักฐาน:** `README.md`, `dvc.yaml`, `.github/workflows/ci.yml`, `cloudlayer/`; โจทย์วิชา [3]

### Slide 4 — ONE VERSIONED DATASET, ONE REPEATABLE PIPELINE (25 วินาที)

**หน้านี้บอกอะไร:** คุณภาพและการแบ่งข้อมูลก่อน train

**เราทำอะไรไป:** ตรวจ 5,456 แถว รับ 5,454 แถว quarantine 2 แถว และแบ่ง 3,817/817/820 โดยกัน profile ซ้ำข้ามชุด

**พูดแบบเข้าใจง่าย:** “เราตรวจข้อมูลก่อนฝึก แยกสองแถวที่มีค่าผิดรูปแบบไว้โดยไม่เดาซ่อม จากนั้นแบ่ง train, validation และ test โดยข้อมูลที่เหมือนกันต้องอยู่ชุดเดียวกัน และเรียน preprocessing จาก train เท่านั้นครับ”

**ชี้ตรงไหน:** ตัวเลข raw/accepted/quarantine แล้วชี้สัดส่วนในแถบ train/validation/test ตัวแถบเป็นจำนวน profiles ไม่ใช่คะแนนโมเดล

**ระวัง:** ค่า 0 ยังไม่ทราบความหมาย; การเลือก keep_zero คือผลเปรียบเทียบ representation ไม่ใช่การพิสูจน์ว่าศูนย์มีความหมายแน่นอน

**หลักฐาน:** `reports/data-audit.json`, `prepared-data.json`, `selection.json`; ภาพ `figures/data-split.png`; แหล่งข้อมูล [1]

### Slide 5 — THE SAME BUNDLE REACHES THE API (25 วินาที)

**หน้านี้บอกอะไร:** โมเดลที่ฝึก ตรวจ และ deploy เชื่อมกันด้วย version/hash

**เราทำอะไรไป:** Azure ML job Completed ตรวจ fresh fit เทียบ canonical bundle ผ่าน ลงทะเบียน travel-style v1 และตรวจ bundle ตอน API startup

**พูดแบบเข้าใจง่าย:** “เราเชื่อมโมเดลกลับไปหา training job และไฟล์ที่ตรวจไว้ได้ Cloud job fit ใหม่และตรวจ equivalence ก่อน export bundle ที่ผ่าน tests แล้ว API ยังตรวจ hash และ golden predictions ก่อนพร้อมใช้งานครับ”

**ชี้ตรงไหน:** การ์ด training/registry และรหัส model version กับ bundle/image hash ไม่ต้องอ่าน hash ยาวทุกตัว บอกว่าเป็นลายนิ้วมือที่ใช้ตรวจรุ่น

**ระวัง:** Hash ของ fresh serialized pipeline ไม่จำเป็นต้องตรง canonical bytes; version 1 ของ registry ไม่ใช่รหัส `abfd88e893ca`

**หลักฐาน:** `reports/azure-training-proof.json`, `finish-training-registry.json`, `bundle-manifest.json`, `ci-deploy-result.json`

### Slide 6 — LIVE DEMO: VALID AND UNEXPECTED INPUT (90 วินาที)

**หน้านี้บอกอะไร:** บริการตอบข้อมูลถูกต้องและรับมือข้อมูลผิดรูปแบบได้

**เราทำอะไรไป:** ตรวจจริงผ่าน HTTPS กับ input ที่บันทึกผลอ้างอิงไว้ มีหนึ่ง profile, invalid input และ batch 100

**พูดก่อนสลับหน้าจอ:** “ผมจะเรียก API บน Azure จริงด้วย profile ที่มีครบ 24 หมวด แล้วลองข้อมูลที่ขาด fields เพื่อดูว่าบริการปฏิเสธอย่างมีเหตุผลแทนการล่มครับ”

**ทำอะไรบนหน้าจอ:** ใช้เซลล์ live demo ในหัวข้อ 7 ของคู่มือนี้ แสดง ready → valid prediction → 422 → batch 100 แล้วกลับสไลด์

**อธิบายผล:** segment คือชื่อกลุ่ม, distance คือระยะหลัง preprocessing, uncertain คือธงที่ใช้ลดการบอกชื่อกลุ่มอย่างมั่นใจเกินข้อมูล, version ช่วยตรวจว่าใช้โมเดลใดอยู่

**ระวัง:** JSON ที่อยู่บนสไลด์เป็นผลจริงที่บันทึกไว้ ไม่ใช่หน้าจอ live ขณะพูด และ HTTP 422 ใน demo คือผลที่ต้องการจากข้อมูล invalid

**หลักฐาน:** `output/presentation/evidence/api-demo.json`, `service/app.py`, `scripts/http_check.py`

### Slide 7 — FAILED TESTS BLOCK DEPLOYMENT (35 วินาที)

**หน้านี้บอกอะไร:** CI/CD gate หยุดการ deploy เมื่อ tests ไม่ผ่าน

**เราทำอะไรไป:** รันสอง workflows ที่ source เดียวกัน มีทั้ง success และ deliberate failure พร้อมตรวจ jobs จริง

**พูดแบบเข้าใจง่าย:** “เราทดลองทั้งสองทาง รอบปกติ tests และ deploy ผ่าน ส่วนรอบที่จงใจให้ test ล้มเหลว deploy ถูกข้าม จึงมีหลักฐานว่าโค้ดที่ทดสอบไม่ผ่านไม่ถูกส่งขึ้นระบบครับ”

**ชี้ตรงไหน:** ฝั่ง NORMAL RUN กับ DELIBERATE FAILURE ถ้าจะเปิด Actions ให้เปิดลิงก์ที่เตรียมไว้ก่อน ไม่ต้องเริ่ม workflow ใหม่บนเวที

**ระวัง:** งาน evidence/documents ที่ commit ต่อมาทำให้ HEAD ต่างจาก tested source ได้ แต่ตรวจแล้วว่า CI inputs ไม่เปลี่ยน สีแดงไม่ใช่ทุกระบบล่ม และรอบ intentional CI failure ไม่ใช่ mapping incident ของหน้า 10

**หลักฐาน:** `reports/ci-runs.json`, `finish-ci-evidence.json`, `.github/workflows/ci.yml`

### Slide 8 — THE API WORKS; CLOUD LATENCY MISSES OUR TARGET (25 วินาที)

**หน้านี้บอกอะไร:** Correctness ผ่านใน tests แต่ cloud latency ยังไม่ผ่านเป้าที่ทีมตั้ง

**เราทำอะไรไป:** Warm tests 200 requests ที่ concurrency 10, batch 1 และ errors 0 มี local p95 274.54 ms, original cloud 813.77 ms และ pooled-client cloud 624.83 ms

**พูดแบบเข้าใจง่าย:** “Local ผ่านเป้า 300 ms แต่ cloud จาก WSL ยังเกินเป้า แม้ผล pooled client ต่ำลงก็ใช้วิธี client/warm-up ต่างกัน จึงยังไม่อ้างว่า server ดีขึ้นเท่านั้น Cold request วัดครั้งเดียวหลัง zero replicas ใช้ประมาณ 3.82 วินาทีครับ”

**ชี้ตรงไหน:** เส้นประ 300 ms และแถบทั้งสาม แล้วชี้การ์ด cold request แยกจาก warm p95

**ระวัง:** Network latency เป็นส่วนหนึ่งของเวลาที่วัด แต่เราไม่ได้แยกออกจนพิสูจน์ว่าเป็นสาเหตุทั้งหมด Cold sample เป็นผลของ image ที่ระบุใน cold report ไม่ใช่การวัด image ล่าสุดซ้ำ และไม่ใช่ p95 cold start

**หลักฐาน:** `reports/serving-recheck/local-load.json`, `azure-load.json`, `pooled-load.json`, `finish-cold.json`; ภาพ `figures/warm-latency.png`

### Slide 9 — MONITOR REQUESTS AND CHECK PREDICTION MEANING (25 วินาที)

**หน้านี้บอกอะไร:** ดูปริมาณ requests, latency และ semantic correctness

**เราทำอะไรไป:** ส่ง structured logs ไป Log Analytics สร้าง workbook และมี actual semantic alert event จาก staging failure

**พูดแบบเข้าใจง่าย:** “เราเก็บ status, latency และ model version โดยไม่เก็บคะแนน profile ทั้งชุดลง log Dashboard ช่วยดูการใช้งาน และ semantic canary ตรวจว่าผลยังตรงกับที่คาดไว้ มีหลักฐาน alert fired แล้วครับ”

**ชี้ตรงไหน:** กราฟด้านบนคือจำนวน requests ต่อช่วงเวลา ด้านล่างคือ logged application p95 กราฟวาดจาก query results จริง ไม่ใช่ภาพ Portal

**ระวัง:** Server log p95 ไม่ใช่ client HTTPS p95 ของหน้า 8; alert event มีจริง แต่ยังไม่ได้ส่ง email และยังไม่ใช่ live feature-drift dashboard

**หลักฐาน:** `reports/azure-telemetry.json`, `dashboard-workbook.json`, `finish-monitor.json`, `finish-alert.json`; ภาพ `figures/monitor-logs.png`

### Slide 10 — A WRONG SEGMENT MAPPING TRIGGERED DETECTION AND RECOVERY (45 วินาที)

**หน้านี้บอกอะไร:** ทดลอง fault ที่ระบบยังตอบได้แต่ความหมายผิด แล้วตรวจและกู้คืน

**เราทำอะไรไป:** เปลี่ยน cluster-to-segment mapping ใน staging แยก canary ได้ 503 มี alert event คืน config/restart แล้ว canary ได้ 200 ยืนยันสองครั้ง

**พูดแบบเข้าใจง่าย:** “เราเลือก failure ที่ไม่ใช่แค่ process ตาย แต่เป็นชื่อกลุ่มผิด ซึ่ง health check อาจไม่เห็น Semantic canary ตรวจพบได้ การกู้คืนครั้งแรกยังไม่ผ่าน เราจึงคืน config และ restart จนตรวจยืนยันผ่านจริง รวมเวลาจากตรวจพบประมาณ 7 นาที 16 วินาทีครับ”

**ชี้ตรงไหน:** INJECT → DETECT → ALERT → RECOVER ลูกศรบอกลำดับเหตุการณ์ ไม่ใช่ระยะเวลาเท่ากันทุกช่อง

**ระวัง:** Recovery ครั้งนี้ใช้ script/config action และการ retry ของเรา ไม่ใช่ self-healing อัตโนมัติที่ alert สั่ง rollback เอง และไม่ต้อง inject fault ใหม่ระหว่าง talk

**หลักฐาน:** `reports/finish-failure.json`, `finish-alert.json`, `tests/test_api.py`

### Slide 11 — A CONTROLLED SHIFT IS DETECTED OFFLINE (20 วินาที)

**หน้านี้บอกอะไร:** ตัวตรวจ input drift ตอบสนองต่อการเปลี่ยนข้อมูลที่เราควบคุมได้

**เราทำอะไรไป:** Reference 1,908 แถว Recent 200 แถว Calibration 100 รอบ และเพิ่ม 1.5 ในสี่ features แรกโดย clip ให้อยู่ 0–5

**พูดแบบเข้าใจง่าย:** “เราทดลอง offline ให้ข้อมูลเปลี่ยนแบบที่รู้ว่าเปลี่ยนจริง Score ของข้อมูลปกติอยู่ต่ำกว่า threshold แต่ข้อมูลที่เพิ่มคะแนนอยู่สูงกว่า จึงตรวจพบได้ ผลนี้ยังไม่ใช่ drift ของผู้ใช้จริงตามเวลาครับ”

**ชี้ตรงไหน:** แถบ normal ≈ 0.0994 กับ shifted ≈ 0.7879 และเส้น threshold ≈ 0.1257

**ระวัง:** ค่าบนแกนเป็น KS statistic ไม่ใช่ p-value หรือ accuracy; drift ไม่แปลว่าโมเดลคุณภาพแย่ลงแน่นอน และ flag นี้ไม่ได้เป็น actual Azure alert ของหน้า 10

**หลักฐาน:** `reports/input-drift.json`, `monitoring/drift.py`; ภาพ `figures/controlled-drift.png`

### Slide 12 — COST PER 1,000 PREDICTIONS: THE ESTIMATE AND ITS LIMITS (30 วินาที)

**หน้านี้บอกอะไร:** แยกงบประมาณกับยอด reported จริง

**เราทำอะไรไป:** ประเมิน short demo 88.89 THB รวม reserve 60 THB ได้ 8.89 THB ต่อ 1,000 จากสมมติ 10,000 predictions ส่วน query จริงใช้ 0.0012035014 USD กับ 841 profiles ในช่วงเดียวกัน ได้ 0.00143104 USD ต่อ 1,000

**พูดแบบเข้าใจง่าย:** “กราฟเป็นแผนก่อน credits ส่วนการ์ด reported cost ใช้ยอดจาก Azure และจำนวน valid profiles ในช่วงเดียวกัน ตัวเลขนี้ยังเป็น provisional เพราะ billing และ logs อาจมาช้า จึงไม่ใช้ยืนยัน full spend หรือบอกว่าอยู่ในงบแน่นอนครับ”

**ชี้ตรงไหน:** แยก PLANNED COST กับ REPORTED COST และหน่วย THB/USD ไม่ต้องเปรียบเทียบว่าสองตัวต่างกันกี่เท่า

**ระวัง:** reserve ไม่ใช่ยอด billed และอัตรา 40 THB/USD เป็นสมมติฐานในแผน ไม่ใช่อัตราเรียกเก็บเงินจริง

**หลักฐาน:** `reports/azure-cost-plan.json`, `cost-per-1000.json`, `azure-billing-query.json`, `docs/COST_REPORT.md`; ภาพ `figures/planned-cost.png`

### Slide 13 — WHAT ANOTHER WEEK WOULD IMPROVE (45 วินาที)

**หน้านี้บอกอะไร:** สิ่งที่จะพัฒนาต่อจากข้อจำกัดที่พบ

**เราทำอะไรไป:** ระบุปัญหาที่มีหลักฐานแล้ว และเสนอขั้นถัดไปโดยไม่อ้างว่าเสร็จ

**พูดแบบเข้าใจง่าย:** “ถ้ามีเวลาเพิ่ม เราจะเริ่มจากแยก network กับ application latency แล้วเลือกการปรับที่คุ้มค่า ตรวจต้นทุนเมื่อ billing ครบ เพิ่ม rolling-window drift จากข้อมูลใหม่จริง และตรวจความหมาย segment กับผู้ใช้ครับ”

**ชี้ตรงไหน:** ตาราง priorities โดยเรียง latency → cost → live drift → user quality

**ระวัง:** ยังไม่ได้แก้ cloud p95 จนผ่าน ยังไม่มี live drift หรือ user study การเพิ่ม replicas/เปลี่ยน region ต้องประเมินต้นทุน ไม่ใช่รับประกันว่าจะเร็วขึ้น และต้อง save evidence ก่อน cleanup

**หลักฐาน:** `reports/finish-delivery.json`, `docs/DELIVERY_STATUS.md`, `docs/FINAL_STEPS.md`

### Slide 14 — REFERENCES (5 วินาที)

**หน้านี้บอกอะไร:** ข้อมูลจากไหน โจทย์กำหนดอะไร และผลที่พูดมีหลักฐานไหน

**พูด:** “ข้อมูลมาจาก UCI ส่วน scope มาจาก course brief และตัวเลขระบบอ้างจาก reports กับ CI runs ของเราครับ”

**ชี้ตรงไหน:** Dataset DOI และ repository link ไม่ต้องอ่านรายการ references ทั้งหมด

**ระวัง:** Dataset เป็นแหล่งข้อมูล แต่ไม่ได้รับรองคะแนนระบบเรา Repository เป็น private ต้องเตรียมสิทธิ์เข้าถึงให้ผู้ตรวจ

**หลักฐาน:** แหล่งข้อมูล [1], โจทย์ [3], `reports/` และ CI links

### Slide 15 — Thank you (10 วินาที)

**พูด:** “ขอบคุณครับ ยินดีตอบคำถามเกี่ยวกับระบบและผลที่เราทดสอบครับ”

**เตรียมหน้าจอ:** คง Notebook demo, Actions สองรอบ และรายงาน failure/cost เปิดไว้สำหรับ Q&A ไม่ต้องเปิดเผย cloud.env, credentials หรือหน้าที่มี token

หลัง slide นี้เผื่อ Q&A อีก 5 นาที ไม่รวมอยู่ใน 8 นาทีของ talk

## 7. Live demo: ทำตามนี้ทีละเซลล์

### 7.1 เตรียมก่อนขึ้นนำเสนอ

1. เปิด VS Code ใน **WSL** ที่โฟลเดอร์ `MLOP-PJ` เช่นเดียวกับที่ใช้ทำงาน ไม่ต้องเปลี่ยนไป Windows Python
2. เปิด `notebooks/22_delivery.ipynb` แล้วเลือก kernel **MLOP-PJ (WSL)** หรือ Python ที่ `~/.venvs/mlop-pj/bin/python`
3. เพิ่ม code cells สำหรับ demo ที่ท้าย Notebook คัดลอกทีละส่วนจากด้านล่าง ไม่ต้องแก้เซลล์เดิม และไม่ต้องกด Run All เพราะเซลล์เดิมมี phase checks ที่ไม่จำเป็นต่อ demo
4. ลองรัน setup, ready และ preflight ด้านล่างหนึ่งรอบก่อนนำเสนอ จากนั้นคง kernel นี้ไว้และยุบผล preflight ตอนพูดจริง
5. เปิด Actions สองลิงก์ใน browser และ login GitHub ล่วงหน้า Repository เป็น private จึงอาจเปิดไม่ได้ถ้ายังไม่ login
6. แอปต้องยังไม่ถูก cleanup ถ้าลบ resource group แล้ว Azure URL จะใช้ไม่ได้ ต้องใช้ local demo หรือ saved evidence พร้อมบอกขอบเขตตามจริง

เซลล์ demo ส่ง HTTPS requests ไป API จริงและใช้ fixture/report ที่มีอยู่ ไม่ submit training, build image, deploy หรือ inject fault ใหม่ การเขียนคู่มือนี้ยังไม่ได้รันเซลล์เหล่านี้กับ cloud รอบใหม่ ผลที่แสดงในสไลด์เป็น saved evidence; เมื่อคุณรัน demo ผลบนหน้าจอจะเป็นผลสดในรอบนั้น

### Cell A — Setup: โหลด URL และตัวอย่างข้อมูล

```python
import json
import sys
from pathlib import Path

ROOT = next(
    p for p in (Path.cwd(), *Path.cwd().parents)
    if (p / "reports/golden-profiles.json").is_file()
)
assert Path(sys.prefix).name == "mlop-pj", "Select the project WSL kernel."
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.http_check import http_call, check_predictions, smoke

fixture = json.loads((ROOT / "reports/golden-profiles.json").read_text())
deploy = json.loads((ROOT / "reports/ci-deploy-result.json").read_text())
url = deploy["url"]
profile = fixture["profiles"][0].copy()

print("Python:", sys.executable)
print("API:", url)
print("Expected model:", fixture["model_version"])
print("Profile fields:", len(profile))
```

**กำลังทำอะไร:** หารากโปรเจกต์ โหลด URL จาก deployment report และโหลดตัวอย่าง profile ที่บันทึกผลอ้างอิงไว้ ไม่ train ใหม่ และไม่พิมพ์ URL ยาวเอง

**ผลที่ต้องเห็น:** Python ของ WSL environment, Azure API URL, model version `abfd88e893ca` และ Profile fields = 24 ถ้า assertion เรื่อง kernel ไม่ผ่าน ให้เลือก kernel ให้ถูก ไม่ลบ assertion เพื่อฝืนรัน

ถ้าอาจารย์อยากดู input ให้รัน `print(json.dumps(profile, indent=2))` จะเห็นตัวเลขครบ 24 fields ตัวอย่างนี้เป็น golden fixture ไม่ใช่ข้อมูลที่สร้างจากผู้ใช้สดตอนนำเสนอ

### Cell B — Ready: API พร้อมใช้โมเดลหรือยัง

```python
status, body, elapsed = http_call(url, "/ready", timeout=60)
print("HTTP:", status)
print(json.dumps(body, indent=2))
assert status == 200, "The API is not ready. Read the response."
assert body["model_version"] == fixture["model_version"]
```

**ผลที่ต้องเห็น:** HTTP 200, `status = ready` และ model version ตรง fixture การรันครั้งแรกอาจช้าจาก scale-to-zero ให้ลองก่อนขึ้นเวทีเพื่อไม่เสียเวลาใน demo 90 วินาที ผลครั้งนี้ไม่ใช่การวัด cold start แบบยืนยัน zero replicas

**พูด:** “บริการพร้อมใช้ และรายงาน model version ที่เราตรวจไว้ครับ”

**Preflight ก่อน talk เท่านั้น:** หลัง ready ผ่าน ใช้เซลล์นี้เช็คทั้งชุดหนึ่งรอบ แล้วตอน talk แสดงผลทีละเซลล์ C–E จะอธิบายง่ายกว่า

```python
checks = smoke(url, fixture)
print(json.dumps(checks, indent=2))
```

ต้องได้ `passed = true`, `status_codes = [200, 200, 200, 422, 200]`, `golden_predictions_match = true`, `batch_100_passed = true` ตัว smoke เปรียบเทียบผลหลาย field ไม่ใช่ดู HTTP 200 อย่างเดียว

### Cell C — Valid profile: ส่งข้อมูลถูกต้องหนึ่ง profile

```python
status, body, elapsed = http_call(
    url, "/predict", {"profiles": [profile]}, timeout=60
)
print("HTTP:", status)
print(json.dumps(body, indent=2))
assert status == 200
check_predictions(body, [fixture["expected"][0]], fixture["model_version"])
```

**ผลที่ต้องเห็น:** HTTP 200 และ predictions หนึ่งรายการ สำหรับ fixture นี้ผลที่บันทึกไว้คือ Segment 1, cluster 0, distance ประมาณ 4.1435, uncertain false และ version abfd88e893ca ส่วน request ID เปลี่ยนได้ตาม request ใหม่ ไม่ใช่ข้อผิดพลาด

**ชี้และพูด:** “เราได้รับชื่อกลุ่ม ระยะทาง และ version กลับมาจริง สำหรับตัวอย่างนี้ไม่ถูก flagged ว่า uncertain ผลยังตรงกับ golden result ที่ใช้ตรวจ regression ครับ”

ไม่ต้องอ่านค่าทุกช่องของ JSON และอย่าเรียก uncertain false ว่า confidence 100%

### Cell D — Missing fields: ข้อมูลผิดต้องได้ 422

```python
status, body, elapsed = http_call(
    url, "/predict", {"profiles": [{"Category 1": 2}]}, timeout=60
)
print("HTTP:", status)
print(json.dumps(body, indent=2))
assert status == 422
```

**กำลังทำอะไร:** จงใจส่งแค่หนึ่งหมวด ทั้งที่ต้องมี 24 หมวด จึงคาดหวัง 422 พร้อมรายละเอียดการปฏิเสธ เช่นให้ส่ง 24 named rating columns

**พูด:** “ข้อมูลนี้ขาด fields บริการจึงตอบ 422 โดยไม่ฝืนทำนายและไม่ทำให้ตัวแอปล่มครับ”

อย่าตกใจเมื่อเห็น 422 หรือแก้ input นี้ให้ครบก่อนแสดง เพราะการปฏิเสธ input ผิดคือสิ่งที่ต้องพิสูจน์ในเซลล์นี้

### Cell E — Batch 100: หลาย profiles ในหนึ่ง request

```python
status, body, elapsed = http_call(
    url, "/predict", {"profiles": [profile] * 100}, timeout=60
)
print("HTTP:", status)
print("Returned predictions:", len(body.get("predictions", [])))
print("Model:", body.get("model_version"))
assert status == 200
check_predictions(
    body, [fixture["expected"][0]] * 100, fixture["model_version"]
)
print("Batch check passed.")
```

**ผลที่ต้องเห็น:** HTTP 200, Returned predictions = 100 และ Batch check passed เราทำซ้ำ profile เดิมเพื่อเช็คขอบเขต batch และผลที่คาดหวัง ไม่ใช่ผู้ใช้จริง 100 คนที่เก็บใหม่

**พูด:** “หนึ่ง request รองรับได้สูงสุด 100 profiles และในกรณีนี้ผลตอบกลับทั้ง 100 รายการถูกตรวจเทียบกับผลที่คาดไว้ครับ”

อย่าเอาเวลาของ batch นี้ไปบอกว่าเป็น warm p95 เพราะการวัด p95 เดิมใช้ batch size 1 และหลาย requests

### Cell F — Canary: เตรียมไว้ตอบ Q&A

```python
status, body, elapsed = http_call(url, "/canary", timeout=60)
print("HTTP:", status)
print(json.dumps(body, indent=2))
assert status == 200 and body.get("passed") is True
```

**กำลังทำอะไร:** ให้บริการตรวจ golden profiles ภายในแอปเอง ผลปกติต้องได้ 200 และ passed true ถ้าเวลาพอใช้ใน slide 9 หรือเปิดเมื่อถูกถามว่า “health ต่างจาก canary อย่างไร” ไม่ต้อง inject mapping ผิดเพื่อแสดง 503 ซ้ำ

### ถ้าอาจารย์ส่ง input ที่เราไม่ได้เตรียม

ใช้ `profile` สำเนาตัวอย่างเดิมแล้วเปลี่ยนตัวเลขในช่องที่อาจารย์ต้องการ หากยังครบ 24 ช่อง ค่าเป็นตัวเลข finite และอยู่ใน 0–5 บริการควรรับได้ แต่กลุ่มหรือ uncertainty อาจเปลี่ยน จึงไม่เทียบกับ golden result เดิมหลังเปลี่ยน input

```python
custom_profile = profile.copy()
custom_profile["Category 1"] = 2.5
status, body, elapsed = http_call(
    url, "/predict", {"profiles": [custom_profile]}, timeout=60
)
print("HTTP:", status)
print(json.dumps(body, indent=2))
```

ตัวอย่างข้างบนคือข้อมูลใหม่ที่ดัดแปลง ไม่ได้มี saved expected segment ล่วงหน้า ถ้า uncertain true แล้ว segment null แต่ HTTP 200 ถือว่าเป็นพฤติกรรมที่ออกแบบไว้สำหรับ valid input ที่ไกลจากกลุ่ม

หากต้องการทดสอบคะแนนเกินช่วง ใช้สำเนาอีกชุดตั้ง `Category 1 = 6` แล้วคาดหวัง 422 หรือส่ง `[profile] * 101` เพื่อทดสอบ batch เกินขอบเขต การทดสอบเหล่านี้ไม่ต้องเปลี่ยนโมเดล/config บน cloud

### 7.2 ลำดับบนเวทีให้ทัน 90 วินาที

| เวลาคร่าว ๆ | สิ่งที่ทำ | สิ่งที่พูด |
|---|---|---|
| 0–10 วินาที | เปลี่ยนจาก slide 6 ไป Notebook ที่ setup/ready แล้ว | เรียก Azure API จริง ใช้ profile ครบ 24 ช่อง |
| 10–40 วินาที | รัน C และชี้ prediction | ชื่อกลุ่ม distance uncertainty version |
| 40–60 วินาที | รัน D | Missing fields ถูกปฏิเสธด้วย 422 |
| 60–80 วินาที | รัน E | รองรับ batch 100 และตรวจผลครบ |
| 80–90 วินาที | กลับ slide 7 | ต่อด้วย gate ที่ป้องกันโค้ดผิดถูก deploy |

เวลาเป็นแผนซ้อม ไม่ใช่ผลวัดหรือการรับประกัน ถ้าจะให้คนพูดกับคนกดคนละคน ต้องตกลงกับทีมก่อน ไม่ได้กำหนดผู้พูดจากชื่อสมาชิกเอง

### 7.3 หน้าอื่นที่ควรเปิดเตรียมไว้

**Actions:** เปิดสองลิงก์นี้แล้วขยาย jobs tests/deploy ไม่ต้องกด Run workflow ใหม่

- [Normal run: tests/deploy success](https://github.com/DewPerawis/MLOP-PJ/actions/runs/38173375457)
- [Intentional failure: tests failure/deploy skipped](https://github.com/DewPerawis/MLOP-PJ/actions/runs/38173380800)

**Failure/alert evidence:** เปิด reports/finish-failure.json กับ finish-alert.json แล้วชี้ `failure_detected`, `recovered`, `previous_errors`, `alert_fired` และ monitorCondition Resolved บอกว่านี่เป็นหลักฐานเหตุการณ์ที่บันทึกไว้ ไม่ใช่กำลังทดลอง fault สด

**Dashboard:** หากจะเปิด Portal ให้ login ล่วงหน้า ไป resource group ของโปรเจกต์ แล้วหา Workbook **MLOP Travel Style** หากเมนูต่างจากที่คุ้น ให้ค้น Workbooks หรือชื่อ resource แทนการเสียเวลาหาเมนูบนเวที ส่วน `reports/dashboard-workbook.json` เป็น export ที่เก็บ queries/config จริง ไม่ใช่ภาพหน้าจอ

**Cost:** เปิด reports/cost-per-1000.json ชี้ numerator, denominator, currency และ actual_limits อย่าส่ง query billing ใหม่ระหว่างพูด เพราะค่าขึ้นกับเวลาที่ provider รายงานและอาจใช้เวลารอ

### 7.4 ถ้า demo ไม่ผ่าน ให้แยกปัญหาก่อน

| สิ่งที่เห็น | หมายถึงอะไร / ทำอย่างไร |
|---|---|
| ModuleNotFoundError | รัน A ก่อน และตรวจ kernel/project path ไม่ต้องติดตั้ง package สุ่ม |
| Kernel assertion ไม่ผ่าน | เลือก project WSL kernel ไม่ใช้ base environment |
| Timeout / URL เปิดไม่ได้ | ตรวจ network และว่า resources ยังอยู่; ลอง ready ก่อนเวที หากยังไม่ได้ให้ใช้ saved evidence และบอกว่ารอบนี้ live connection ไม่สำเร็จ |
| `/ready` เป็น 503 | บริการยังไม่พร้อมใช้ bundle; อ่าน response/log ไม่บอกว่าผ่านเพราะ health เป็น 200 |
| Valid fixture ได้ 422 | ตรวจ JSON ว่ามี profiles list และครบชื่อ 24 ช่อง; ลอง C เดิมโดยไม่แก้ fixture |
| D ได้ 422 | เป็นผลที่ตั้งใจให้เกิด ไม่ใช่เหตุให้หยุดทั้งหมด |
| Canary 503 หรือ golden mismatch | เป็นปัญหา correctness ต้องเก็บผลและตรวจ version/mapping ไม่ลบ assertion เพื่อให้ดูผ่าน |
| Request ID เปลี่ยน | ปกติ เพราะแต่ละ request มี ID ใหม่ |

กรณี cloud ล่มจริง ให้เปิด `output/presentation/evidence/api-demo.json` แล้วบอกชัดว่าเป็น saved real HTTP evidence **ไม่ใช่ live result** ภาพหรือไฟล์ที่บันทึกไว้ช่วยอธิบายได้ แต่ไม่แทนผล live demo ที่สำเร็จในรอบนำเสนอ

## 8. อะไรเป็น requirement และอะไรยังต้องทำหลัง demo

Capstone ต้องมี versioned data/code, reproducible training, model registry/lineage, inference, CI/CD tests ที่ล้มเหลวได้, dashboard, working alert, cost ต่อ 1,000 predictions, one-page model card และ deliberate failure [3] มีหลักฐานแต่ละส่วนใน `reports/finish-delivery.json` แต่การผ่าน checklist ไม่รับประกันคะแนนหรือความพร้อม production

300 ms และงบ 150 THB เป็น targets ของทีม จึงต้องอธิบายเมื่อยังไม่ถึง ไม่ใช่เลข fixed pass/fail ใน brief ส่วน screenshot Portal เป็นหลักฐานเสริมที่มีประโยชน์ Brief ไม่บังคับว่า dashboard/alert ต้องพิสูจน์ด้วย screenshot เท่านั้น

Lab 5 Task 5 ต้องใช้ actual billing [4] และ rubric ของ Capstone อ้างงาน cost จาก Lab 5 แต่ไม่ควรเหมารวมว่า task ทุกข้อของ Lab 5 เช่น LLM/second provider เป็น requirement ของโปรเจกต์นี้

หลัง demo ให้เก็บหลักฐานแล้วทำ cleanup ตาม `docs/FINAL_STEPS.md` ตรวจ `reports/cleanup.json` ว่า `cleanup_verified=true` และติดตาม billing ที่ครบขึ้นเพื่อปรับ cost report Cloud reminders ไม่ได้ลบ resources ให้อัตโนมัติ และหลัง cleanup แอป/Blob remote จะใช้ไม่ได้ ผู้ตรวจต้องมีช่องทางข้อมูล public UCI กับ pinned hash ตาม README

## 9. แผนที่ศัพท์สำหรับคนที่เพิ่งอ่านงาน

| ศัพท์ | เข้าใจง่าย ๆ |
|---|---|
| Profile / feature | Profile คือหนึ่งชุดข้อมูล; feature คือหนึ่งหมวดคะแนนในชุดนั้น |
| Training / inference | Training เรียนโมเดล; inference ใช้โมเดลที่เรียนแล้วตอบข้อมูลใหม่ |
| Centroid | จุดศูนย์กลางของกลุ่มในพื้นที่ข้อมูลที่โมเดลใช้ |
| Pipeline | ขั้นตอนที่ต่อกัน เช่น impute → scale → K-Means |
| Artifact / bundle | ไฟล์ผลลัพธ์ที่ต้องใช้รันโมเดล และสิ่งประกอบที่เซฟร่วมกัน |
| Manifest | รายการข้อมูลกำกับ เช่น hash, version, features และ thresholds |
| Hash / digest | ลายนิ้วมือไฟล์/image ใช้ตรวจว่าตรงรุ่นหรือเปลี่ยนไป |
| Registry / lineage | รายการโมเดลที่ลงทะเบียน / เส้นทางย้อนกลับไปหาที่มาของโมเดล |
| Golden fixture | Input และ expected output ที่รู้ไว้ ใช้จับ regression |
| Regression test | ตรวจว่าการแก้ใหม่ไม่ได้ทำพฤติกรรมที่เคยถูกต้องเสียไป |
| CI/CD gate | เงื่อนไขที่ต้องผ่านก่อนส่งโค้ดขึ้นระบบ |
| Staging | ระบบแยกสำหรับทดสอบก่อนหรือแทนการเสี่ยงกับแอปหลัก |
| Monitoring / alert | ดูข้อมูลการทำงาน / สร้างเหตุเตือนเมื่อเจอเงื่อนไข |
| Semantic canary | ตรวจความหมายของผลที่คาดหวัง ไม่ใช่แค่ process ยังตอบ |
| Input drift / concept drift | การกระจาย input เปลี่ยน / ความสัมพันธ์ input กับ outcome เปลี่ยน |
| Replica / scale-to-zero | Instance ของแอป / ลดจำนวน instance เหลือศูนย์เมื่อ idle |
| Warm / cold | แอปพร้อมรันอยู่แล้ว / เริ่มพร้อมใช้งานหลังไม่มี replica |
| p95 | เวลาที่ประมาณ 95% ของ samples ในการวัดไม่เกิน |
| OIDC / managed identity | วิธีใช้ identity/token ที่จัดการให้ แทนใส่ password ในโค้ด |
| Provisional cost | ยอดที่ provider รายงานตอนนี้ แต่ยังอาจไม่ครบทั้งหมด |

## 10. แหล่งข้อมูลที่ใช้ตรวจคู่มือนี้

ไฟล์ภายในต่อไปนี้อ้างจากราก `MLOP-PJ` ตัวเลขระบบมาจาก reports ไม่ได้มาจากเอกสารวิธีใช้ของ library

- `output/presentation/MLOP-PJ_Presentation.pptx`, `slide_sources.json`, `slide_guide.md`: ลำดับหน้าและเนื้อหาสไลด์จริง
- `src/data.py`, `train.py`, `bundle.py`, `service/app.py`, `runtime.py`: วิธีเตรียมข้อมูล ฝึก และตอบ request
- `scripts/train_selected.py`, `http_check.py`, `cloudlayer/finish_build.py`, `finish_monitor.py`, `finish_ci.py`: training/cloud evidence/monitoring/CI
- `reports/data-audit.json`, `prepared-data.json`, `selection.json`, `bundle-manifest.json`, `azure-training-proof.json`, `finish-training-registry.json`: ข้อมูลและโมเดล
- `reports/ci-runs.json`, `ci-deploy-result.json`, `finish-ci-evidence.json`, `finish-failure.json`, `finish-alert.json`, `input-drift.json`: CI, serving และ failure/drift
- `reports/azure-load.json`, `pooled-load.json`, `finish-cold.json`, `serving-recheck/local-load.json`, `cost-per-1000.json`: latency และต้นทุน

**References สำหรับข้อมูลและคำอธิบาย:**

[1] S. Renjith, “Travel Review Ratings,” UCI Machine Learning Repository, 2018, DOI: 10.24432/C5C31Q. [หน้า UCI](https://archive.ics.uci.edu/dataset/485/travel%2Breview%2Bratings)

[2] scikit-learn, “silhouette_score,” official documentation. [คำอธิบาย metric](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html) เอกสารใช้ประกอบคำอธิบายทั่วไป ผลทดลองจริงใช้ package versions ที่บันทึกในโปรเจกต์

[3] ITCS355, “Capstone Project Brief.” ไฟล์ `docs/reference/course/project/project-brief.md` หัวข้อ Required components, Presentation และ Marking

[4] ITCS355, “Lab 5 — Cloud MLOps and Cost.” ไฟล์ `docs/reference/course/labs/lab-05-cloud-mlops-and-cost.md` Task 5
