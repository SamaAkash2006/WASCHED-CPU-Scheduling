import random, statistics
from collections import deque

def generate_workload(n,kind='mixed',arrival='batch',seed=42):
 r=random.Random(seed); jobs=[]; t=0
 for i in range(n):
  if kind=='short_dominant': b=r.randint(1,5) if r.random()<.8 else r.randint(20,40)
  elif kind=='long_dominant': b=r.randint(20,60) if r.random()<.8 else r.randint(1,5)
  elif kind=='uniform': b=r.randint(7,9)
  elif kind=='highly_variable': b=min(60,max(1,int(r.lognormvariate(1.6,1))))
  else: b=r.randint(1,40)
  if arrival=='batch': a=0
  else:
   t+=r.randint(0,4) if arrival!='bursty' or i%5 else r.randint(3,8); a=t
  jobs.append({'pid':f'P{i+1}','arrival':a,'burst':b,'priority':r.randint(1,5)})
 return jobs

def workload_features(jobs):
 b=[p['burst'] for p in jobs]; mean=sum(b)/len(b); sd=statistics.pstdev(b) if len(b)>1 else 0; med=sorted(b)[len(b)//2]
 return {'count':len(jobs),'mean_burst':round(mean,3),'cv':round(sd/mean if mean else 0,3),'tail_ratio':round(max(b)/max(1,med),3),'short_fraction':round(sum(x<=5 for x in b)/len(b),3),'batch_fraction':round(sum(p['arrival']==0 for p in jobs)/len(jobs),3),'arrival_span':max(p['arrival'] for p in jobs)-min(p['arrival'] for p in jobs)}

def _sim(jobs,policy,q):
 ps={p['pid']:dict(p,rem=p['burst'],first=None,done=None) for p in jobs}; t=done=sw=0; last=None; gantt=[]; ready=[]; rq=deque(); arrived=set(); n=len(ps)
 while done<n:
  new=sorted((p for p in ps.values() if p['arrival']<=t and p['pid'] not in arrived),key=lambda p:(p['arrival'],p['pid']))
  for p in new:
   arrived.add(p['pid']); (rq.append(p['pid']) if policy=='RR' else ready.append(p['pid']))
  if policy=='RR':
   while rq and ps[rq[0]]['rem']<=0: rq.popleft()
   if not rq:
    fut=[p['arrival'] for p in ps.values() if p['rem']>0 and p['arrival']>t]
    if not fut: break
    t=min(fut); continue
   pid=rq.popleft()
  else:
   ready=[x for x in ready if ps[x]['rem']>0]
   if not ready:
    fut=[p['arrival'] for p in ps.values() if p['rem']>0 and p['arrival']>t]
    if not fut: break
    t=min(fut); continue
   key={'FCFS':lambda x:(ps[x]['arrival'],x),'SJF':lambda x:(ps[x]['burst'],ps[x]['arrival']),'SRTF':lambda x:(ps[x]['rem'],ps[x]['arrival']),'Priority':lambda x:(ps[x]['priority'],ps[x]['arrival'])}[policy]
   pid=min(ready,key=key); ready.remove(pid)
  p=ps[pid]
  if p['first'] is None:p['first']=t
  if last is not None and last!=pid:sw+=1
  last=pid; run=min(q,p['rem']) if policy=='RR' else (1 if policy=='SRTF' else p['rem'])
  if policy=='SRTF':
   fut=[x['arrival'] for x in ps.values() if x['rem']>0 and x['arrival']>t]
   if fut:run=min(p['rem'],max(1,min(fut)-t))
  start=t;p['rem']-=run;t+=run
  if gantt and gantt[-1]['pid']==pid and gantt[-1]['end']==start:gantt[-1]['end']=t
  else:gantt.append({'pid':pid,'start':start,'end':t})
  if p['rem']<=0:p['done']=t;done+=1
  elif policy=='RR':rq.append(pid)
  elif policy=='SRTF':ready.append(pid)
 rows=[]
 for p in ps.values():
  tat=(p['done'] or t)-p['arrival']; rows.append({'pid':p['pid'],'arrival':p['arrival'],'burst':p['burst'],'priority':p['priority'],'waiting':max(0,tat-p['burst']),'turnaround':tat,'response':max(0,(p['first'] if p['first'] is not None else p['arrival'])-p['arrival']),'completion':p['done']})
 avg=lambda k:round(sum(x[k] for x in rows)/len(rows),2); slow=[x['turnaround']/max(1,x['burst']) for x in rows]; fairness=sum(slow)**2/(len(slow)*sum(x*x for x in slow)) if slow else 1; span=max((p['done'] or 0) for p in ps.values())-min(p['arrival'] for p in ps.values())
 return {'algorithm':policy,'avg_waiting':avg('waiting'),'avg_turnaround':avg('turnaround'),'avg_response':avg('response'),'context_switches':sw,'throughput':round(len(rows)/max(1,span),4),'fairness':round(fairness,3),'gantt':gantt,'processes':rows}
def run_all(jobs,quantum=4,ml_choice='SRTF'):
 out=[_sim(jobs,p,quantum) for p in ['FCFS','SJF','SRTF','RR','Priority']]; x=_sim(jobs,ml_choice,quantum);x['algorithm']='ML-ADAPTIVE';x['selected_policy']=ml_choice;return out+[x]
