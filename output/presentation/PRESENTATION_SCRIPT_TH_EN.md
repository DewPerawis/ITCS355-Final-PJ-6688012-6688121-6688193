# Presentation script — Thai and English

ใช้คู่กับ `6688012_6688121_6688193_Presentation.pptx` และ `LIVE_DEMO.ipynb` ในโฟลเดอร์นี้ ตรวจลำดับจาก PowerPoint และ PDF ฉบับปัจจุบันแล้ว: **15 slides, talk 8 minutes, Q&A อีก 5 minutes**

[เปิดสไลด์](C:/Users/SN23341J001185/Documents/MyWork/ICT/ICTYear4_1/MLop/public_teaching_mlaiops/course/MLOP-PJ/output/presentation/6688012_6688121_6688193_Presentation.pptx) · [เปิด Notebook demo](C:/Users/SN23341J001185/Documents/MyWork/ICT/ICTYear4_1/MLop/public_teaching_mlaiops/course/MLOP-PJ/output/presentation/LIVE_DEMO.ipynb) · [เปิดคู่มือไทย](C:/Users/SN23341J001185/Documents/MyWork/ICT/ICTYear4_1/MLop/public_teaching_mlaiops/course/MLOP-PJ/output/presentation/PROJECT_SUMMARY_TH.md)

## วิธีใช้ไฟล์นี้

- อ่าน **TH** เพื่อเข้าใจและซ้อมภาษาไทย หรืออ่าน **EN** เพื่อพูดภาษาอังกฤษ เลือกหนึ่งภาษา ไม่อ่านสองภาษาต่อกันบนเวที
- ข้อความ **ทำบนหน้าจอ** เป็นคำสั่งให้ผู้กด ไม่ต้องอ่านออกเสียง ส่วนข้อความใต้ TH/EN เป็นบทพูดที่อ่านได้เลย
- รัน demo **A/B ก่อนเริ่มพูด** แล้วใช้ **C–F ใน Slide 6** บทของ C–F อยู่ตรงหน้านั้น ให้อ่านต่อไปแล้วกลับ Slide 7 ได้เลย
- G ใช้ประกอบ Slide 7 และ H ใช้ประกอบ Slide 10 เลือกเปิด Notebook card หรือหลักฐาน browser ตามที่ซ้อม ไม่ต้องอธิบายสองรอบ
- I ใช้เฉพาะเมื่อถูกถามให้ลอง input ใหม่ ส่วน J ใช้เมื่อจบ demo/session บทของ A/B/I/J อยู่ท้ายไฟล์
- บทพูดผล live ใช้เมื่อผลบนหน้าจอตรง expected ถ้าไม่ผ่าน ให้ใช้บทสำรองท้ายไฟล์ ห้ามอ่านว่า “ผ่านแล้ว” ทั้งที่ยัง error

เวลาของแต่ละหน้าเป็นแผนซ้อม รวม 480 วินาที โดย Slide 6 รวมเวลารันและสลับหน้าจอแล้ว ส่วนเตรียม A/B และ Q&A ไม่รวมใน 480 วินาที ความเร็วพูดและเวลารอ API ต้องซ้อมจริงอีกครั้ง

## Part 1 — Slide-by-slide script

### Slide 1 — Travel Style Segmentation & Drift Monitoring (15 seconds)

**ทำบนหน้าจอ:** เปิดหน้า title ชี้ชื่อโปรเจกต์ ไม่ต้องอ่านรหัสสมาชิกครบทุกคน ไม่บอกวันเริ่มทำงาน

**TH**

สวัสดีครับ วันนี้ทีมเราจะนำเสนอ Travel Style Segmentation and Drift Monitoring เราทำบริการจัดกลุ่มจากคะแนนด้านการท่องเที่ยว โดยต่อให้เป็นระบบบน Azure พร้อมการทดสอบและติดตามการทำงานครับ

**EN**

Hello everyone. Our project is Travel Style Segmentation and Drift Monitoring. We turn travel-rating profiles into a working Azure service, with tests and monitoring around the model.

### Slide 2 — ONE PROFILE, A SIMPLE TRAVEL SEGMENT (45 seconds)

**ทำบนหน้าจอ:** ชี้ INPUT → MODEL → OUTPUT ตามลำดับ

**TH**

ระบบรับคะแนน 24 หมวดเป็นหนึ่ง profile แล้วใช้ K-Means จัดเข้าหนึ่งในห้ากลุ่ม ผลมีชื่อกลุ่ม ระยะจากจุดศูนย์กลาง uncertainty และ model version กลุ่มเหล่านี้อาจช่วยแพลตฟอร์มท่องเที่ยวแบ่งความสนใจของผู้ใช้ได้ แต่ตอนนี้ยังใช้ชื่อ Segment 1 ถึง 5 ชั่วคราว เราไม่ได้ทดสอบว่าแนะนำสถานที่ได้ดีแล้ว และไม่ได้ใช้ทำนายบุคลิกภาพครับ

**EN**

The service takes 24 category ratings as one profile and assigns it to one of five groups using K-Means. It returns a segment, distance, uncertainty flag, and model version. A travel platform could use these groups to understand similar interests. The names are still provisional. We have not tested recommendation quality or personality claims.

### Slide 3 — FROM VERSIONED DATA TO A MONITORED API (40 seconds)

**ทำบนหน้าจอ:** ชี้ตามลูกศรจาก DATA ไป SERVE แล้วชี้ OBSERVE ด้านล่าง

**TH**

เริ่มจากข้อมูลและโค้ดที่มีเวอร์ชัน โดยใช้ Git, DVC และ Azure Blob จากนั้นฝึกและลงทะเบียนโมเดลบน Azure ML GitHub Actions ตรวจ tests ก่อนสร้างและ deploy image จาก ACR บริการจริงรันบน Container Apps ส่วน logs, dashboard และ alert ช่วยดูการทำงาน และนำปัญหาที่พบกลับไปเพิ่มใน tests ครับ

**EN**

We start with versioned data and code using Git, DVC, and Azure Blob. Azure ML trains and registers the model. GitHub Actions checks the tests before building and deploying an ACR image. Container Apps runs the API. Logs, a dashboard, and an alert help us observe failures and feed them back into tests.

### Slide 4 — ONE VERSIONED DATASET, ONE REPEATABLE PIPELINE (25 seconds)

**ทำบนหน้าจอ:** ชี้ raw → accepted → quarantine แล้วชี้แถบ split

**TH**

ข้อมูลดิบมี 5,456 แถว เราแยกสองแถวที่มีค่าผิดรูปแบบไว้ เหลือ 5,454 แถว จากนั้นแบ่ง train, validation และ test โดย profile ที่เหมือนกันต้องอยู่ชุดเดียวกัน และ fit preprocessing จาก train เท่านั้นเพื่อลดข้อมูลรั่วครับ

**EN**

We accepted 5,454 of the 5,456 raw rows and quarantined two malformed rows. Identical profiles stay in the same split. We fit preprocessing only on training data, use validation to choose settings, and reserve test data for evaluation.

### Slide 5 — THE SAME BUNDLE REACHES THE API (25 seconds)

**ทำบนหน้าจอ:** ชี้ MANAGED TRAINING → SERVING BUNDLE แล้วชี้ version/hash โดยไม่อ่าน hash ยาวทุกตัว

**TH**

Azure training job สำเร็จและลงทะเบียนโมเดลแล้ว โดย fit ใหม่และตรวจว่าเทียบเท่ากับโมเดลที่เราทดสอบไว้ ก่อนนำ verified bundle ไปใช้ Bundle เก็บทั้ง preprocessing, mapping, thresholds และ version และ API ตรวจ hash กับ golden predictions ก่อนพร้อมใช้งานครับ

**EN**

Azure training completed and the model was registered. A fresh fit matched the tested model before we kept the verified bundle for serving. The bundle includes preprocessing, mapping, thresholds, and version. Startup checks its hash and golden predictions before readiness.

### Slide 6 — LIVE DEMO: VALID AND UNEXPECTED INPUT (90 seconds)

**ทำบนหน้าจอ:** สลับไป `LIVE_DEMO.ipynb` ที่ A/B ผ่านแล้ว ยุบ code และผล preparation เลือก CASE 0 ตามที่ซ้อม ใช้ C → D → E → F บทพูดด้านล่างรวมอยู่ใน 90 วินาทีนี้ ไม่ใช่เวลาเพิ่ม

**TH — เปิด demo**

ต่อไปผมจะเรียก API บน Azure จริง เริ่มจาก profile ที่ถูกต้อง แล้วลองข้อมูลที่ขาด fields และ batch 100 ครับ

**EN — Demo opening**

I will now call the Azure API, starting with a valid profile, then incomplete input and a batch of 100.

ถ้ากำลังใช้ local fallback ให้ใช้บท local ใน Part 3 แทนคำเปิดด้านบน

<a id="demo-c"></a>
#### Demo Cell C — Input (0–20 seconds, including the opening)

**ทำบนหน้าจอ:** รัน C ชี้กราฟหกหมวด ถ้าต้องการดูครบ กด Show all 24 ratings แต่ไม่จำเป็นต้องขยายระหว่าง talk สั้น ๆ

**TH**

นี่เป็น profile ตัวอย่างที่บันทึกไว้ เราแสดงหกหมวดให้อ่านง่าย แต่ส่งคะแนนครบทั้ง 24 หมวดไป API ครับ

**EN**

This is a saved example profile. We show six categories for readability, but send all 24 ratings to the API.

<a id="demo-d"></a>
#### Demo Cell D — Prediction (20–45 seconds)

**ทำบนหน้าจอ:** รัน D รอการ์ด PREDICTION ชี้ Segment, Uncertain และ Model ก่อน Distance สำหรับ CASE 0 expected คือ Segment 1 / uncertain No ไม่ต้องอ่าน version ยาวทุกตัว

**TH**

API ตอบ Segment 1 และตัวอย่างนี้ไม่ถูก flagged ว่า uncertain เราตรวจผลกับ golden result ด้วย ระยะทางไม่ใช่เปอร์เซ็นต์ความมั่นใจครับ

**EN**

The API returns Segment 1, without an uncertainty flag. We also check this result against the golden reference. Distance is not a confidence percentage.

ถ้าเลือก CASE อื่น ให้พูดชื่อกลุ่มตามหน้าจอจริง แทนการอ่านว่า Segment 1

<a id="demo-e"></a>
#### Demo Cell E — Invalid input (45–65 seconds)

**ทำบนหน้าจอ:** รัน E ชี้ INVALID INPUT: SAFELY REJECTED และ HTTP 422

**TH**

ตอนนี้ผมจงใจส่งแค่หนึ่งหมวด บริการจึงตอบ 422 เพราะข้อมูลไม่ครบ นี่เป็นการปฏิเสธที่เราคาดหวัง ไม่ใช่แอปล่มครับ

**EN**

I deliberately send only one rating. The API returns 422 because fields are missing. This is the expected rejection, not a crash.

<a id="demo-f"></a>
#### Demo Cell F — Batch 100 (65–85 seconds)

**ทำบนหน้าจอ:** รัน F ชี้ Profiles sent = 100, Predictions checked = 100 และ HTTP 200

**TH**

หนึ่ง request รับได้สูงสุด 100 profiles รอบนี้เราทำซ้ำตัวอย่างเดิมเพื่อเช็คขอบเขต batch ผลครบ 100 และผ่านการตรวจ ไม่ใช่การวัด throughput ครับ

**EN**

One request supports up to 100 profiles. We repeat this example to check the batch limit. All 100 results are verified. This is not a throughput benchmark.

**ทำบนหน้าจอ (85–90 seconds):** กลับ Slide 7 ไม่รัน I/J ในช่วงนี้

### Slide 7 — FAILED TESTS BLOCK DEPLOYMENT (35 seconds)

**ทำบนหน้าจอ:** ชี้ NORMAL RUN กับ DELIBERATE FAILURE หรือรัน G เพื่อแสดง SAVED CI EVIDENCE ใช้บทเดียวด้านล่าง หากเปิด Actions ให้เปิดแท็บที่เตรียมไว้ แล้วชี้ jobs tests/deploy ไม่กดเริ่ม workflow ใหม่

**TH**

เราทดลอง CI สองทางจาก source commit เดียวกัน รอบปกติ tests และ deploy ผ่าน ส่วนรอบที่จงใจให้ test ล้มเหลว deploy ถูกข้าม จึงมีหลักฐานว่า gate หยุดการส่งโค้ดที่ทดสอบไม่ผ่าน สีแดงในรอบนี้เป็นสิ่งที่ตั้งใจ ไม่ใช่รอบ deploy ปกติที่เสียครับ

**EN**

These two completed runs use the same source commit. The normal run passed tests and deployment. In the deliberate failure run, tests failed and deployment was skipped. The red run is intentional: it shows that the gate blocks deployment when tests fail.

### Slide 8 — THE API WORKS; CLOUD LATENCY MISSES OUR TARGET (25 seconds)

**ทำบนหน้าจอ:** ชี้เส้นประ target 300 ms แล้วเปรียบเทียบ local กับ cloud สองแถบ ไม่อ่านตัวเลขทั้งหมดตามลำดับ ชี้การ์ด cold request แยก

**TH**

Local ผ่านเป้า p95 300 milliseconds แต่ cloud ทั้งสองวิธียังเกินเป้า วิธี pooled client วัดได้ต่ำลง แต่การวัดเปลี่ยนด้วย จึงยังไม่อ้างว่า server เร็วขึ้น ส่วน cold request ประมาณ 3.82 วินาทีเป็นหนึ่ง sample ไม่ใช่ p95 ครับ

**EN**

Local p95 met our 300-millisecond target, but both cloud tests missed it. The pooled-client result was lower, with a different measurement method. Cold readiness took about 3.82 seconds in one sample, not a p95 estimate.

### Slide 9 — MONITOR REQUESTS AND CHECK PREDICTION MEANING (25 seconds)

**ทำบนหน้าจอ:** ชี้ request counts ด้านบน แล้วชี้ logged p95 กับ ACTUAL ALERT หากเปิด workbook ให้เปิดเตรียมไว้ก่อน ไม่ค้นหาเมนูใหม่บนเวที

**TH**

Dashboard ดูจำนวน requests, errors, application latency และ model version เราไม่ log คะแนน profile ทั้งชุด กราฟนี้มาจากผล query จริง และมี semantic alert fired แล้ว resolved แต่ยังไม่ได้ตั้ง email ส่วน application latency ไม่ใช่ client HTTPS latency ครับ

**EN**

Our dashboard tracks requests, errors, application latency, and model version, without logging full profiles. The charts use saved query results. A semantic alert fired and later resolved; email is not configured. Application timing differs from client HTTPS timing.

### Slide 10 — A WRONG SEGMENT MAPPING TRIGGERED DETECTION AND RECOVERY (45 seconds)

**ทำบนหน้าจอ:** ชี้ INJECT → DETECT → ALERT → RECOVER หรือรัน H เพื่อแสดง SAVED STAGING INCIDENT ใช้บทเดียวด้านล่าง เหตุการณ์นี้เป็นหลักฐานที่บันทึกไว้ ไม่ inject fault ใหม่บนเวที

**TH**

นี่เป็นเหตุการณ์ที่บันทึกไว้จาก staging แยก เราสลับชื่อ segment ที่ผูกกับกลุ่ม ทำให้โมเดลยังรันได้แต่ความหมายของคำตอบผิด Canary ตรวจพบและตอบ 503 พร้อมมี alert จริง การกู้คืนครั้งแรกไม่ผ่าน เราจึงคืน config และ restart จน canary ผ่านสองครั้ง รวมเวลาตั้งแต่ตรวจพบถึงกู้คืนประมาณ 7 นาที 16 วินาที ไม่ใช่ alert สั่ง rollback เองครับ

**EN**

This is a saved incident from a separate staging app. We swapped segment mappings, so the model still ran but the returned meaning was wrong. The canary detected it and an alert fired. The first recovery failed. We restored configuration, restarted staging, and confirmed the canary twice. Total recovery took about seven minutes sixteen seconds; it was not automatic alert rollback.

### Slide 11 — A CONTROLLED SHIFT IS DETECTED OFFLINE (20 seconds)

**ทำบนหน้าจอ:** ชี้ normal ต่ำกว่าเส้น threshold และ injected shift สูงกว่าเส้น ไม่ต้องอ่านทุกค่า/ทุกขนาด sample

**TH**

เราทดลอง input drift แบบ offline โดยเพิ่มคะแนนในสี่หมวด ข้อมูลปกติอยู่ต่ำกว่า threshold แต่ข้อมูลที่เปลี่ยนถูกตรวจพบ นี่ยังไม่ใช่ drift ของผู้ใช้จริงหรือการพิสูจน์ concept drift ครับ

**EN**

We tested input drift offline by shifting four ratings. The normal sample stayed below the threshold; the shifted sample was detected. This is not observed live drift or evidence of concept drift.

### Slide 12 — COST PER 1,000 PREDICTIONS: THE ESTIMATE AND ITS LIMITS (30 seconds)

**ทำบนหน้าจอ:** ชี้แผนทางซ้าย แล้วแยก PLANNED COST กับ REPORTED COST ทางขวา อย่าเทียบค่า THB กับ USD ตรง ๆ

**TH**

แผน short demo รวมประมาณ 88.89 บาท หรือ 8.89 บาทต่อ 1,000 predictions เมื่อสมมติ 10,000 predictions ส่วน reported cost ใช้ยอด Azure และ 841 profiles ในช่วงเดียวกัน โดยแสดงเป็น USD แต่ billing และ logs อาจยังมาไม่ครบ จึงเป็นค่าชั่วคราว ไม่ใช่บิลสุดท้ายหรือหลักฐานว่าอยู่ในงบแน่นอนครับ

**EN**

Our short-demo plan is about 88.89 baht, or 8.89 baht per thousand at 10,000 assumed predictions. The reported figure uses Azure cost and 841 observed profiles in the same window, in USD. Billing and logs may lag, so this is provisional, not a final bill or proof of the budget cap.

### Slide 13 — WHAT ANOTHER WEEK WOULD IMPROVE (45 seconds)

**ทำบนหน้าจอ:** ชี้ตารางตามลำดับ latency → cost → live drift → user quality และบรรทัด cleanup

**TH**

ถ้ามีเวลาเพิ่ม เราจะเริ่มจากแยก network กับ application latency ก่อนเลือกวิธีปรับที่คุ้มค่า จากนั้นตรวจต้นทุนเมื่อ billing ครบ ต่อ drift check กับข้อมูลใหม่แบบ rolling windows และตรวจความหมายของ segment กับผู้ใช้ เพราะตอนนี้ชื่อกลุ่มยังชั่วคราวและความหมายศูนย์ยังไม่ชัด นี่เป็นแผนพัฒนาต่อ ส่วนหลัง final demo เราจะเก็บหลักฐานและตรวจการลบ cloud resources ครับ

**EN**

With another week, we would first separate network and application latency before choosing a cost-effective change. We would then reconcile billing, connect drift checks to live windows, and review segment meaning with users. These are planned improvements. Labels are still provisional and zero meaning is unknown. After the final demo, we will save evidence and verify cloud cleanup.

### Slide 14 — REFERENCES (5 seconds)

**ทำบนหน้าจอ:** ชี้รายการ references ผ่าน ๆ ไม่อ่าน DOI หรือ URL ยาว

**TH**

ข้อมูลมาจาก UCI ส่วนข้อกำหนดและผลระบบอ้างจาก course brief กับรายงานของเราครับ

**EN**

These are our dataset, course brief, and project evidence sources.

### Slide 15 — Thank you (10 seconds)

**ทำบนหน้าจอ:** จบ presentation แล้วคง Notebook/Actions/รายงานไว้สำหรับ Q&A อีก 5 นาที

**TH**

ขอบคุณครับ ยินดีตอบคำถาม และเปิดผลทดสอบหรือหลักฐานประกอบเพิ่มเติมครับ

**EN**

Thank you. We are ready for questions and can show the supporting results and evidence.

## Part 2 — Demo script for every cell

ตารางนี้เป็นสารบัญ A–J บท C–F รวมอยู่ใน Slide 6 แล้ว ส่วน G/H ใช้บทของ Slide 7/10 เพื่อไม่พูดซ้ำ

| Cell | ใช้เมื่อไร | ไปที่บทพูด |
|---|---|---|
| A | ก่อนเริ่ม talk / หลังเปิดเครื่องหรือ kernel ใหม่ | A ด้านล่าง |
| B | ก่อนเริ่ม talk รอ READY FOR DEMO | B ด้านล่าง |
| C | Slide 6 — แสดง input | [Cell C](#demo-c) |
| D | Slide 6 — prediction | [Cell D](#demo-d) |
| E | Slide 6 — invalid input | [Cell E](#demo-e) |
| F | Slide 6 — batch 100 | [Cell F](#demo-f) |
| G | Slide 7 — saved CI evidence | G ด้านล่าง / บท Slide 7 |
| H | Slide 10 — saved incident | H ด้านล่าง / บท Slide 10 |
| I | Q&A — input ที่ดัดแปลงใหม่ | I ด้านล่าง |
| J | หลังจบ demo session | J ด้านล่าง |

### Demo Cell A — Setup and mode (before the talk)

**ทำบนหน้าจอ:** เปิด Notebook ใน VS Code WSL เลือก MLOP-PJ kernel รัน A โดยค่าเริ่มต้น MODE=cloud ดูว่า DEMO SETUP ระบุ LIVE AZURE API หากใช้ local ต้องบอกตามป้ายจริง ใช้บทนี้ซ้อมอธิบาย ไม่จำเป็นต้องโชว์ setup ระหว่าง talk

**TH**

ขั้นนี้โหลด URL และตัวอย่างจากไฟล์โปรเจกต์ พร้อมเลือกโหมด demo ตอนนี้ผมเลือก cloud เพื่อเรียก Azure API เดิม ไม่ได้ฝึกหรือ deploy ใหม่ครับ

**EN**

This step loads the API URL and example data from the project files. I select cloud mode to call the existing Azure API. It does not retrain or redeploy the system.

### Demo Cell B — Prepare and check the API (before the talk)

**ทำบนหน้าจอ:** รัน B รอ READY FOR DEMO ก่อนแสดง C–F หากยังรอหรือ PREPARATION STOPPED ห้ามอ่านบท success ด้านล่าง เมื่อเตรียมแล้ว ยุบ code/ผล A/B เพื่อให้คนดูเริ่มที่ input ได้เลย

**TH — เมื่อผ่านแล้ว**

ขั้นเตรียมตรวจ readiness, semantic canary, golden predictions, invalid input และ batch แล้วผ่าน เราจึงพร้อมแสดงบริการ ขั้นนี้ช่วยให้การเรียกครั้งแรกและการตรวจระบบเกิดก่อนขึ้นพูดครับ

**EN — After it passes**

Preparation passed readiness, the semantic canary, golden predictions, invalid-input handling, and the batch check. We are ready to present. We do this before the talk to handle the first request and verify the service.

ถ้าปิดเครื่องหรือ restart kernel หลังเตรียม ต้องเริ่ม A/B ใหม่ ไม่ใช้ผลที่ค้างบนหน้าจอเป็นการยืนยัน session ใหม่

### Demo Cell G — Saved CI evidence (with Slide 7)

**ทำบนหน้าจอ:** รัน G ป้ายต้องเป็น SAVED CI EVIDENCE เปิดลิงก์เฉพาะเมื่อเตรียม login GitHub แล้ว

**ใช้บท TH/EN ของ Slide 7 เป็นบทหลัก** หากต้องการประโยคสั้นขณะสลับจากสไลด์มาที่ Notebook ใช้ด้านล่างแทนบางส่วน ไม่อ่านซ้ำทั้งสองชุด

**TH**

การ์ดนี้อ่านผลจากสอง Actions runs ที่เสร็จแล้ว ลิงก์เปิด jobs จริงได้ เราไม่ได้เริ่ม CI ใหม่ระหว่างนำเสนอครับ

**EN**

This card shows two completed Actions runs. The links open the actual jobs. We are not starting another CI run during the talk.

### Demo Cell H — Saved failure and recovery (with Slide 10)

**ทำบนหน้าจอ:** รัน H ดู SAVED STAGING INCIDENT ชี้ 503 → alert → 200 และ recovery time

**ใช้บท TH/EN ของ Slide 10 เป็นบทหลัก** ประโยคด้านล่างใช้ชี้ประเภทหลักฐานเมื่อเปิดการ์ด ไม่ใช่บทเพิ่มที่ต้องอ่านซ้ำ

**TH**

นี่เป็นหลักฐาน incident ที่บันทึกไว้ ไม่ใช่การทำให้ระบบผิดซ้ำตอนนี้ เราเก็บทั้งความพยายามกู้คืนที่ไม่ผ่านและผลยืนยันการกู้คืนจริงครับ

**EN**

This is saved incident evidence, not a new fault injection. It includes the failed recovery attempt and the later confirmed recovery.

### Demo Cell I — Custom input (optional Q&A)

**ทำบนหน้าจอ:** เปลี่ยนคะแนนใน `custom_profile` ตามโจทย์อาจารย์ โดยคง 24 named fields จากนั้นรัน I กราฟจะแสดง input ที่เปลี่ยน และ prediction มาจาก request ใหม่ ไม่แก้ fixture/model

**TH — ก่อนรัน**

ผมจะเปลี่ยนคะแนนตามที่อาจารย์เสนอ แล้วส่งข้อมูลใหม่นี้ไป API ผลอาจเปลี่ยนกลุ่มหรือถูก flagged ว่า uncertain จึงไม่ใช้ชื่อกลุ่มเดิมเป็นเฉลยครับ

**EN — Before running**

I will change the rating as requested and send this modified profile to the API. The group or uncertainty may change, so the original segment is not treated as the expected answer.

**TH — ถ้าได้ 200 และ uncertain เป็น No**

บริการรับข้อมูลใหม่ได้ และตอบกลุ่มตามที่เห็นบนหน้าจอ พร้อม model version เดิมครับ

**EN — If HTTP is 200 and uncertainty is No**

The service accepts the modified profile and returns the group shown here, using the recorded model version.

**TH — ถ้าได้ 200 และ uncertain เป็น Yes**

ข้อมูลรูปแบบถูกต้อง แต่ไกลจากกลุ่มมากเกิน threshold เราจึงไม่บอกชื่อ segment และแสดง uncertainty แทน ไม่ใช่ request ล้มเหลวครับ

**EN — If HTTP is 200 and uncertainty is Yes**

The input is valid, but too far from its assigned group under our distance rule. We return no segment name and mark it uncertain. The request itself succeeded.

**TH — ถ้าได้ 422 จากข้อมูลที่ตั้งใจให้ผิด**

ข้อมูลใหม่นี้ไม่ผ่านกติกา เช่นคะแนนเกินช่วง บริการจึงปฏิเสธพร้อมเหตุผล แทนการฝืนทำนายครับ

**EN — If deliberately invalid input returns 422**

The modified input breaks the contract, such as a rating outside the allowed range. The API rejects it with a reason instead of forcing a prediction.

### Demo Cell J — Stop this demo session (after the demo)

**ทำบนหน้าจอ:** รัน J เมื่อไม่ใช้ prediction ต่อแล้ว อย่ารันก่อน Q&A ที่ยังต้องใช้ I หากจะกลับมา demo ต้องเริ่ม A/B ใหม่

**TH**

ขั้นนี้ปิด demo session และหยุด local process ที่ Notebook สร้างไว้เท่านั้น ยังไม่ได้ลบ Azure resources การ cleanup cloud จะทำแยกหลังจบ final demo และเก็บหลักฐานแล้วครับ

**EN**

This closes the demo session and stops its local process. It does not delete Azure resources. Cloud cleanup is a separate step after the final demo and evidence collection.

## Part 3 — Backup lines: waiting, local mode and failure

ใช้เฉพาะเมื่อเกิดสถานการณ์นั้น ไม่รวมในบทปกติ 8 นาที หากเกิด error จริง ไม่ยืนยันผลสำเร็จจากการ์ดเก่าที่ค้างบนหน้าจอ

### If the first request is still waking up

**ทำบนหน้าจอ:** รอผลจริง ไม่กดรันซ้อนหลายครั้ง ถ้ายังไม่ผ่านให้หยุดตามข้อความ error

**TH**

บริการใช้ scale-to-zero จึงอาจต้องเริ่ม instance เมื่อเรียกครั้งแรก เราจะรอผล readiness ก่อนยืนยันว่าพร้อมครับ

**EN**

The service uses scale-to-zero, so the first request may need to start an instance. We will wait for readiness before claiming it is ready.

### If using local fallback

**ทำบนหน้าจอ:** เปลี่ยน MODE=local แล้วรัน A/B ใหม่ ใช้เมื่อ READY FOR DEMO ของ local ผ่าน ป้ายต้องเป็น LIVE LOCAL API — NOT AZURE

**TH**

รอบนี้ผมใช้ Local API สำรองบนเครื่องนี้ ไม่ใช่ Azure live demo ใช้ bundle และ input contract เดิม ส่วนผล cloud และ CI จะอ้างจากหลักฐานที่บันทึกไว้ครับ

**EN**

For this run, I am using the local API fallback on this laptop, not the live Azure endpoint. It uses the same bundle and input contract. Cloud and CI results are shown as saved evidence.

### If the live API is unavailable

**ทำบนหน้าจอ:** เก็บ error หยุดบอกว่า live ผ่าน เปิด saved api-demo.json หรือ JSON บน Slide 6 เพื่ออธิบายหลักฐานย้อนหลัง

**TH**

การเรียก live ในรอบนี้ยังไม่สำเร็จ ผมจะเปิดผล real HTTP ที่บันทึกไว้เพื่ออธิบายพฤติกรรมที่เคยตรวจ แต่ไม่อ้างว่าเป็นผลสดของรอบนี้ครับ

**EN**

The live request did not succeed in this run. I will show saved real HTTP evidence to explain the tested behaviour, without claiming it is a current live result.

### If a canary or golden prediction check fails

**ทำบนหน้าจอ:** หยุด demo ที่ต้องอาศัยผลนั้น เก็บ response/error ตรวจ version/mapping ภายหลัง ไม่ลบ assertion หรือเปลี่ยน expected เพื่อให้ผ่าน

**TH**

ผลไม่ตรงกับ semantic check ที่คาดไว้ เราต้องตรวจ version และ mapping ก่อน จึงยังไม่ยืนยันว่าผลถูกต้อง การตรวจนี้มีไว้ไม่ให้เราฝืนแสดงผลที่ผิดครับ

**EN**

The result did not match our semantic check. We need to inspect the version and mapping before claiming correctness. This check is meant to stop us from presenting an unchecked result.

## Part 4 — Quick reading notes

### คำอ่านที่ใช้บ่อย

| คำบนสไลด์ | อ่านเป็นอังกฤษ | ความหมายสั้น ๆ |
|---|---|---|
| API | A-P-I | ช่องทางเรียกบริการ |
| Azure | AZH-er | Cloud ที่ใช้ในงาน |
| K-Means | kay means | วิธีจัดกลุ่ม |
| DVC | D-V-C | เครื่องมือจัดการเวอร์ชันข้อมูล |
| ACR | A-C-R | ที่เก็บ container images ของ Azure |
| CI/CD | C-I, C-D | ตรวจและส่งระบบอัตโนมัติ |
| p95 | P ninety-five | เปอร์เซ็นไทล์ 95 ไม่ใช่ mean |
| 200 / 422 / 503 | two hundred / four twenty-two / five oh three | HTTP status codes |
| 300 ms | three hundred milliseconds | Target warm p95 ของทีม |
| 3.82 seconds | about three point eight two seconds | Cold readiness sample เดียว |
| Canary | kuh-NAIR-ee | ตัวตรวจ known prediction results |
| Provisional | pruh-VIZH-uh-nuhl | ยังเป็นชั่วคราว/ยังไม่สรุปสุดท้าย |

ไม่ต้องอ่าน hash, URL หรือ model version ทีละตัว หากถูกถามให้ชี้ field ใน report แทน

### ตัวเลขไว้ตอบเมื่อถูกถาม ไม่ต้องอ่านทุกค่าระหว่าง talk

| เรื่อง | ผลที่ตรวจจากรายงาน |
|---|---|
| Split | Train 3,817 / validation 817 / test 820 |
| K-Means quality | Validation silhouette 0.1448 / test silhouette 0.1445 |
| Local / original cloud / pooled cloud warm p95 | 274.54 / 813.77 / 624.83 ms |
| Warm workload | 200 requests, concurrency 10, batch 1; errors 0 |
| Cold sample | 3,819.60 ms ≈ 3.82 seconds; one readiness request after zero replicas |
| Drift | Normal 0.0994 / threshold 0.1257 / shifted 0.7879 |
| Recovery | Detection → confirmed recovery 7 min 16.4 sec, including first failed attempt |
| Planned cost | 88.89 THB total / 8.89 THB per 1,000 at 10,000 predictions |
| Provisional reported cost | 0.0012035014 USD / 841 observed profiles × 1,000 = 0.00143104 USD per 1,000 |

ตัวเลขเหล่านี้เป็น saved measurements ไม่ใช่ผลวัดใหม่ตอนเขียนสคริปต์ หากมี report ใหม่ก่อนนำเสนอ ต้องตรวจและปรับบทด้วย โดยเฉพาะ cost และสถานะ live

## Sources — สำหรับตรวจบท ไม่ต้องอ่านบนเวที

- สไลด์ปัจจุบัน: `output/presentation/6688012_6688121_6688193_Presentation.pptx` และ PDF ชื่อเดียวกัน มี 15 หน้า
- ลำดับ/เวลา: `output/presentation/slide_sources.json` รวม 480 seconds และ Q&A 300 seconds
- Demo steps/output labels: `output/presentation/LIVE_DEMO.ipynb`, `demo_support.py`
- ข้อมูลและโมเดล: `reports/data-audit.json`, `prepared-data.json`, `selection.json`, `bundle-manifest.json`, `azure-training-proof.json`, `finish-training-registry.json`
- CI และ runtime: `reports/ci-runs.json`, `finish-ci-evidence.json`, `ci-deploy-result.json`, `output/presentation/evidence/api-demo.json`
- Monitoring/failure: `reports/finish-monitor.json`, `finish-alert.json`, `finish-failure.json`, `azure-telemetry.json`
- Latency/drift/cost: `reports/serving-recheck/local-load.json`, `azure-load.json`, `pooled-load.json`, `finish-cold.json`, `input-drift.json`, `cost-per-1000.json`
- References ใช้ตาม Slide 14: [1] S. Renjith, Travel Review Ratings, UCI, 2018, DOI 10.24432/C5C31Q; [2] ITCS355 Capstone Project Brief; [3] Project reports and CI runs ของทีม

คู่มือรายละเอียดและ startup หลังเปิดเครื่องอยู่ใน `PROJECT_SUMMARY_TH.md` หัวข้อ 7 ส่วนคำถามเพิ่มเติมอยู่ใน `PRESENTATION_QA_EN_TH.md` การเขียนไฟล์นี้ไม่ได้รัน training, cloud checks หรือ demo ใหม่ และไม่ได้แก้ outputs ของ Notebook เดิม
