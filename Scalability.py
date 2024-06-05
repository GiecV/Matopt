from Solver import Solver
from MPA.MPA import MPA
from Heuristic.Greedy import Greedy
from Heuristic.FixOpt import FixOpt
import random as r
import json
from IPython.display import clear_output
import time

##############################################################
# Script used for the scalability analysis of the algorithms #
##############################################################

r.seed(10) # Seed for reproducibility
  
with open('credentials.txt') as f: # Load the credentials for Gurobi
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

N_and_M = [(20, 2), (25, 5), (30, 7), (35, 9), (40, 10)]
maximum_times = [15, 40, 120, 600, 4000]
maximum_times_heuristic = [10, 30, 90, 300, 2500]
results_IP = {}
results_MP = {}
results_FO = {}

for i, (N_cardinality, M_cardinality) in enumerate(N_and_M):
    t = time.time()
    P_dict, S_dict = generate_instance(N_cardinality = N_cardinality, M_cardinality = M_cardinality,
                                       min_execution_time = 1, max_execution_time = 100,
                                       min_setup_time = 1, max_setup_time = 100) # Generate the instance

    N = range(1, N_cardinality+1) # Create the sets N, M, N0
    M = range(1, M_cardinality+1)
    N0 = [i for i in N]
    N0.insert(0,0)

    s = Solver(execution_times = P_dict, setup_times = S_dict) # Solve using the IP solver
    decision_variables,completion_times,maximum_makespan,assignments = s.solve(options=options)
    results_IP[(N_cardinality, M_cardinality)] = (round(maximum_makespan), time.time() - t, s.gap)

    t = time.time()

    s = MPA(execution_times = P_dict, setup_times = S_dict, t_max=maximum_times[i]) # Solve using the MP solver
    decision_variables,maximum_makespan = s.solve(options=options)
    results_MP[(N_cardinality, M_cardinality)] = (round(maximum_makespan), time.time() - t, s.gap)

    t = time.time()

    greedy = Greedy(execution_times=P_dict, setup_times=S_dict) # Find the initial solution 
    solution = greedy.solve()
    m = FixOpt(initial_solution=solution, setup_times=S_dict,execution_times=P_dict, N=N, M=M, N0=N0, # Solve using the FO heuristic
           subproblem_size_adjust_rate=0.1, t_max = maximum_times_heuristic[i], subproblem_runtime_limit=10, subproblem_size=5)
    solution, makespan = m.solve()
    results_FO[(N_cardinality, M_cardinality)] = (round(makespan), time.time() - t, ((maximum_makespan - makespan)/maximum_makespan)*100)

    clear_output(wait=True)

print('Integer Programming:')
for result, v in results_IP.items():
    print(f'N: {result[0]}, M: {result[1]}, Makespan: {v[0]} with gap {v[2]}, Time: {v[1]}s')
print('Mathematical Programming:')
for result, v in results_MP.items():
    print(f'N: {result[0]}, M: {result[1]}, Makespan: {v[0]} with gap {v[2]}, Time: {v[1]}s')
print('Fix-and-Optimize Heuristic:')
for result, v in results_FO.items():
    print(f'N: {result[0]}, M: {result[1]}, Makespan: {v[0]} with gap {v[2]}, Time: {v[1]}s')