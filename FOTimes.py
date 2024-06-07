from Solver import Solver
from Heuristic.Greedy import Greedy
from Heuristic.FixOpt import FixOpt
import random as r
import json
from IPython.display import clear_output
import time

##############################################################################
# Script used to test the heuristic performance with different maximum times #
##############################################################################

r.seed(10)
  
with open('credentials.txt') as f: 
    data = f.read() 
options = json.loads(data)

def generate_instance(N_cardinality, M_cardinality,
                      min_execution_time = 1,max_execution_time = 10,
                      min_setup_time = 1,max_setup_time = 3):
    
    P = {}
    S = {}
    
    N = range(1, N_cardinality+1)
    M = range(1, M_cardinality+1)
    
    for i in M:
        for j in N:
            P[i,j] = r.randint(min_execution_time, max_execution_time)
            
    for i in M:
        for j in N:
            for k in N:
                S[i,j,k] = r.randint(min_setup_time, max_setup_time)
    
    return P,S

N_and_M = (40, 10)
N_cardinality, M_cardinality = N_and_M

N = range(1, N_cardinality+1)
M = range(1, M_cardinality+1)
N0 = [i for i in N]
N0.insert(0,0)

maximum_times_heuristic = [60, 120, 180, 240, 300, 600, 900, 1000, 1100, 1200, 1300, 1400]
maximum_makespan = 10

results_FO = {}

P_dict, S_dict = generate_instance(N_cardinality=N_cardinality,M_cardinality=M_cardinality)

t = time.time()

s = Solver(execution_times = P_dict, setup_times = S_dict) # Find the exact solution 
decision_variables,completion_times,maximum_makespan,assignments = s.solve(options=options)
results_IP = (round(maximum_makespan), time.time() - t, s.gap)

for t_max in maximum_times_heuristic: # Use the heuristic for every maximum time in the list
    t = time.time()

    greedy = Greedy(execution_times=P_dict, setup_times=S_dict)
    solution = greedy.solve()
    m = FixOpt(initial_solution=solution, setup_times=S_dict, execution_times=P_dict, N=N, M=M, N0=N0, 
           subproblem_size_adjust_rate=0.1, t_max = t_max, subproblem_runtime_limit=10, subproblem_size=5)
    solution, makespan = m.solve()
    results_FO[t_max] = (round(makespan), time.time() - t, ((maximum_makespan - makespan)/maximum_makespan)*100)

    clear_output(wait=True)

print('Integer Programming:')
print(f'Makespan: {results_IP[0]} with gap {results_IP[2]}, Time: {results_IP[1]}s')

print('Fix-and-Optimize Heuristic:')
for result, v in results_FO.items():
    print(f'T_max: {result}, Makespan: {v[0]} with gap {v[2]}, Time: {v[1]}s')