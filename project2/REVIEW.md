# ผลตรวจ Project 2 — 2 ตุลาคม 2026

> อัปเดต 3 ตุลาคม 2026: อาจารย์ไม่ต้องการ PDF แล้วตามที่ผู้ใช้แจ้ง
> ข้อความเรื่องการสร้าง/ส่ง report.pdf และกฎรูปแบบรายงานด้านล่างเป็นข้อมูลเก่า
> ให้ดูผลตรวจล่าสุดใน ../PROJECT_REVIEW.md และข้อกำหนดปัจจุบันใน README.md
> เก็บแผนและผลทดลองเดิมไว้เป็นหลักฐาน ไม่ใช้สถานะเก่าเพื่อสรุปความพร้อมส่ง

ผู้ใช้ยืนยันว่าอาจารย์อนุญาตสมาชิก 3 คนแล้ว รายงานใส่ชื่อและรหัสตามลำดับ:
Pattraporn Joomnok — B6644932, Chayapha Leksungnoen — B6735173,
Arrirat Mungyotklang — B6739485 ข้อสงสัยเรื่องจำนวนสมาชิกในบันทึกเก่าถือว่าคลี่คลายแล้ว

## อัปเดตหลังแก้ไขตามคำขอ

- แก้ PEP8 ครบแล้ว: bayesfilter.py, pacmanagent.py, run_experiments.py,
  analyze.py และ check_models.py ผ่านทั้งหมด
- เพิ่มการทดสอบ filter ที่คำนวณคำตอบด้วยมือ รวมเป็น 6 tests และผ่านทั้งหมด
- สคริปต์ทดลองสร้างโฟลเดอร์เอง บันทึก JSON metadata จำนวนขั้น/เหตุผลจบ
  ใส่จำนวนผีในชื่อไฟล์เมื่อมากกว่าหนึ่ง และตรวจค่าพารามิเตอร์
- สคริปต์วิเคราะห์ตรวจโฟลเดอร์ว่าง/ไม่มีข้อมูลหลัง burn-in ป้องกันการ
  ผสมจำนวนผี และไม่ตีความ trial เดียวว่า CI เป็นศูนย์
- จัดทำ report.tex ตามลำดับคำถามเดิมและคง Leave empty; report.pdf
  ฉบับร่างภาษาอังกฤษ 4 หน้า ใส่รหัส B6644932, B6735173, B6739485
- PDF สร้างด้วย ReportLab และตรวจหน้าจริง เนื่องจาก compiler ในแอป
  ล้มเหลวด้วย `Unable to find standard directories for platform`.
  จึงยังไม่ได้ยืนยันการคอมไพล์ต้นฉบับ LaTeX หรือความตรงของ typography
  กับ template ต้อง compile report.tex พร้อม review_figs ใน LaTeX เต็มระบบ
  ก่อนใช้เป็นรายงานส่งที่ตรง template ทุกด้าน
- รันเพิ่ม 20 trials สำหรับ confused บน large_filter_walls, variance 1/4,
  seeds 0–9 ครบ 1,000 ขั้นทุก trial เปรียบเทียบ t=750–999 กับ 500–749
  พบ entropy drift -0.148 ± 0.143 และ -0.167 ± 0.117 bits ตามลำดับ
  (paired 95% CI) จึงยังไม่อ้างว่าลู่เข้าแล้ว
- README และ models.md อัปเดตสถานะแล้ว เทมเพลตต้นฉบับไม่ถูกแก้

ส่วนด้านล่างเป็นบันทึกการตรวจครั้งแรกก่อนแก้ไข จุด PEP8 และรายงานว่าง
ที่กล่าวไว้ได้รับการแก้แล้ว ส่วน convergence ยังต้องพิจารณาก่อนส่งจริง

สถานะ: **ยังไม่ครบและยังไม่พร้อมส่ง** โค้ดหลักมีแล้วและผ่านการตรวจเบื้องต้น แต่รายงานฉบับสมบูรณ์ยังไม่มี ผลทดลองและกราฟที่สร้างในรอบตรวจนี้ต้องนำไปวิเคราะห์และใส่ในรายงานก่อนส่ง

## ผลตรวจที่รันได้

- ตรวจ syntax ด้วย Python 3.12 (`python -m compileall -q project2`): ผ่านทุกไฟล์
- พบ conda เดิม `C:\Users\Lenovo\miniconda3\envs\tf-env\python.exe` (Python 3.11.15) และใช้รันงานจริง ไม่ต้องติดตั้ง environment ใหม่
- `python -m project2.check_models`: ผ่าน 4 tests
- กรณีคำนวณด้วยมือเพิ่มเติม: posterior บนทางเดินสามช่อง, ผีหลายตัว, ผีถูกกิน และ fallback ของ impossible evidence ผ่านทั้งหมด
- เกมผี 3 ตัว: `large_filter_walls`, `afraid`, variance 1, seeds 0–1 ผ่านครบ 60 ขั้นต่อ trial และบันทึกผีครบ 3 ตัวในแต่ละขั้น (`review_multighost/`)
- โบนัส seed 0, ผีหนึ่งตัว, variance 1 ชนะทั้ง 6 คู่: large_filter confused/afraid/scared ใช้ 15/45/27 ขั้น คะแนน 685/655/673; large_filter_walls ใช้ 12/16/72 ขั้น คะแนน 688/684/628 (`review_bonus/`)
- PEP8 ของไฟล์ส่ง: `bayesfilter.py:322` พบ W292 (ไม่มี newline ท้ายไฟล์); `pacmanagent.py` ผ่าน
- PEP8 ของเครื่องมือ: `run_experiments.py:124` W292; `analyze.py:86` E124 และ `:169` W292; `check_models.py` ผ่าน
- conda เดิมขาด dateutil/six ที่ pandas และ matplotlib ต้องใช้ จึงเพิ่ม path ของแพ็กเกจที่มีอยู่แล้วใน runtime ของ Codex เฉพาะ process วิเคราะห์ โดยไม่ได้ติดตั้งหรือแก้ conda
- การตรวจรอบแรกใช้ Python คนละตัวและติด SciPy; หลังผู้ใช้แจ้งว่ามี environment เดิม จึงค้นพบ tf-env และรันต่อ ผล runtime ด้านบนแทนข้อสรุปเดิมที่ว่ารันไม่ได้
- ยังไม่ได้คอมไพล์รายงาน เพราะ template ยังว่าง

## ผลทดลองที่รันครบ

รัน 2 layouts × 3 ghost policies × variances 0.25, 1, 4 × 10 seeds (0–9) = **180 trials** ผีหนึ่งตัวต่อ trial ทุก trial มีข้อมูลครบ **200 ขั้น** ไม่มี trial สั้น ตัด 100 ขั้นแรกออกก่อนสรุป ค่าเฉลี่ยคำนวณจากค่าเฉลี่ยช่วงท้ายของแต่ละ trial และ error bars เป็น 95% Student-t confidence interval ข้าม 10 trials

ผลที่ variance เริ่มต้น 1 (ค่าเฉลี่ย ± 95% CI):

| Layout | Ghost | Entropy (bits) | Expected Manhattan error |
|---|---|---:|---:|
| large_filter | confused | 3.063 ± 0.313 | 3.248 ± 0.531 |
| large_filter | afraid | 2.129 ± 0.309 | 2.229 ± 0.455 |
| large_filter | scared | 0.939 ± 0.076 | 0.838 ± 0.085 |
| large_filter_walls | confused | 2.462 ± 0.397 | 2.473 ± 0.601 |
| large_filter_walls | afraid | 2.033 ± 0.242 | 1.886 ± 0.295 |
| large_filter_walls | scared | 1.009 ± 0.069 | 0.894 ± 0.074 |

- ในชุดนี้ scared มี entropy และ error ต่ำสุดทั้งสองแผนที่; confused สูงสุด ความเอนเอียงหนีที่มากขึ้นช่วยจำกัดบริเวณที่ผีอยู่ แต่ไม่ใช่หลักประกันสำหรับทุกแผนที่หรือนโยบาย Pacman
- เพิ่ม variance 0.25 → 1 → 4 แล้วค่าเฉลี่ย entropy และ error เพิ่มขึ้นทุกคู่ layout/policy
- แผนที่มีกำแพงมีค่าเฉลี่ยต่ำกว่าแผนที่แรกสำหรับ confused และ afraid แต่ scared สูงกว่าเล็กน้อย อย่าสรุปว่ากำแพงช่วยเสมอ หรืออ้างความแตกต่างทุกคู่มีนัยสำคัญจากค่าเฉลี่ยอย่างเดียว
- **ยังไม่รับรองการลู่เข้า** เปรียบเทียบช่วง t=100–149 กับ t=150–199 พบ entropy ของ confused ใน large_filter_walls เปลี่ยน -0.428 ± 0.288 bits ที่ variance 1 และ -0.262 ± 0.195 bits ที่ variance 4 (paired 95% CI ของความต่างข้าม trials) ช่วงท้ายยังมี drift ที่ควรตรวจต่อ ข้อมูลนี้เป็น diagnostic เชิงสำรวจ ไม่ใช่การพิสูจน์ convergence
- ควรเพิ่มความยาว เช่น 500–1000 ขั้น และเพิ่ม seeds เช่น 30 ต่อเงื่อนไข โดยตัดสินความเพียงพอจาก drift, ความกว้าง CI และความคงที่เมื่อเพิ่มระยะเวลา ไม่ใช่เลือกตัวเลขแล้วถือว่าผ่านทันที

ไฟล์ผล: `review_out/*.csv`, `review_figs/summary.csv`, `trial_lengths.csv`, `late_window_drift.csv` และกราฟ `curves_default_variance.png`, `steady_state_bars.png`, `variance_sweep.png` สคริปต์ `review_summary.py` ตรวจความยาว trial และ late-window drift ทำซ้ำได้

## ความครบตามโจทย์

| ข้อ | สถานะ | สิ่งที่พบ |
|---|---|---|
| 1.a sensor model | มีร่าง | `report_parts/models.md` อธิบาย centered Binomial, support และ variance จริง |
| 1.b transition model | มีร่าง | ใช้พารามิเตอร์เดียว น้ำหนัก 1, 2, 8 ตามนโยบายผี |
| 2.a Bayes filter | ผ่านการตรวจเบื้องต้น | prediction, correction, normalization; ผ่านโมเดล กรณีเล็ก และเกมหลายผี |
| 3.a uncertainty | มีโค้ด | entropy หน่วย bits ใน `_record_metrics` |
| 3.b quality | มีโค้ด | expected Manhattan distance จาก belief ไป ground truth |
| 3.c experiments | รันผลในรอบตรวจ | CSV ใน review_out และกราฟ/95% CI ใน review_figs; ต้องวิเคราะห์และใส่รายงาน |
| 3.d ghost parameter discussion | มีทฤษฎี ยังขาดผลประกอบ | ร่างใน `models.md` ยังต้องเชื่อมกับข้อมูลจริงทั้งสอง layouts |
| 3.e sensor variance discussion | ยังขาด | ต้องรันหลาย variance แล้ววิเคราะห์ผล |
| 3.f controller explanation | ยังขาดคำตอบรายงาน | โค้ดไล่ belief ที่ใกล้ที่สุดมีแล้ว แต่ต้องอธิบายหลักการและข้อจำกัด |
| 3.g bonus | ผ่าน smoke test 6 คู่ที่ seed 0 | ใช้ตำแหน่ง Pacman, legal actions และ belief; ยังไม่ได้วัดอัตราชนะหลาย seeds |
| report.pdf | ไม่มี | template ยังว่างและชื่อ/รหัสเป็นตัวอย่าง |
| archive .tar.gz | ไม่มี | ต้องมี `report.pdf`, `bayesfilter.py` และ optional `pacmanagent.py` |

## จุดที่ต้องแก้หรือยืนยันก่อนส่ง

1. **เติมรายงานตาม template ให้ครบ** ภาษาอังกฤษหรือฝรั่งเศส ไม่เกิน 5 หน้า คงส่วน Leave empty และใส่ชื่อ/รหัสจริง; ร่างโมเดลอย่างเดียวไม่ใช่รายงานฉบับส่ง
2. **ยืนยันความยาวของ trial** ใน `run_experiments.py:82` การหยุดหลัง `steps` เป็นเพียงเพดาน เกมยังจบได้เมื่อผีทั้งหมดถูกกิน การเดินไปช่องที่ห่างผีอย่างน้อย 2 ไม่รับประกันว่าจะปลอดภัย เพราะผีเดินเข้าหาได้ในตาถัดไปและเกมมีเกณฑ์ชนของตัวเอง ต้องบันทึกจำนวนขั้นจริงและเหตุผลจบของทุก trial ตรวจจำนวน trial ที่เหลือหลัง burn-in และระบุวิธีจัดการ trial สั้น การเฉลี่ยเฉพาะ trial ที่รอดอาจทำให้เกิด survivor bias
3. **แสดงหลักฐานการลู่เข้า** ค่าเริ่มต้น 30 trials, 200 steps และ burn-in 100 ยังไม่ใช่หลักฐานว่าผลนิ่ง ควรเปรียบเทียบหน้าต่างช่วงท้ายและทดลองเพิ่มระยะเวลา/จำนวน seed ตรวจจำนวน samples ต่อจุดเวลาและรายงานวิธีตัดสินความเพียงพอ
4. **เปิดเผยนโยบาย Pacman ในการทดลอง** `WanderingPacman` ใช้ตำแหน่งจริงของผีเพื่อหลบ แม้ filter ไม่ใช้ ground truth แต่การเดินส่งผลต่อข้อมูล sensor และผลทดลอง จึงต้องอธิบายให้ชัดและไม่ใช้ผลนี้อ้างเป็นผลโบนัสของ controller ที่ใช้ belief เท่านั้น
5. **เพิ่มการตรวจ filter และโบนัส** `check_models.py` มีสี่ tests สำหรับโมเดล ยังไม่มี tests ของ `_get_updated_belief` เช่นเทียบกับผลคำนวณบนแผนที่เล็ก, ผีหลายตัว, ผีถูกกิน, Pacman เปลี่ยนตำแหน่ง และ zero-likelihood fallback ตรวจ sum=1, nonnegative, zero mass บนกำแพงด้วย
6. **ขยายการทดสอบโบนัส** greedy Manhattan distance อาจวนหรือเลือกทางที่ระยะดูใกล้แต่ติดกำแพง รอบนี้ชนะทั้งสองแผนที่และสามชนิดผีที่ seed 0 แล้ว แต่ควรทดสอบหลาย seeds พร้อมเพดานเวลาและรายงานอัตราสำเร็จ
7. **แก้ PEP8 ที่พบ** เพิ่ม newline ท้าย bayesfilter.py และแก้ indentation/newline ของเครื่องมือทดลองตามรายการข้างต้น; บันทึก models.md ที่บอกว่าเคยผ่านไม่ใช่ผลของเวอร์ชันปัจจุบัน
8. **แก้เอกสารที่ล้าสมัย** ท้าย `report_parts/models.md` ยังระบุว่า filter, metrics, controller ไม่เสร็จ ทั้งที่ปัจจุบันมีโค้ดแล้ว `WORK_PLAN.md` เป็นแผนสำหรับ 3 คน แต่ README หลักกำหนดสูงสุด 2 คน ต้องยึดข้อกำหนดที่ผู้สอนอนุญาต กำหนดส่งใน README เป็นปี 2025 จึงไม่ใช่กำหนดส่งปัจจุบันที่ยืนยันแล้ว
9. **เพิ่มวิธีตั้งสภาพแวดล้อมและคำสั่งสำหรับ Windows** ต้องมี NumPy, SciPy, pandas, matplotlib และ pycodestyle; คำสั่ง `PYTHONPATH=.. python ...` ใน docstring เป็นรูปแบบ shell ฝั่ง Unix ใช้ตรง ๆ ใน PowerShell ไม่ได้

## คำสั่งรันเมื่อ dependencies พร้อม (PowerShell)

จาก root ของ repository ใช้ conda เดิม:

```powershell
& 'C:\Users\Lenovo\miniconda3\envs\tf-env\python.exe' -m project2.check_models
& 'C:\Users\Lenovo\miniconda3\envs\tf-env\python.exe' -m pycodestyle project2/bayesfilter.py project2/pacmanagent.py
$env:PYTHONPATH = (Get-Location).Path
Set-Location project2
& 'C:\Users\Lenovo\miniconda3\envs\tf-env\python.exe' run_experiments.py --trials 30 --steps 200 --variances 0.25 1 4 --out new_experiments
& 'C:\Users\Lenovo\miniconda3\envs\tf-env\python.exe' analyze.py --data new_experiments --burnin 100 --figs new_figs
```

คำสั่ง analyze.py ตรง ๆ ยังต้องมี dateutil/six ใน environment; รอบนี้ใช้คำสั่งด้านล่างจาก repository root เพื่อโหลดแพ็กเกจที่มีอยู่แล้วโดยไม่ติดตั้งเพิ่ม:

```powershell
$env:MPLCONFIGDIR = 'D:\GitHub\ai-aofphy\project2\review_figs\mplconfig'
& 'C:\Users\Lenovo\miniconda3\envs\tf-env\python.exe' -c "import sys,runpy; sys.path.append(r'C:\Users\Lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\Lib\site-packages'); sys.argv=['analyze.py','--data','project2/review_out','--burnin','100','--figs','project2/review_figs']; runpy.run_path('project2/analyze.py',run_name='__main__')"
```

ตัวเลขนี้เป็นชุดเริ่มต้น ไม่ใช่การรับรองว่าลู่เข้าแล้ว ต้องตรวจจำนวนขั้นจริงก่อนใช้ summary และเพิ่มการทดลองตามหลักฐาน รอบตรวจนี้ใช้ 10 trials ต่อเงื่อนไข ควรแยกชุดทดสอบหลายผีออกเป็น output อีกโฟลเดอร์ เพราะชื่อ CSV ปัจจุบันไม่บันทึก `nghosts` และอาจเขียนทับผลเดิม

## ขอบเขตการตรวจ

รอบนี้อ่านข้อกำหนด โค้ด เครื่องมือทดลอง ร่างรายงาน และ template พร้อมรันทดสอบจริงด้วย conda เดิม ไม่ได้แก้ implementation ผลใน review_out, review_multighost และ review_bonus เป็นข้อมูลจากเกมจริง
