from MPA.MPA import MPA
from Heuristic_iterations.FixOpt import FixOpt
from Heuristic_iterations.Greedy import Greedy
from Solver import Solver
import time
import random as r
from IPython.display import clear_output
import json

options = {}

# Uncomment if you are using a WLS Gurobi license
# and write your credentials in credentials.txt
with open('credentials.txt') as f: 
    data = f.read() 
options = json.loads(data)

def generate_instance(N_cardinality, M_cardinality,
                      min_execution_time = 1,max_execution_time = 100,
                      min_setup_time = 1,max_setup_time = 100):
    
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

def convert_keys_to_string(dictionary):
    return {str(key): value for key, value in dictionary.items()}

# N_cardinalities = [40,50]
# M_cardinalities = [2,5,10]

N_cardinalities = [10,20]
M_cardinalities = [2]

heuristic_runs = 5

results_MP = {}
results_FO = {}

for M_cardinality in M_cardinalities:
    for N_cardinality in N_cardinalities:

        t = time.time()

        N = range(1, N_cardinality+1)
        M = range(1, M_cardinality+1)
        N0 = [i for i in N]
        N0.insert(0,0)

        print(f"Running with N = {N_cardinality}, M = {M_cardinality}")

        results_MP[(N_cardinality, M_cardinality)] = {}
        results_FO[(N_cardinality, M_cardinality)] = {}

        P_dict, S_dict = generate_instance(N_cardinality=N_cardinality,M_cardinality=M_cardinality,
                                   min_execution_time = 1, max_execution_time = 100,
                                   min_setup_time = 1, max_setup_time = 100)
        
        s = Solver(execution_times = P_dict, setup_times = S_dict)
        s = MPA(execution_times = P_dict, setup_times = S_dict, t_max=1800) #  max_time = 1800
        decision_variables,maximum_makespan = s.solve(options=options)

        results_MP[(N_cardinality, M_cardinality)] = {'makespan': round(maximum_makespan), 'time': time.time() - t, 'gap': 0}

        for run in range(heuristic_runs):

            t = time.time()

            print(f"Running iteration {run} with N={N_cardinality}, M={M_cardinality}")
            
            greedy = Greedy(execution_times=P_dict, setup_times=S_dict)
            solution = greedy.solve()
            m = FixOpt(initial_solution=solution, setup_times=S_dict,execution_times=P_dict, N=N, M=M, N0=N0, 
            subproblem_size_adjust_rate=0.1, iterations = 20, subproblem_runtime_limit=10, subproblem_size=5,
            WLS_license = True) # In case you are using a WLS Gurobi license
            solution, makespan = m.solve()

            results_FO[(N_cardinality, M_cardinality)][run] = {'makespan': round(makespan), 'time': time.time() - t, 'gap': ((maximum_makespan - makespan)/maximum_makespan)*100}

results_MP_str_keys = convert_keys_to_string(results_MP)
results_FO_str_keys = convert_keys_to_string(results_FO)

with open('Scalability/results/MP_results_2.txt', 'w') as file:
    file.write(str(results_MP))
with open('Scalability/results/FO_results_2.txt', 'w') as file:
    file.write(str(results_FO))

print("Results saved to results.txt")




