import time
import random as r
from Solver import Solver

class FixOpt:

    def __init__(self, initial_solution, setup_times, execution_times, t_max=10_000, subproblem_size=5,
                 subproblem_runtime_limit = 100, subproblem_size_adjust_rate = 0):
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
        time = 0
        start_time = time.time()
        while time < self.t_max:
            
            M_prime = []
            M_prime.append(self.find_makespan_machine())
            N_prime = []
            N_prime.append(job for job in self.solution[M_prime[0]])
            while len(N_prime) <= self.n:
                
                other_machine = self.get_machine_from_roulette_wheel(M_prime)
                M_prime.append(other_machine)
                
                if (len(N_prime) + len(self.solution[other_machine])) <= self.n:
                    N_prime.append(job for job in self.solution[other_machine])
                else: 
                    jobs_needed = len(N_prime) - self.N
                    r.sample(self.solution[other_machine], jobs_needed) #! occhio che non metta 2 volte lo stesso
                    
                execution_subdict, setup_subdict = self.get_subdictionaries(M=M_prime, N=N_prime)
                s = Solver(execution_times=execution_subdict, setup_times=setup_subdict)
            
            end_time = time.time()
            time += end_time - start_time
        
        return self.solution
    
    def find_makespan_machine(self):
        makespan_for_machine = {}
        
        for key in self.solution:
            makespan_for_machine[key] = self.compute_makespan(self, key, self.solution[key])
            
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
    
    def get_subdictionaries(self, M, N):
        
        execution = {}
        setup = {}
        
        #create subdictionaries from M and N
        
        return execution, setup
    