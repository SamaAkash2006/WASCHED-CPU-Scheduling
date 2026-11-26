# WASCHED — Workload-Aware Adaptive CPU Scheduling

A student OS project prototype featuring FCFS, SJF, SRTF, Round Robin, Priority, synthetic workload generation, custom process input, a small decision-tree recommendation model, comparison metrics, charts, and a Gantt-style timeline.

## Run on Windows
1. Install Python 3.10+.
2. Extract the ZIP and open this folder in VS Code.
3. In the terminal run:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python app.py
   ```
4. Open http://127.0.0.1:5000 in your browser.

## Enter a custom workload
Choose **Enter my own processes** and enter one CSV process per line:

```text
PID,Arrival,Burst,Priority
P1,0,7,2
P2,2,4,1
P3,3,9,3
P4,5,5,2
```

Header is optional. Priority is optional and defaults to 3. Arrival time must be non-negative, burst time positive, priority from 1–5 (1 is highest), IDs unique, and 2–100 processes are accepted. All algorithms receive the same process list.

## ML model notes
The decision tree is trained on synthetic feature vectors with heuristic labels. Its confidence is not evidence that the selected policy is optimal. Validate on held-out workloads before drawing research conclusions. This app simulates scheduling and does not modify the operating-system kernel.
