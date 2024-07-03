from Solver import Solver
from Heuristic.Greedy import Greedy
from Heuristic.FixOpt import FixOpt
import random as r
import json
from IPython.display import clear_output
import time
import matplotlib.pyplot as plt
import numpy as np

##############################################################################
# Script used to test the heuristic performance with different maximum times #
##############################################################################

# r.seed(10) # Seed for reproducibility
  
with open('credentials.txt') as f: # Load the credentials for Gurobi
    data = f.read() 
options = json.loads(data)

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

N_cardinality = 50
M_cardinality = 10

amount_of_problems = 10
times = [.1,.2,.3,.4,.5,.6, .7, .8, .9, 1, 1.5]
heuristic_runs = 5

N = range(1, N_cardinality+1) # Create the sets N, M, N0
M = range(1, M_cardinality+1)
N0 = [i for i in N]
N0.insert(0,0)

gaps = {}

for percentage in times:
            gaps[percentage] = []

for i in range(amount_of_problems):
    P_dict, S_dict = generate_instance(N_cardinality = N_cardinality, M_cardinality = M_cardinality) # Generate the instance

    t = time.time()
    s = Solver(execution_times = P_dict, setup_times = S_dict) # Solve using the IP solver
    decision_variables,completion_times,maximum_makespan,assignments = s.solve(options=options)

    elapsed_time = time.time() - t

    for percentage in times:
        runtime_limit = elapsed_time * percentage
        print(runtime_limit)

        for run in range(heuristic_runs):
            clear_output(wait=True)
            print(f'Running iteration {run} with runtime limit {runtime_limit}', end='\r')
            greedy = Greedy(execution_times=P_dict, setup_times=S_dict) # Find the initial solution
            solution = greedy.solve()
            m = FixOpt(initial_solution=solution, setup_times=S_dict,execution_times=P_dict, N=N, M=M, N0=N0, # Solve using the FO heuristic
                   subproblem_size_adjust_rate=0.5, t_max = runtime_limit, subproblem_runtime_limit=30, subproblem_size=10, WLS_license=True)
            solution, makespan = m.solve()

            gaps[percentage].append((makespan - maximum_makespan)/maximum_makespan * 100)

with open('results/FO_times_results.txt', 'w') as file:
    file.write(str(gaps))

# Plot the results
# Step 1: Calculate Averages and Standard Deviations
averages = []
std_devs = []
runtime_limits = sorted(gaps.keys())  # Ensure the keys are sorted for plotting

for runtime_limit in runtime_limits:
    avg = np.mean(gaps[runtime_limit])
    std_dev = np.std(gaps[runtime_limit])
    averages.append(avg)
    std_devs.append(std_dev)

# Step 3: Plotting
plt.figure(figsize=(10, 6))
plt.plot(runtime_limits, averages, label='Average Gap', color='blue')  # Plot the average line
plt.fill_between(runtime_limits, np.subtract(averages, std_devs), np.add(averages, std_devs), color='blue', alpha=0.2)  # Plot the standard deviation as a shadow

plt.xlabel('Runtime Limit (%)')
plt.ylabel('Average Gap (%)')
plt.title('Heuristic Time with Different Runtime Limits')
plt.legend()
plt.grid(True)
plt.show()