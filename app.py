from flask import Flask, render_template, request, jsonify
from scheduler import run_all, generate_workload, workload_features
from ml_model import train_model, predict_policy
import csv, io
app = Flask(__name__)
MODEL = train_model()

def parse_custom_processes(raw):
    if not isinstance(raw, str) or not raw.strip(): raise ValueError('Enter at least two processes.')
    processes, seen = [], set()
    for line_no, row in enumerate(csv.reader(io.StringIO(raw.strip())), 1):
        row = [c.strip() for c in row]
        if not row or all(not c for c in row): continue
        if not processes and row[0].lower() in {'pid','process','process_id'}: continue
        if len(row) not in (3,4): raise ValueError(f'Line {line_no}: use PID, arrival, burst, and optional priority.')
        pid=row[0]
        if not pid or pid in seen: raise ValueError(f'Line {line_no}: process ID is empty or duplicated.')
        try: arrival, burst = int(row[1]), int(row[2]); priority=int(row[3]) if len(row)==4 and row[3] else 3
        except ValueError: raise ValueError(f'Line {line_no}: values must be whole numbers.')
        if arrival<0 or burst<1 or not 1<=priority<=5: raise ValueError(f'Line {line_no}: arrival must be >=0, burst >=1, priority 1–5.')
        processes.append({'pid':pid,'arrival':arrival,'burst':burst,'priority':priority}); seen.add(pid)
    if not 2<=len(processes)<=100: raise ValueError('Please enter between 2 and 100 processes.')
    return processes

@app.route('/')
def index(): return render_template('index.html')
@app.route('/api/run', methods=['POST'])
def run():
    data=request.get_json(force=True)
    try:
        kind=data.get('workload','mixed')
        if kind=='custom': processes=parse_custom_processes(data.get('custom_processes',''))
        else: processes=generate_workload(max(5,min(100,int(data.get('count',20)))),kind,data.get('arrival','batch'),int(data.get('seed',42)))
        quantum=max(1,min(10,int(data.get('quantum',4))))
        features=workload_features(processes)
    except (ValueError,TypeError) as e: return jsonify({'error':str(e)}),400
    choice,confidence=predict_policy(MODEL,features)
    return jsonify({'processes':processes,'features':features,'ml':{'choice':choice,'confidence':round(confidence,3)},'results':run_all(processes,quantum,choice),'note':'Simulation only; no OS kernel is modified.'})
if __name__=='__main__': app.run(debug=True)
