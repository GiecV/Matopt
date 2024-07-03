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

# r.seed(10) # Seed for reproducibility
  
with open('credentials.txt') as f: # Load the credentials for Gurobi
    data = f.read() 
options = json.loads(data)

def convert_keys_to_string(dictionary):
    """Converts dictionary keys to strings."""
    return {str(key): value for key, value in dictionary.items()}

def generate_instance(N_cardinality, M_cardinality,
                      min_execution_time = 1, max_execution_time = 100,
                      min_setup_time = 1, max_setup_time = 10):
    
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

M_list = [2,3,5,10]
N_list = [10,20,30,40,50]
runtime_limit = 1800 # seconds
runs_for_each_case = 10

results_IP = {}
results_MP = {}
results_FO = {}

for M_cardinality in M_list:
    for N_cardinality in N_list:

        N = range(1, N_cardinality+1) # Create the sets N, M, N0
        M = range(1, M_cardinality+1)
        N0 = [i for i in N]
        N0.insert(0,0)

        results_IP[(N_cardinality, M_cardinality)] = {}
        results_MP[(N_cardinality, M_cardinality)] = {}
        results_FO[(N_cardinality, M_cardinality)] = {}

        for iteration in range(runs_for_each_case):

            print(f'Running iteration {iteration} with N={N_cardinality}, M={M_cardinality}', end='\r')

            t = time.time()
            P_dict, S_dict = generate_instance(N_cardinality = N_cardinality, M_cardinality = M_cardinality) # Generate the instance

            s = Solver(execution_times = P_dict, setup_times = S_dict, max_time = runtime_limit) # Solve using the IP solver
            decision_variables,completion_times,maximum_makespan,assignments = s.solve(options=options)
            results_IP[(N_cardinality, M_cardinality)][iteration] = {'makespan': round(maximum_makespan), 'time': time.time() - t, 'gap': s.gap}

            t = time.time()
            s = MPA(execution_times = P_dict, setup_times = S_dict, t_max = runtime_limit) # Solve using the MP solver
            decision_variables,maximum_makespan_MPA = s.solve(options=options)
            results_MP[(N_cardinality, M_cardinality)][iteration] = {'makespan': round(maximum_makespan_MPA), 'time': time.time() - t, 'gap': ((maximum_makespan - maximum_makespan_MPA)/maximum_makespan)*100}

            runtime_for_heuristic = min(results_IP[(N_cardinality, M_cardinality)][iteration]['time'], results_MP[(N_cardinality, M_cardinality)][iteration]['time'])
            #! min
            t = time.time()
            greedy = Greedy(execution_times=P_dict, setup_times=S_dict) # Find the initial solution
            solution = greedy.solve()
            m = FixOpt(initial_solution=solution, setup_times=S_dict,execution_times=P_dict, N=N, M=M, N0=N0, # Solve using the FO heuristic
                   subproblem_size_adjust_rate=0.5, t_max = runtime_for_heuristic, subproblem_runtime_limit=30, subproblem_size=10, WLS_license=True)
            solution, makespan = m.solve()
            print(f'FO: {makespan} vs IP: {maximum_makespan}')
            results_FO[(N_cardinality, M_cardinality)][iteration] = {'makespan': round(makespan), 'time': time.time() - t, 'gap': ((maximum_makespan - makespan)/maximum_makespan)*100}

results_IP_str_keys = convert_keys_to_string(results_IP)
results_MP_str_keys = convert_keys_to_string(results_MP)
results_FO_str_keys = convert_keys_to_string(results_FO)

with open('results/IP_results.txt', 'w') as file:
    file.write(str(results_IP))
with open('results/MP_results.txt', 'w') as file:
    file.write(str(results_MP))
with open('results/FO_results.txt', 'w') as file:
    file.write(str(results_FO))

print("Results saved to results.txt")