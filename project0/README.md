# Project 0

## Deliverables

You are requested to deliver
- A `bfs.py` file containing your implementation of the BFS algorithm, based on the `pacmanagent.py` template.
- A `astar.py` file containing your implementation of A\* algorithm, based on the `pacmanagent.py` template.

## Instructions

Use the files in the `project0` directory of this repository; no separate archive is required. In this first part of the project, only food dots, capsules and Pacman are in the maze. Your task is to design an intelligent agent based on search algorithms (see [Lecture 2]) for **maximizing** the score. You are asked to implement the **breadth-first search (BFS)** and **A\*** algorithms. We recommend to implement them in this order. It is mandatory to use only the [API](..#api) to retrieve game information.

To help you, we provide an implementation of the DFS algorithm in the `dfs.py` file. However, the `key` function is not finished. Once you have activated your Pacman environment (see [installation](..#installation)), you can test the DFS algorithm using the following commands:
```console
$ python run.py --agentfile dfs.py  --layout medium
```
If you want to test one of your implementation, just replace the script parameter `dfs` by the name (without the extension) of the agent file you want to test. Refer to the [usage section](..#usage) for more details about the options.

## Evaluation

Each of your agents will be evaluated against new mazes, some being designed to test common pitfalls. Passing the public tests does not mean that your code is correct. Do your own tests. Follows the criteria for this project:

- **BFS** (20%): If implemented correctly, your implementation should return the same score as ours and expand roughly the same amount of nodes.
- **A\*** (75%): A well-implemented A\* algorithm should return the optimal solution no matter the maze structure. The number of expanded nodes needed to find an optimal solution depends on the quality of the heuristic. For this algorithm, we check whether the returned solution is optimal for all mazes. The number of expanded nodes is also taken into account (the lower the better) in the grade.
- **Code style** (5%): No points are awarded if your code is not PEP-8 compliant.

## สิ่งที่ต้องส่ง (Deliverables)

คุณจะต้องส่งไฟล์ต่อไปนี้:
- ไฟล์ `bfs.py` ที่มีการติดตั้งอัลกอริทึม BFS ตามแม่แบบ `pacmanagent.py`
- ไฟล์ `astar.py` ที่มีการติดตั้งอัลกอริทึม A* ตามแม่แบบ `pacmanagent.py`

## คำแนะนำ (Instructions)

ใช้ไฟล์ในโฟลเดอร์ `project0` ของ repository นี้ได้เลย โดยไม่ต้องดาวน์โหลดหรือแตกไฟล์ ZIP เพิ่ม ในส่วนแรกของโครงการนี้ ภายในเขาวงกต (maze) จะมีเพียงจุดอาหาร (food dots), แคปซูล (capsules) และ Pacman เท่านั้น  
**ภารกิจของคุณ** คือ การออกแบบตัวแทนอัจฉริยะ (intelligent agent) โดยใช้อัลกอริทึมค้นหา (search algorithms) (ดู [Lecture 2])  
โดยมีเป้าหมายเพื่อ **เพิ่มคะแนน (score) ให้ได้มากที่สุด**

คุณจะต้องติดตั้งอัลกอริทึม:
- **Breadth-First Search (BFS)**
- **A\* Search**

เราแนะนำให้คุณเริ่มจาก BFS ก่อนแล้วจึงไปทำ A\*

**ข้อกำหนดสำคัญ**  
คุณจะต้องใช้งานเฉพาะ [API](..#api) เท่านั้นในการดึงข้อมูลสถานะของเกม  

เพื่อช่วยคุณเริ่มต้น เราได้เตรียมตัวอย่างการติดตั้งอัลกอริทึม DFS ไว้ในไฟล์ `dfs.py` แล้ว  
อย่างไรก็ตาม ฟังก์ชัน `key` ในไฟล์นี้ยังไม่เสร็จสมบูรณ์  

เมื่อคุณได้เปิดใช้งานสภาพแวดล้อม Pacman เรียบร้อยแล้ว (ดู [installation](..#installation))  
คุณสามารถทดสอบอัลกอริทึม DFS ได้ด้วยคำสั่งต่อไปนี้:

```console
$ python run.py --agentfile dfs.py --layout medium
```

**การประเมินผล (Evaluation)**

ตัวแทนของคุณแต่ละตัวจะถูกประเมินบนเขาวงกตใหม่ๆ ซึ่งบางแบบถูกออกแบบมาเพื่อทดสอบข้อผิดพลาดที่พบบ่อย
หมายเหตุ: ผ่านการทดสอบสาธารณะ (public tests) ไม่ได้แปลว่าโค้ดของคุณถูกต้องสมบูรณ์
คุณควรเขียนการทดสอบของคุณเองเพิ่มเติม

เกณฑ์การให้คะแนนมีดังนี้:
	•	BFS (20%)
ถ้าติดตั้งถูกต้อง ผลลัพธ์ควรได้คะแนนเท่ากับของเรา และขยายจำนวน node ใกล้เคียงกับของเรา
	•	A* (75%)
อัลกอริทึม A* ที่ติดตั้งดีควรสามารถหาผลลัพธ์ที่ดีที่สุด (optimal solution) ได้ในทุกเขาวงกต
จำนวน node ที่ถูกขยายขึ้นอยู่กับคุณภาพของ heuristic
สำหรับอัลกอริทึมนี้ เราจะตรวจสอบว่าเส้นทางที่ได้ เป็นเส้นทางที่ดีที่สุด สำหรับเขาวงกตทุกแบบหรือไม่
และจำนวน node ที่ขยายจะถูกนำมาพิจารณาด้วย (ยิ่งน้อยยิ่งดี)
	•	รูปแบบการเขียนโค้ด (Code style) (5%)
จะไม่ได้คะแนนถ้าโค้ดของคุณไม่เป็นไปตามมาตรฐาน PEP-8

## ไฟล์ที่ทำเสร็จแล้ว

- `bfs.py`: BFS ใช้คิว FIFO และบันทึกสถานะที่พบตั้งแต่เข้าคิว
  เพื่อหาเส้นทางชนะที่ใช้จำนวนก้าวน้อยที่สุด
- `astar.py`: A* ใช้ต้นทุน `จำนวนก้าว + 5 × จำนวนแคปซูลที่กิน`
  เพื่อให้ได้คะแนนสูงสุดในด่านที่ไม่มีผี
- `dfs.py`: เติมทั้ง `key` และ DFS ที่ยังเว้นว่างในไฟล์ต้นฉบับ
- `test_search.py`: ทดสอบเส้นทาง การคิดคะแนน สถานะปลายทาง
  อาหารที่เข้าไม่ถึง และเขาวงกตสุ่ม 20 แบบ โดยเทียบกับ UCS
- `requirements.txt`: ไลบรารีที่เกมต้องใช้

สถานะค้นหาประกอบด้วยตำแหน่ง Pacman อาหารที่เหลือ และแคปซูลที่เหลือ
ทุกการขยายสถานะเกมใช้ `generatePacmanSuccessors()` ตาม API ของโจทย์
A* คำนวณ heuristic จากระยะทางจริงตามช่องทางเดินไปอาหารที่ใกล้ที่สุด
รวมกับน้ำหนัก minimum spanning tree (MST) ของอาหารที่เหลือ
โดยอ่านกำแพงผ่าน `getWalls()` และเก็บผลไว้ใช้ซ้ำ
ค่านี้ไม่เกินต้นทุนจริง เพราะไม่รวมค่าแคปซูลและไม่บังคับให้เดินครบเส้นทางจริง
เมื่อพบเส้นทางที่ถูกกว่า A* จะเปิดสถานะนั้นให้ค้นหาใหม่

เมื่อชนะ รางวัลอาหารและโบนัสชนะคงที่ จึงลดต้นทุนข้างต้นแทนการเพิ่มคะแนนได้
BFS อาจได้คะแนนต่ำกว่า A* เพราะเส้นทางสั้นที่สุดอาจผ่านแคปซูล
DFS ไม่รับประกันจำนวนก้าวหรือคะแนนที่ดีที่สุด
ทั้งสามตัวแทนนี้ออกแบบสำหรับ Project 0 ที่ไม่มีผี

## วิธีเซ็ตอัพและรัน (Windows PowerShell)

ต้องมี Python 3 และ NumPy; ทดสอบโค้ดนี้ด้วย Python 3.12
หากยังไม่มีคำสั่ง `py` หรือ `python` ให้ติดตั้ง Python ก่อน
แล้วเปิด terminal ใหม่ หากเครื่องใช้คำสั่ง `python` ให้ใช้แทน `py` ในการสร้าง venv

```powershell
cd D:\GitHub\ai-aofphy\projects\project0
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

เรียก Python ใน venv โดยตรงได้โดยไม่ต้อง activate:

```powershell
# แสดงเกมเป็นหน้าต่าง (ต้องมี Tkinter)
.\.venv\Scripts\python.exe run.py --agentfile bfs.py --layout small
.\.venv\Scripts\python.exe run.py --agentfile astar.py --layout medium

# แสดงคะแนน เวลา และจำนวนโหนด โดยไม่เปิดหน้าต่าง
.\.venv\Scripts\python.exe run.py --agentfile astar.py --layout large --silentdisplay

# ทดสอบความถูกต้อง
.\.venv\Scripts\python.exe -m unittest -v test_search

# ตรวจ PEP-8 ของไฟล์ที่แก้/เพิ่ม
.\.venv\Scripts\python.exe -m pip install pycodestyle
.\.venv\Scripts\python.exe -m pycodestyle bfs.py astar.py dfs.py test_search.py
```

เลือกด่านได้เป็น `small`, `medium`, `large` และเปลี่ยน agent เป็น `dfs.py` ได้
สำหรับ Linux/macOS ใช้ `python3 -m venv .venv` แล้วเรียก `.venv/bin/python`
แทน `.\.venv\Scripts\python.exe` จากโฟลเดอร์ `projects/project0`
หากใช้ conda ตาม README หลัก ให้ activate environment ติดตั้ง NumPy
แล้วใช้ `python run.py ...` ได้เลย
ตัวเลือกที่ตรงกับ `run.py` ของ Project 0 คือ `--agentfile` และ `--silentdisplay`

## ผลการรันทดสอบ

ผลจากการรันแบบไม่เปิดหน้าต่างบน Python 3.12:

| Agent | ด่าน | คะแนน | โหนดที่ขยาย | เวลาคำนวณ (วินาที) |
| --- | --- | ---: | ---: | ---: |
| BFS | small | 497 | 23 | 0.002 |
| BFS | medium | 565 | 25,761 | 4.879 |
| BFS | large | 429 | 3,312 | 1.266 |
| A* | small | 500 | 11 | 0.002 |
| A* | medium | 568 | 282 | 0.069 |
| A* | large | 433 | 223 | 0.152 |

ทั้ง 6 ครั้งชนะเกม เวลาอาจเปลี่ยนตามเครื่องและแต่ละรอบ
การทดสอบอัตโนมัติผ่าน 5 กลุ่ม รวมเขาวงกตสุ่ม 20 แบบ
กรณีทดสอบแคปซูลยืนยันว่า A* เลือกเดิน 6 ก้าวโดยไม่กินแคปซูล
แทนเส้นทาง BFS 4 ก้าวที่กินแคปซูล จึงได้คะแนนมากกว่า
ผลนี้ไม่ได้แทนการประเมินด้วยด่านลับของผู้สอน
