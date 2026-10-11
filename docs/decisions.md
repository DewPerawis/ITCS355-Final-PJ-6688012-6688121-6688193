# Project decisions

## D001 — Proposal workflow

- Date: 11 ตุลาคม 2026
- Source/decision owner: ผู้ใช้ในแชต
- Clarification: Proposal เป็นการส่ง เริ่มทำได้หาก scope ตรงโจทย์ ไม่ต้องรอ approval แยก
- Action: ใช้ `SCOPE_REVIEW.md` ตรวจ required components และปรับ AGENT/PLAN/README ไม่ให้ approval เป็น gate เพิ่ม
- Boundary: ไม่อ้างว่าอาจารย์อนุมัติเป็นลายลักษณ์อักษรแล้ว เอกสาร brief ต้นฉบับยังเก็บเดิม

## D002 — Notebook ทีละขั้น

- Date: 11 ตุลาคม 2026
- Source/decision owner: ผู้ใช้ขอทำ Notebook ทีละนิด
- Action: เตรียม `../notebooks/00_project_start.ipynb` มี code cell เดียวสำหรับตรวจ environment ผู้ใช้รันแล้วส่ง output ก่อนเตรียมขั้นถัดไป
- Design: Notebook ทำ exploration/explanation และเรียก reusable logic ใน src; tests/pipeline ใช้ logic เดียวกัน
- Boundary: ยังไม่เลือก/ติดตั้ง project environment และไม่บันทึกผลผู้ช่วยเป็นผล kernel ของผู้ใช้

## D003 — Capstone scope และ Lab 5

- Date: 11 ตุลาคม 2026
- Analysis owner: ผู้ช่วย; หลักฐานคือ Proposal/project brief/Lab 5 ในเครื่อง
- Decision: proposed design ครอบคลุม required components จึงเริ่มทำต่อได้; Lab 5 Part A มี overlap มาก แต่ Capstone รวม Labs 1–4 ด้วย
- Boundary: ไม่เพิ่ม LLM/second-provider swap เป็น Capstone requirement อัตโนมัติ และไม่ตีความ design coverage เป็นผลผ่าน rubric

Team ownership confirmation, calendar deadlines, zero policy, split proportions, selected model และ cloud configuration ยังไม่ได้ตัดสินจากข้อมูลจริงในรอบนี้

## D004 — .gitignore เป็น local-only

- Date: 11 ตุลาคม 2026
- Source/decision owner: ผู้ใช้สั่งให้ `.gitignore` ignore ตัวเองและนำฉบับที่เคย commit ออกจาก tracking
- Verified before change: `.gitignore` ถูก track และพบ commit `f86fda2` (`init`); ยังไม่มีกฎ self-ignore และ staged changes ว่าง
- Action: เพิ่ม `/.gitignore`, ถอนเฉพาะ `.gitignore` จาก index, เก็บไฟล์จริงและกฎอื่นครบ และให้ผู้ใช้ commit staged deletion ตาม workflow
- Boundary: การถอน tracking เปลี่ยน index/commit ถัดไป; historical copies ยังอยู่ และไม่มีการ rewrite history หรือ force-push

## D005 — Language and student writing style

- Date: 11 October 2026
- Decision owner: the user in chat.
- Decision: use simple English for new project text, comments, docstrings, and instructions. Use clear student-style code while keeping correctness, readability, security, and useful checks.
- Correction: the user clarified that Notebook 00 must also be in English. The earlier Thai exception was a misunderstanding and is removed. Keep the saved output in its original language.
- Action: update `../AGENT.md` and sync `../AGENTS.md` and `../CLAUDE.md`. Keep old teacher documents and proposals as they are.

## D006 — Review the saved Notebook 00 result

- Date: 11 October 2026
- Evidence: the saved code cell in `../notebooks/00_project_start.ipynb`, execution count 1, with stdout and no error output.
- Result: Python 3.11.5 runs in Windows Anaconda base. The project folder was found. NumPy 2.3.5, pandas 2.1.4, scikit-learn 1.3.0, and matplotlib 3.7.2 metadata was found. MLflow and DVC were not installed in that kernel.
- Limit: metadata does not prove that imports or package compatibility pass. There are no model or cloud results from this cell.
- Action: review the saved result before editing. Keep its outputs, execution count, and kernel metadata. Change only Markdown and a comment; no rerun is needed for this edit.
- Next: prepare a separate project environment and check imports before the data audit. Installation has not started.

## D007 — Short English text and WSL

- Date: 11 October 2026
- Source: the user's correction in chat.
- Decision: all notebook text and comments use short, simple English. Keep notes brief and code correct.
- Environment: use WSL as in the labs. Ubuntu WSL 2, Python 3.12.3, and Docker commands are present. Ubuntu lacks ensurepip; the setup script installs venv support if needed.
- Action: shorten Notebook 00, preserve its earlier output, and prepare setup_wsl.sh and Notebook 01. Installation and notebook execution remain user steps.
- Timing: aim for useful progress before 21:00. Full Azure completion is not confirmed.
