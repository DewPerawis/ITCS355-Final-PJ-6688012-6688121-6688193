# Project migration record

วันที่: **10 ตุลาคม 2026**

ต้นทาง: `MLop/public_teaching_mlaiops/course/6688012-ITCS355-MLOP/pj/`

ปลายทาง: `MLop/public_teaching_mlaiops/course/MLOP-PJ/`

## สิ่งที่ย้ายจริง

| ชื่อต้นทางใน pj | ตำแหน่งใหม่ใน MLOP-PJ | การจัดประเภท |
|---|---|---|
| `Project Proposal.docx` | `proposals/current/Project Proposal.docx` | Current editable proposal |
| `Project Proposal 6688012-6688121-6688193.pdf` | `proposals/current/Project Proposal 6688012-6688121-6688193.pdf` | Current one-page Azure proposal |
| `Travel Style Segmentation & Drift Monitoring - One-Page Project Proposal.docx` | `proposals/archive/` ชื่อเดิม | Historical proposal |
| `Travel Style Segmentation & Drift Monitoring - Project Proposal.pdf` | `proposals/archive/` ชื่อเดิม | Historical proposal |
| `AGENTS.md` | `docs/legacy/pj-AGENTS.original.md` | Historical internal guide |
| `CLAUDE.md` | `docs/legacy/pj-CLAUDE.original.md` | Historical internal guide |

ไฟล์ทั้ง **6 ไฟล์** ถูกย้ายด้วย native filesystem move โดยไม่เขียนทับไฟล์ปลายทาง เนื้อหา/byte size และ SHA-256 ตรวจตรงกับที่บันทึกก่อนย้ายทุกไฟล์ และไฟล์ชื่อเดิมไม่เหลือในต้นทาง

เก็บ `pj/README.md` ในตำแหน่งเดิมเพื่อให้ผู้เปิดโฟลเดอร์เก่ารู้ตำแหน่งใหม่ ไม่เก็บ Proposal หรือกติกาสองชุดที่อาจแก้ไม่ตรงกัน

## สิ่งที่คัดลอกเป็น reference

สำเนา **20 ไฟล์** จาก course root: `project/`, `spec/`, `reference/`, `labs/`, `slides/`, `README.md`, `getting-started-azure.md` และ `getting-started-gcp.md` อยู่ใน `docs/reference/course/`

ตรวจ SHA-256 ตรงต้นฉบับทุกไฟล์ ต้นฉบับอาจารย์ยังอยู่ครบ ไม่ย้ายหรือแก้ไข สำเนาถูกจัดเป็น local-only references เพื่ออ่าน specification/rubric/handouts โดยไม่ปะปนกับผล implementation

## สิ่งที่เตรียมใหม่

- `AGENT.md` เป็นฉบับหลัก และ `AGENTS.md`/`CLAUDE.md` เป็น aliases เนื้อหาเดียวกัน
- `PLAN.md` มี phases, dependencies, owners/reviewers, outputs, exit criteria, rubric matrix, risks และ demo/cost/cleanup
- README/status notes และ `.gitignore` สำหรับ standalone project
- `scripts/sync_agent_rules.ps1` ซิงก์กติกาเฉพาะ project root และตรวจ SHA-256
- Reserved folders พร้อม `.gitkeep`: configs/src/service/cloudlayer/monitoring/tests/loadtest/data/reports/models ยังไม่มี project runtime implementation
- `docs/MIGRATION_MANIFEST.json` เก็บ source/target/operation/bytes/SHA-256 และ destination HEAD ก่อน/หลังสำหรับตรวจในเครื่อง

คู่มือเก่าเก็บครบ แต่ข้อความใหม่อิง Proposal ปัจจุบัน เช่น primary user เป็น **travel platform** และ Proposal มีชื่อ owners จริงแล้ว โดยยังต้องยืนยันทีมและ approval แยกจากการมีชื่อในเอกสาร

## ผลการรักษา repository และขอบเขต

- Existing Git repository ใน MLOP-PJ ไม่ถูกแทนที่หรือย้าย history
- Destination HEAD ก่อน/หลังการจัดย้าย: `d5c636f` เหมือนเดิม ตรวจ full hash ใน manifest
- `.gitattributes` เดิมไม่เปลี่ยน SHA-256
- ไม่แก้ source/results ของ Lab 1–3; source student HEAD ที่ตรวจคือ `cc4605623f4d848a45497763c8d294b247ff7ebf`
- ไม่ย้าย nested `.git`, environments, raw data, credentials, cloud.env หรือ saved model artifacts
- ไม่รัน project training, dependency installation, cloud provisioning, promotion, teardown, commit หรือ push

การกล่าวถึง Labs ใน PLAN เป็น **reuse plan** ผล Lab ไม่ใช่ผล Capstone และ Labs ยังคงอยู่ใน repository เดิม

## ขอบเขตหลักฐานปัจจุบัน

อ่าน source DOCX และตรวจ Proposal PDF ปัจจุบันแบบ rendered visual: A4 หนึ่งหน้า ฉบับ Microsoft Azure ตัวเลข warm latency, cost allocation และ workload เป็น proposed targets/assumptions

ไม่ได้ download/re-audit UCI dataset หรือยืนยัน current licence/prices/quota/cloud state ในรอบจัดโฟลเดอร์ Historical audit ในคู่มือเก่าไม่ถูกยกระดับเป็น fresh result ยังไม่พบ scope approval, ownership confirmation หรือวันส่งปฏิทินจากชุดไฟล์ที่ตรวจ

## การเก็บไฟล์ใน Git

Current/archived proposals, README, migration explanation และ future source/tests/config/locks/evidence reports ไม่ถูก blanket-ignore `.gitignore` เป็น shared safety configuration ของ repository ทีมใหม่นี้

AGENT/AGENTS/CLAUDE, PLAN, historical guides, reference snapshots, migration manifest และ local sync helper ถูก ignore ตามนโยบาย internal working documents เดิม ยังคงเปิดได้ครบในเครื่อง การจัดย้ายไม่ได้ stage/commit/push ไฟล์ใด

Final reproduction ต้องใช้ source/config/artifact-access instructions ที่อยู่ใน repository จริง ไม่พึ่งไฟล์ local-only ถ้าต้องการส่งต่อ PLAN/กติกาให้ทีมผ่าน Git ให้เปลี่ยนนโยบายเฉพาะไฟล์เมื่อผู้ใช้สั่ง โดยตรวจข้อมูลภายในก่อน
