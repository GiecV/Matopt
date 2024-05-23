import time
import random as r
from Solver import Solver
import gurobipy as gb
import numpy as np

class FixOpt:

    def __init__(self, initial_solution, setup_times, execution_times, t_max=10_000, subproblem_size=106,
                 subproblem_runtime_limit = 16, subproblem_size_adjust_rate = 0.2):
        self.solution = initial_solution
        self.setup_times = setup_times
        self.execution_times = execution_times
        self.t_max = t_max
        self.n = subproblem_size
        self.t_it = subproblem_runtime_limit
        self.alpha = subproblem_size_adjust_rate
        
        keys = []
        for key in execution_times:
            keys.append(key)
        max_key = max(keys, key=lambda item: item)

        self.M = range(1,max_key[0]+1)
        self.N = range(1,max_key[1]+1)
        
        max_makespan = 0
        for machine in self.solution:
            makespan = self.compute_makespan(machine=machine, job_queue=self.solution[machine])
            if makespan > max_makespan:
                max_makespan = makespan
                
        self.solution_makespan = max_makespan

    def solve(self):
        elapsed_time = 0
        start_time = time.time()
        while elapsed_time < self.t_max:
            
            M_prime = []
            M_prime.append(self.find_makespan_machine())
            N_prime = []
            for job in self.solution[M_prime[0]]:
                N_prime.append(job)
            while len(N_prime) < self.n:
                
                other_machine = self.get_machine_from_roulette_wheel(M_prime)
                M_prime.append(other_machine)
                
                if (len(N_prime) + len(self.solution[other_machine])) <= self.n:
                    for job in self.solution[other_machine]:
                        N_prime.append(job)
                else: 
                    jobs_needed = len(N_prime) - self.n
                    r.sample(self.solution[other_machine], jobs_needed) #! occhio che non metta 2 volte lo stesso
            
            execution_subdict, setup_subdict = self.get_subdictionaries(M_prime=M_prime, N_prime=N_prime)
            s = Solver(execution_times=execution_subdict, setup_times=setup_subdict, N=N_prime, M=M_prime)
            #! LOAD SOLUTION INTO MIP ?????
            decision_variables,completion_times,maximum_makespan,assignments = s.solve()
            
            self.solution = self.convert_to_solution_format(decision_variables)
            
            if s.status == gb.GRB.OPTIMAL:
                self.n = np.ceil(self.n * (1 + self.alpha))
            else:
                self.n = np.floor(self.n * (1 - self.alpha))
            
            end_time = time.time()
            elapsed_time += end_time - start_time
        
        return self.solution
    
    def find_makespan_machine(self):
        makespan_for_machine = {}
        
        for key in self.solution:
            makespan_for_machine[key] = self.compute_makespan(key, self.solution[key])
            
        return max(makespan_for_machine, key=makespan_for_machine.get)
    
    def compute_makespan(self, machine, job_queue):
        
        sum_execution_times = 0
        sum_setup_times = 0
        
        for job in job_queue:
            sum_execution_times += self.execution_times[machine, job]
            for i in range(len(job_queue)):
                if i != 0:
                    sum_setup_times += self.setup_times[machine, job_queue[i], job_queue[i-1]]
                              
        return (sum_execution_times + sum_setup_times)
    
    def get_machine_from_roulette_wheel(self, M_prime):
        
        difference_M_set = []
        for machine in self.M:
            if machine not in M_prime:
                difference_M_set.append(machine)
                
        probabilities = {}
        for machine in difference_M_set:
            makespan = self.compute_makespan(machine=machine, job_queue=self.solution[machine])
            probabilities[machine] = 1 - ((self.solution_makespan - makespan)/self.solution_makespan)
            
        return max(probabilities, key=probabilities.get)
    
    def get_subdictionaries(self, M_prime, N_prime):
        
        execution = {}
        setup = {}
        
        for key in self.setup_times:
            i,j,k = key
            if i in M_prime and j in N_prime and k in N_prime:
                setup[i,j,k] = self.setup_times[i,j,k]
        
        for key in self.execution_times:
            i,j = key
            if i in M_prime and j in N_prime:
                execution[i,j] = self.execution_times[i,j]
                
        return execution, setup
    
    def convert_to_solution_format(self, decision_dictionary):
        
        keys = {}
        solution = {}  
        
        for key in decision_dictionary:
            i,j,k = key
            if decision_dictionary[key] == 1:
                if i not in keys:
                    keys[i] = []
                keys[i].append((j,k))
              
        for i in keys:
            solution[i] = []
            job_to_find = 0
            first_iteration = True
            while job_to_find != 0 or first_iteration:
                first_iteration = False
                for pair in keys[i]:
                    j,k = pair
                    if k == job_to_find:
                        if j != 0:
                            solution[i].append(j)
                        job_to_find = j
                        break 
                    
        for i in self.M:
            if i not in self.solution:
                solution[i] = []
                            
        return solution
            
                
