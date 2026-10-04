# งานเก่าและเครื่องมือทดลองที่ไม่ต้องส่ง

ย้ายมารวมวันที่ 4 ตุลาคม 2026 หลังอาจารย์ยกเลิกข้อ 3.c, กราฟและ error bars
รวมถึงไม่ต้องส่ง PDF เก็บข้อมูลเดิมไว้ครบสำหรับอ้างอิง ไม่ต้องทำให้ผลผ่าน
เกณฑ์ CI เดิมเพื่อส่งงาน ข้อ 2.a และข้ออื่นยังอยู่ตาม [README ปัจจุบัน](../README.md)

โฟลเดอร์นี้รวมข้อมูล CSV/JSON, กราฟ, บันทึกตรวจ, แผนทดลองเดิม,
LaTeX เก่า และสคริปต์ทดลอง/วิเคราะห์พร้อมชุดตรวจเครื่องมือเหล่านั้น
ข้อความและคำสั่งในบันทึกเก่าอาจใช้ตำแหน่งก่อนย้าย ให้ใช้คำสั่งด้านล่าง
จาก repository root เมื่อต้องการเรียกเครื่องมือเก็บงานเก่า:

```powershell
python -m unittest project2._archive.test_convergence -v
python -m project2._archive.run_experiments --help
python -m project2._archive.run_tracking_experiments --help
python -m project2._archive.convergence_check --help
python -m project2._archive.plot_stability --help
python -m project2._archive.analyze --help
python -m project2._archive.review_summary
```

กำหนด input/output ให้ชี้มายัง `project2/_archive/` ตามต้องการ
`review_summary` ใช้ข้อมูลในโฟลเดอร์นี้โดยตรง ไม่ต้องย้ายไฟล์กลับไปที่เดิม
ผลทางสถิติเดิมไม่ได้เปลี่ยนหลังย้าย

## Historical implementation and experiments (October 3, 2026)

The section below records previous experiments and optional reproduction
commands. Its references to an incomplete experimental requirement and
suggested additional trials predate the removal of question 3.c.

The new stability work uses a prespecified practical-equivalence check,
not a claim that a flat-looking graph proves convergence. See
`CONVERGENCE_PLAN.md` and `STABILITY_RESULTS.md` for protocols, margins,
completed trial counts and the latest conclusions. Normal gameplay data
and continuous tracking experiments are kept in separate folders.

The instructor no longer requires a PDF report, as confirmed by the user.
The PDF, PDF builder and obsolete submission archive have been removed.
Submit `bayesfilter.py` and optionally `pacmanagent.py`; the original archive
format below is retained until the instructor gives different packaging
instructions. PDF page limits, template formatting and report compilation
instructions no longer apply.

The filter and optional belief-only controller are implemented. Historical
`report.tex` and `template-project2.tex` are retained as reference notes;
they are not required for execution or submission. Keep experiment data,
analysis scripts and model notes for verification and explanation.

Imports now support both standalone project folders and repository packages.
From this folder, `python run.py` and `python run_experiments.py` no longer
need PYTHONPATH. From the root, `python -m project2.run` also locates the
bundled layouts. Standalone execution is tested by copying the submission
files and engine outside the repository. The protected filter methods remain
unchanged. Install analysis dependencies from `../requirements.txt` in your
chosen environment; no packages were installed into the existing environment.

Validation: model/filter tests and PEP8 checks pass for both submission
files and the experiment/analysis scripts. Baseline data are in `review_out/`
(180 complete 200-step trials); figures and 95% confidence intervals are in
`review_figs/`. Follow-up data are in `convergence_out/` (20 complete
1,000-step trials). Residual entropy drift remains, so convergence and full
completion of the experimental requirement are not claimed. See `REVIEW.md`.

PowerShell, from the repository root, using the existing conda environment:

```powershell
& 'C:\Users\Lenovo\miniconda3\envs\tf-env\python.exe' -m project2.check_models
& 'C:\Users\Lenovo\miniconda3\envs\tf-env\python.exe' -m pycodestyle project2/bayesfilter.py project2/pacmanagent.py
$env:PYTHONPATH = (Get-Location).Path
$env:OPENBLAS_NUM_THREADS = '1'
Set-Location project2
& 'C:\Users\Lenovo\miniconda3\envs\tf-env\python.exe' run_experiments.py --trials 30 --steps 1000 --variances 0.25 1 4 --out next_experiments
& 'C:\Users\Lenovo\miniconda3\envs\tf-env\python.exe' analyze.py --data next_experiments --burnin 500 --figs next_figs
```

The analysis needs NumPy, SciPy, pandas, matplotlib, python-dateutil and six.
The current tf-env lacks the last two; the existing bundled copies were
loaded for this run using the command documented in `REVIEW.md`. New trials
write a JSON sidecar recording actual length, ending reason, ghost count and
actual sensor variance. Keep different ghost counts in separate analysis
folders. The 30-trial/1,000-step suggestion is not a convergence guarantee.

