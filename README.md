# Travel Style Segmentation & Drift Monitoring

ITCS355 Machine Learning Operation and Deployment · Faculty of ICT, Mahidol University

**สถานะ 10 ตุลาคม 2026: จัดพื้นที่โปรเจกต์และแผนเรียบร้อย ยังไม่มี Capstone implementation หรือผลทดสอบระบบใน repository นี้**

โปรเจกต์จะรับ rating profile ครบ 24 หมวด แล้วคืน travel preference segment ให้แพลตฟอร์มท่องเที่ยวใช้ระหว่าง interactive personalization โมเดลหลักคือ K-Means พร้อม simple Gaussian Mixture comparator ระบบจะเน้น reproducibility, lineage, deployment, CI/CD, monitoring, alert และ failure recovery บน Microsoft Azure

## เริ่มอ่านจากตรงไหน

| เอกสาร | ใช้ทำอะไร |
|---|---|
| [Proposal ปัจจุบัน](proposals/current/Project%20Proposal%206688012-6688121-6688193.pdf) | โจทย์หนึ่งหน้า ฉบับ Azure และ ownership ที่ทีมต้องยืนยัน |
| [Proposal source](proposals/current/Project%20Proposal.docx) | ต้นฉบับแก้ไขได้ |
| [PLAN.md](PLAN.md) | แผนละเอียด งานแต่ละ phase, dependencies, outputs และ exit criteria; local-only |
| [AGENT.md](AGENT.md) | กติกาผู้ช่วยและการรักษาขอบเขต; local-only |
| [การย้ายไฟล์](docs/MIGRATION.md) | รายการย้าย/สำเนาและผลตรวจความครบถ้วน |
| [Course references](docs/reference/README.md) | สำเนาโจทย์ rubric และ handouts สำหรับอ่านในเครื่อง |

`AGENTS.md` และ `CLAUDE.md` เป็นชื่อสำเนาของ `AGENT.md` สำหรับเครื่องมือแต่ละตัว ส่วน Proposal เก่าอยู่ `proposals/archive/` และคู่มือเดิมอยู่ `docs/legacy/` ไม่ใช้ฉบับเก่าเป็น implementation authority

## ทีมตาม Proposal ปัจจุบัน

| สมาชิก | งานหลักตาม Proposal |
|---|---|
| Perawis Buranasing · 6688012 | Data, DVC, preprocessing, training, tracking และ registry |
| Supitsara Tanasansukstid · 6688121 | FastAPI, Docker, Container Apps, CI/CD และ load test |
| Atichat Kangsamut · 6688193 | Monitoring, drift, alert, failure demo, cost และ model card |

การระบุชื่อใน Proposal ไม่ใช่หลักฐานว่าทีมยืนยัน ownership หรืออาจารย์อนุมัติแล้ว ต้องบันทึกหลักฐานทั้งสองส่วนก่อน build เต็มระบบ

## เป้าหมายที่ต้องพิสูจน์

- Versioned data/code, automated reproducible training และ registered model ที่ trace lineage ได้
- Deployed inference, CI/CD ที่บล็อก bad change ได้, dashboard และ alert ที่ทำงานจริง
- Planned failure: cluster-to-segment mapping ผิดใน staging → semantic alert → investigation → rollback → regression gate
- Cost ต่อ 1,000 predictions, model card หนึ่งหน้า และ demo 8 นาที + Q&A 5 นาที
- Proposal target: warm p95 <300 ms ที่ concurrency 10, batch ≤100; cold start วัดแยก
- Proposal estimate: งบ 150 THB ก่อนเครดิต (compute/serving 70 + storage/registry/monitoring 25 + contingency 55) ยังไม่ใช่ bill หรือราคาที่ตรวจสอบปัจจุบัน

## โครงสร้างที่เตรียมไว้

```text
MLOP-PJ/
├── AGENT.md / AGENTS.md / CLAUDE.md   # กติกาภายในสามชื่อ เนื้อหาเดียวกัน
├── PLAN.md                          # แผนภายใน
├── README.md
├── proposals/current/               # Proposal Azure ปัจจุบัน
├── proposals/archive/               # Proposal เก่า
├── docs/MIGRATION.md
├── docs/legacy/                     # คู่มือเก่าแบบเก็บต้นฉบับ
├── docs/reference/course/           # สำเนาเอกสารอาจารย์ในเครื่อง
├── configs/                         # reserved; ยังไม่มี config ที่รันได้
├── src/ service/ cloudlayer/        # reserved; ยังไม่มี implementation
├── monitoring/ tests/ loadtest/     # reserved
├── data/ reports/ models/           # reserved; data/models outputs ใช้ DVC/artifact store
└── scripts/sync_agent_rules.ps1     # ใช้งานได้สำหรับซิงก์กติกา
```

โฟลเดอร์ reserved มี `.gitkeep` เท่านั้น ไม่ใช่ scaffold ที่รันระบบได้ `make reproduce`, `make deploy` และคำสั่ง project pipeline ใน PLAN เป็น **interface ที่วางแผนจะสร้าง** ยังรันไม่ได้ และยังไม่มี lock file หรือ environment ที่ติดตั้ง

## ขอบเขตการจัดย้ายและ Git

ย้ายไฟล์โปรเจกต์จาก `../6688012-ITCS355-MLOP/pj/` ทั้ง 6 ไฟล์ โดยรักษา bytes เดิมและตรวจ SHA-256 ไม่ย้าย Labs หรือ repository history และไม่ย้ายต้นฉบับอาจารย์ โฟลเดอร์ `pj/` เดิมมี README ชี้มาที่นี่

Git repository และ `.gitattributes` ที่มีอยู่ใน MLOP-PJ ถูกเก็บไว้ `.gitignore` ป้องกัน secrets/raw data/cache และแยกบันทึกภายในออกจาก deliverables; ไม่ ignore source, tests, DVC pointers หรือ evidence reports ทั้งโฟลเดอร์

Links ไป PLAN/AGENT/reference snapshots ใช้ได้ในเครื่องนี้; เอกสารเหล่านี้เป็น local-only และไม่ควรเป็น dependency ของคำสั่ง reproduce สำหรับผู้ตรวจ Final README จะต้องแทนสถานะเตรียมงานนี้ด้วย prerequisites, commands, expected outputs และหลักฐานจริงที่อยู่ใน final repository

ขั้นแรกคือ **Phase 0 ใน PLAN**: เก็บ approval, ยืนยัน ownership/วันส่งจากประกาศจริง และ freeze scope จากนั้นทำ data audit เพื่อปิดความหมาย/นโยบายค่า `0` ก่อน training
