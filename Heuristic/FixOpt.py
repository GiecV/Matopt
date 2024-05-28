import gurobipy as gb
from gurobipy import GRB
import numpy as np
import random as r
import time
from Heuristic.Solver import Solver
import json

class FixOpt:

    def __init__(self, initial_solution, setup_times, N, M ,N0, execution_times, t_max=300, subproblem_size= 106,
                 subproblem_runtime_limit = 1, subproblem_size_adjust_rate = 0.1, makespan_upper_bound = 10_000):
        
        self.solution = initial_solution
        self.setup_times = setup_times
        self.execution_times = execution_times
        self.t_max = t_max
        self.n = subproblem_size
        self.t_it = subproblem_runtime_limit
        self.alpha = subproblem_size_adjust_rate
        self.makespan_upper_bound = makespan_upper_bound
        self.N = N
        self.N_len = len(N)
        self.M = M
        self.M_len = len(M)
        self.N0 = N0

    def compute_single_makespan(self, machine): # Compute the makespan of a single machine
        
        makespan = 0
        
        for (i,j,k), v in self.solution.items(): # For every job in the queue of the machine sum the execution and setup times
            if v == 1 and i == machine:
                if j != 0:
                    makespan += self.execution_times[machine,j]
                if j != 0 and k != 0:
                    makespan += self.setup_times[machine,j,k]
                    
        return makespan

    def compute_makespan(self): # Find the maximum makespan and the machine that has it
        
        machine_times = {}
        
        for (i,j,k), v in self.solution.items(): # For every machine, every job in its queue sum the execution and setup times
            if i not in machine_times:
                machine_times[i] = 0
            if v == 1:
                if j != 0:
                    machine_times[i] += self.execution_times[i,j]
                if j != 0 and k != 0:
                    machine_times[i] += self.setup_times[i,j,k]
                    
        argmax = max(machine_times, key=machine_times.get) # Find the machine with the maximum makespan
        makespan = machine_times[argmax] # Find the maximum makespan
        
        return makespan, argmax
    
    def reduce_matrices(self, N_prime, M_prime): # Reduce the execution and setup times matrices to the subproblem size
        
        reduced_execution_times = {(i, j): self.execution_times[i, j] for i in M_prime for j in N_prime}
        reduced_setup_times = {(i, j, k): self.setup_times[i, j, k] for i in M_prime for j in N_prime for k in N_prime}
        
        return reduced_execution_times, reduced_setup_times
    
    def solve_subproblem(self, N_prime, M_prime, fixed_jobs = {}): # Solve the subproblen, given the indeces of the jobs and machines
        
        job_convertion_table = {} # Convert the indeces of the jobs to the indeces of the subproblem
        job_inverse_convertion_table = {} # Convert the indeces of the subproblem to the indeces of the jobs
        machine_convertion_table = {} # Convert the indeces of the machines to the indeces of the subproblem
        machine_inverse_convertion_table = {} # Convert the indeces of the subproblem to the indeces of the machines
        reduced_setup = {} # Reduced setup times matrix
        reduced_execution = {} # Reduced execution times matrix
        converted_fixed_jobs = {} # Convert the indeces of the fixed jobs to the indeces of the subproblem
        solution = {}

        job_convertion_table[0] = 0 # The dummy job has always index 0
        job_inverse_convertion_table[0] = 0

        for idx, job in enumerate(N_prime): # Create the job conversion tables
            job_convertion_table[job] = idx+1
            job_inverse_convertion_table[idx+1] = job

        for idx, machine in enumerate(M_prime): # Create the machine conversion tables
            machine_convertion_table[machine] = idx+1
            machine_inverse_convertion_table[idx+1] = machine
            
        for job, machine in fixed_jobs.items(): # Convert the fixed jobs
            converted_fixed_jobs[job_convertion_table[job]] = machine_convertion_table[machine]

        # Create the reduced setup and execution times matrices
        for i in M_prime:
            for j in N_prime:
                for k in N_prime:
                    i_tilde = machine_convertion_table[i]
                    j_tilde = job_convertion_table[j]
                    k_tilde = job_convertion_table[k]
                    reduced_setup[i_tilde, j_tilde, k_tilde] = self.setup_times[i, j, k]

        for i in M_prime: 
            for j in N_prime:
                    i_tilde = machine_convertion_table[i]
                    j_tilde = job_convertion_table[j]
                    reduced_execution[i_tilde, j_tilde] = self.execution_times[i, j]

        s = Solver(reduced_execution, reduced_setup, jobs_fixed_to_machine=converted_fixed_jobs, time_limit = self.t_it)

        with open('credentials.txt') as f: 
            data = f.read() 
        options = json.loads(data)

        local_solution, _, local_makespan, _ = s.solve(options=options) # Solve the subproblem

        for (i_tilde,j_tilde,k_tilde),v in local_solution.items(): # Convert the solution to the original indeces
                i = machine_inverse_convertion_table[i_tilde]
                j = job_inverse_convertion_table[j_tilde]
                k = job_inverse_convertion_table[k_tilde]

                solution[i,j,k] = v

        return solution, local_makespan, s.status      

    def find_jobs(self, machine): # Find the jobs in the queue of a machine
        
        jobs = []
        
        for (i,j,k),v in self.solution.items():
            if v == 1 and i == machine and j != 0:
                jobs.append(j)

        return jobs

    def select_machine(self, set, makespan): # Compute the probability of selecting a machine and select one at random
        
        p = {}
        
        for machine in set:
            p[machine] = 1 - ((makespan - self.compute_single_makespan(machine=machine))/makespan)
            
        machines = list(p.keys())
        probabilities = list(p.values())

        print(p)
        
        selected_machine = r.choices(machines, weights=probabilities, k=1)[0]
    
        return selected_machine

    def join_solutions(self, partial_solution, N0_prime, M_prime): # Join the solution of the subproblem with the global solution
        
        new_solution = self.solution.copy()
    
        # Set all new_solution[i, j, k] to 0 where i is in M_prime and j and k are in N0_prime
        for i in M_prime:
            for j in self.N0: #N0_prime
                for k in self.N0: #N0_prime
                    new_solution[i, j, k] = 0
    
        # Update new_solution with the keys from partial_solution
        for key, v in partial_solution.items():
            new_solution[key] = v

        return new_solution

    def solve(self):
        
        start_time = time.time() # Start the timer	
        
        while time.time() - start_time < self.t_max: # Until the time limit is reached
            
            makespan, i_max = self.compute_makespan() # Compute the makespan and the machine with the maximum makespan
            
            M_prime = []
            M_prime.append(i_max) # Add the machine with the maximum makespan to the subproblem
            N_prime = self.find_jobs(i_max) # Add the jobs in the queue of the machine with the maximum makespan to the subproblem

            N0_prime = N_prime.copy()
            N0_prime.insert(0,0)

            fixed_jobs = {}

            while len(N_prime) < self.n: # Until the subproblem size is reached

                M_difference = [machine for machine in self.M if machine not in M_prime] # Find M-M'
                if M_difference == []: # If M-M' is empty, then solve the entire problem
                    break
                i = self.select_machine(M_difference, makespan) # Select the machine with the highest probability

                M_prime.append(i) # Add the machine to the subproblem
                idx = M_difference.index(i) 
                M_difference.pop(idx) # Remove the machine from M-M'

                S_i = self.find_jobs(i) # Find the jobs in the queue of the machine

                if len(N_prime) + len(S_i) <= self.n: # If possible, add all the jobs in the queue of the machine
                    for job in S_i:
                        N_prime.append(job)
                else: # If not, add a random sample of the jobs in the queue of the machine
                    needed_jobs = self.n - len(N_prime)
                    jobs = r.sample(S_i, int(needed_jobs))
                    for job in jobs:
                        N_prime.append(job)
                    
                    for job in S_i: # The jobs that are not sampled have to be fixed to the current machine
                        if job not in jobs and job != 0:
                            fixed_jobs[job] = i
                    
                for job in fixed_jobs: # Add the fixed jobs to the subproblem, as they can be moved in the queue they currently are
                    N_prime.append(job)

            partial_solution, _, status = self.solve_subproblem(N_prime=N_prime, M_prime=M_prime,
                                                                               fixed_jobs=fixed_jobs)

            self.solution = self.join_solutions(partial_solution, M_prime= M_prime, N0_prime=  N0_prime) # Complete the partial solution

            overall_makespan, _ = self.compute_makespan() # Compute the makespan of the whole problem

            if status == GRB.OPTIMAL: # If the subproblem is solved to optimality, increase the subproblem size
                self.n = min(len(self.N), np.ceil(self.n * (1 + self.alpha)))
            else: # If not, decrease the subproblem size
                self.n = max(1, np.floor( self.n * (1 - self.alpha) ))

            self.time = time.time() - start_time # Update the time
            self.makespan = overall_makespan # Update the makespan

        return self.solution, self.makespan
