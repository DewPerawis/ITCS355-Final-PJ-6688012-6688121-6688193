# Scope review — 11 ตุลาคม 2026

**ผลวิเคราะห์: หัวข้อ Travel Style Segmentation & Drift Monitoring ตรง Capstone scope ในระดับ problem/design และเริ่มพัฒนาได้ตามคำชี้แจงผู้ใช้ ยังไม่ใช่ระบบที่ผ่าน rubric แล้ว**

แหล่ง: Proposal Azure ปัจจุบันใน `../proposals/current/`, project brief ต้นฉบับ `../../project/project-brief.md`, Lab 5 `../../labs/lab-05-cloud-mlops-and-cost.md` และ specification

## ความสอดคล้องกับ required components

| ข้อกำหนด Capstone | Design ที่เสนอ | สิ่งที่จะต้องสร้าง/พิสูจน์ |
|---|---|---|
| Versioned data and code | Git + DVC; immutable raw data | dataset version/hash + reproducible access |
| Automated reproducible training | Small CPU clustering + tracked pipeline | locked env/seeds/train-only transforms/one-command run |
| Registered model with lineage | Azure ML/MLflow + full model bundle | exact registry version + code/data/run/image lineage + reload |
| Deployed inference | FastAPI online + batch ≤100 บน Container Apps | real staging endpoint/revision + smoke/load tests |
| CI/CD with tests that fail | unit/data-contract/model behavior/container integration | failing bad PR + deployment blocked |
| Dashboard | service latency/errors/version + data/assignment stats | dashboard from project telemetry |
| Working alert ≥1 | semantic canary และ calibrated drift signals | alert delivered on controlled event |
| Cost/1,000 predictions | Azure allocation 150 THB ก่อนเครดิต | current estimate + actual billing/count/optimization |
| One-page model card | intended use/data/quality/lineage/limitations | finished one-page artifact |
| Deliberate failure | cluster-name mapping ผิดใน staging | detection/diagnosis/rollback/confirmed recovery/regression |

K-Means เป็นขอบเขตที่เหมาะเพราะ model complexity ต่ำและ assignment ของ profile ใหม่ทำได้ จึงมีเวลาเน้น operational components ที่วิชาให้คะแนน Primary use case ใน Proposal เป็น interactive personalization จึงมีเหตุผลรองรับ online API โดยต้องวัด cold start แยก

ความเสี่ยงที่ยังต้องตัดสินจากข้อมูลจริง: zero-value semantics, malformed records, duplicate leakage, cluster stability/naming, distance threshold, cloud region/quota/fixed costs ตัวเลข budget/latency เป็น targets และ assumptions ไม่ใช่ผลที่ทำได้แล้ว

## ความคล้าย Lab 5

Lab 5 Part A overlap กับ managed pipeline/evaluation gate, least privilege, retraining, portability discipline, cost และ verified teardown Capstone ยังคงรวม versioning/training/registry จาก Labs 1–2, deployment จาก Lab 3 และ monitoring/failure handling จาก Lab 4

Lab 5 Part B กำหนด LLM golden-set evaluation, guardrails และ token bill สำหรับ Lab นั้น Capstone brief ที่มีอยู่ไม่ได้กำหนด LLM เป็น mandatory component ทุกหัวข้อ และไม่ได้สั่ง second-provider swap เป็น required component แยกเหมือน Lab 5 จึงไม่เพิ่มสองงานนี้เป็น scope project โดยอัตโนมัติ แต่ยังรักษา portability contract/audit ที่ brief ระบุ

## คำชี้แจง workflow ล่าสุด

ผู้ใช้แจ้งในแชตวันที่ 11 ตุลาคม 2026 ว่า Proposal เป็นการส่ง ไม่จำเป็นต้องได้รับ approval แยกหากตรงโจทย์ และมอบหมายให้ผู้ช่วยตรวจความสอดคล้อง

Project brief ในเครื่องยังมีข้อความ approval ก่อน build จึงบันทึกข้อแตกต่างอย่างตรงไปตรงมา: **การปฏิบัติงานใช้คำชี้แจงผู้ใช้ล่าสุด ไม่เพิ่ม approval gate และไม่อ้างว่าได้ตรวจพบหนังสืออนุมัติหรือประกาศอาจารย์ใหม่แล้ว** ต้นฉบับเอกสารอาจารย์ไม่ถูกแก้

เริ่มจาก Notebook environment/data audit แล้ว implement ทีละช่วง Paid cloud operations, promotion, teardown และ Git writes ยังใช้ user-executed steps ตามที่ตกลง หากมีประกาศอาจารย์ใหม่ให้ตรวจเทียบและปรับ scope ตามประกาศจริง
