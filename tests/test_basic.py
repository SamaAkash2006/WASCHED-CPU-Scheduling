import unittest
from scheduler import generate_workload, workload_features, run_all
from app import app, parse_custom_processes
class Tests(unittest.TestCase):
 def test_seed(self): self.assertEqual(generate_workload(8,seed=7),generate_workload(8,seed=7))
 def test_custom_parser(self): self.assertEqual(len(parse_custom_processes('PID,Arrival,Burst,Priority\nP1,0,7,2\nP2,2,4,1')),2)
 def test_custom_api(self): self.assertEqual(app.test_client().post('/api/run',json={'workload':'custom','custom_processes':'P1,0,5,2\nP2,1,3,1'}).status_code,200)
 def test_invalid_custom(self): self.assertEqual(app.test_client().post('/api/run',json={'workload':'custom','custom_processes':'P1,-1,0,8\nP2,0,2,2'}).status_code,400)
 def test_all_policies(self): self.assertEqual(len(run_all(generate_workload(8))),6)
if __name__=='__main__': unittest.main()
