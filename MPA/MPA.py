from MPA.Master import Master
from MPA.Sequence import Sequence
import time
import gurobipy as gb
from gurobipy import GRB
import numpy as np

class MPA:
    def __init__(self, execution_times:dict, setup_times:dict, t_max = 600):

        self.execution_times = execution_times 
        self.setup_times = setup_times
        self.t_max = t_max # Time limit in seconds

        keys = []
        for key in execution_times:
            keys.append(key)
        max_key = max(keys, key=lambda item: item)

        self.M = range(1,max_key[0]+1)
        self.N = range(1,max_key[1]+1)
        self.N0 = range(max_key[1]+1) # N0 has to start from 0


    def solve(self, options={}):
        
        best_makespan = np.Inf # Initialize best makespan
        iteration = 0
        t = self.t_max
        start_time = time.time() # Start time of the algorithm
        master_solution = {} 
        master_makespan = best_makespan
        master_status = None
        sequence_solution = {}
        sequence_makespan = best_makespan
        best_solution = {}
        C_max_h = {}
        thetas = {}
        N_h = {}
        

        master = Master(execution_times=self.execution_times, setup_times=self.setup_times,
                        M=self.M, N=self.N, N0=self.N0) # Initialize master problem

        while t > 0: # Until the time limit is reached
            iteration += 1 # Increase iteration
            # print('Iteration:', iteration)
            # print('Best makespan:', best_makespan)
            # print('Best solution:')
            # for i in self.M:
            #     for j in self.N0:
            #         for k in self.N0:
            #             if best_solution.get((i,j,k), 0) != 0:
            #                 print(f'{(i,j,k)} = {best_solution[i,j,k]}')
            
            if iteration == 1: # In the first iteration, the problem has to be solved with gap <2% or time limit 90% of the total time
                master_solution, master_assignments, master_makespan, master_status = master.solve(options=options, iteration=iteration,
                                                                               C_max_h=C_max_h,
                                                                               theta=thetas, N_h=N_h, t_max=t)
            else: #Else solve normally
                master_solution, master_assignments, master_makespan, master_status = master.solve(options=options, C_max_h=C_max_h,
                                                                               theta=thetas, N_h=N_h, t_max=t)

            # print('Master solution:')
            # for i in self.M:
            #     for j in self.N0:
            #         for k in self.N0:
            #             if master_solution[i,j,k] != 0 :
            #                 print(f'{(i,j,k)} = {master_solution[i,j,k]}')
            # print('Master assignments:')
            # for i in self.M:
            #     for j in self.N0:
            #         if master_assignments[i,j] != 0 :
            #             print(f'{(i,j)} = {master_assignments[i,j]}')
            # print('Master makespan:', master_makespan)

            if master_makespan < best_makespan:
                # Solve the sequence problem
                sequence = Sequence(fixed_assignments = master_assignments, M = self.M, N = self.N, N0  = self.N0, 
                                    setup_times=self.setup_times, execution_times= self.execution_times, time_limit = t)
                sequence_solution, sequence_makespan = sequence.solve(options=options)

                # print('Sequence solution:')
                # for i in self.M:
                #     for j in self.N0:
                #         for k in self.N0:
                #             if sequence_solution[i,j,k] == 1 :
                #                 print(f'{(i,j,k)}')
                # print('Sequence makespan:', sequence_makespan)

                if sequence_solution is not None and sequence_makespan is not None:
                    if sequence_makespan < best_makespan: # Update the best solution    
                        best_makespan = sequence_makespan
                        best_solution = sequence_solution
                
                if master_status == gb.GRB.OPTIMAL: # Compute parameters for adding cuts to the master problem
                    # C_max_h[iteration] = self.compute_C_max_h(master_solution, master_assignments) #! best_solution
                    C_max_h[iteration] = self.compute_C_max_h(sequence_solution)
                    thetas[iteration] = self.compute_thetas(master_assignments)
                    N_h[iteration] = self.compute_N_h(master_assignments)
                    
            else: # If no improvement is found, but an optimal solution has been found, return it
                if master_status == gb.GRB.OPTIMAL:
                    return best_solution, best_makespan
                
            t = self.t_max - (time.time() - start_time)
            
        return best_solution, best_makespan
    
    def compute_C_max_h(self, solution):  # Compute C^{h,i}_max
        
        C_max_h = {}
        for i in self.M:  # Compute the makespan for each machine
            makespan = 0
            execution_time = 0
            setup_time = 0
            for j in self.N0:
                for k in self.N0:
                    if solution[i,j,k] != 0:
                        if j == 0:
                            execution_time = 0
                            setup_time = 0
                        elif k == 0:
                            execution_time = self.execution_times[i, j] * solution[i, j, k]
                            setup_time = 0
                        else:
                            execution_time = self.execution_times[i, j] * solution[i, j, k]
                            setup_time = self.setup_times[i, j, k] * solution[i, j, k]

                        time = (execution_time + setup_time)
                        makespan += time
            C_max_h[i] = makespan

        # C_max_h = {}
        
        # for i in self.M:
        #     sum1 = 0
        #     for j in self.N0:
        #         if j != 0:  # Ensuring we only take j ≠ 0
        #             for k in self.N:
        #                 sum1 += self.setup_times[i, j, k] * solution.get((i, j, k), 0)
        
        #     sum2 = 0
        #     for k in self.N:
        #         sum2 += self.execution_times[i, k] * assignments.get((i, k), 0)
        
        #     C_max_h[i] = sum1 + sum2

        # print(f'C_max: {C_max_h}')

        return C_max_h

    def compute_thetas(self, master_assignments): # Compute theta^h_{i,j}
        thetas = {}
        for i in self.M:
            for j in self.N0:
                if j != 0:
                    assigned_jobs = [j for j in self.N if master_assignments[i,j] == 1 and j != 0] # Find the assigned jobs
                    # Find the maximum setup time among the assigned jobs
                    max_setup_time = max(self.setup_times[i, j, k] for k in assigned_jobs) if assigned_jobs else 0
                    thetas[i, j] = self.execution_times[i, j] + max_setup_time # Sum the processing time to the maximum setup time

        # print(f'theta: {thetas}')

        return thetas

    def compute_N_h(self, master_assignments):  # Compute N^h_i
        N_h = {i: [] for i in self.M}
        for i in self.M:
            for j in self.N0:
                if master_assignments[i, j] == 1 and j != 0:
                    N_h[i].append(j)

        # print(f'N_h: {N_h}')

        return N_h  # Return the set of jobs for each machine