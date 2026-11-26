from sklearn.tree import DecisionTreeClassifier
import numpy as np

def _label(row):
 cv,tail,short,batch,mean=row
 if batch>=.9 and cv<.8:return 'RR'
 if short>=.45 or (cv>=.8 and tail>=3):return 'SJF'
 if batch<.9 and cv>=.15:return 'SRTF'
 return 'FCFS'
def train_model():
 r=np.random.default_rng(2026); X=[];y=[]
 for _ in range(1800):
  row=[float(r.uniform(0,1.8)),float(r.uniform(1,10)),float(r.uniform(0,1)),float(r.uniform(0,1)),float(r.uniform(1,45))];X.append(row);y.append(_label(row))
 m=DecisionTreeClassifier(max_depth=5,random_state=2026);m.fit(np.array(X),np.array(y));return m
def predict_policy(model,f):
 x=np.array([[f['cv'],f['tail_ratio'],f['short_fraction'],f['batch_fraction'],f['mean_burst']]]);p=model.predict_proba(x)[0];i=int(np.argmax(p));return str(model.classes_[i]),float(p[i])
