from Heuristic.FixOpt import FixOpt
from Heuristic.Greedy import Greedy
import random as r

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

N_cardinality = 10
M_cardinality = 3

execution, setup = generate_instance(N_cardinality = 10, M_cardinality = 3)

N = range(1, N_cardinality+1)
M = range(1, M_cardinality+1)
N0 = [i for i in N]
N0.insert(0,0)

m = Greedy(execution_times=execution, setup_times=setup)
solution = m.solve()
for i in M:
    for j in N:
        for k in N0:
            if solution[i,j,k] == 1:
                print(f'Job {j} scheduled after job {k} in machine {i}')

m = FixOpt(initial_solution=solution, setup_times=setup, execution_times=execution, N=N, M=M, N0=N0, subproblem_size_adjust_rate=0)
solution = m.solve()
for i in M:
    for j in N:
        for k in N0:
            if solution[i,j,k] == 1:
                print(f'Job {j} scheduled after job {k} in machine {i}')
