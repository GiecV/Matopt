import random as r
import numpy as np

class Greedy:

    def __init__(self, execution_times, setup_times):
        self.execution_times = execution_times 
        self.setup_times = setup_times

        keys = []
        for key in execution_times:
            keys.append(key)
        max_key = max(keys, key=lambda item: item)

        self.M = range(1,max_key[0]+1)
        self.N = range(1,max_key[1]+1)
        self.N0 = range(max_key[1]+1)
        self.S = {}

    def solve(self):

        solution_dict = {}

        for i in self.M: # Initialization of the solution
            self.S[i] = []

        self.N = self.shuffle(self.N) #Shuffle N

        for j in self.N: # For each job
            m = self.find_smallest_completion_time(j) # Find the machine with the smallest completion time
            p = self.find_best_position(m, j) # Find the best position of the queue

            self.S[m].insert(p, j) # Insert the job in the queue

        # Convert the solution to a dictionary
        for machine in self.S:
            for idx, job in enumerate(self.S[machine]):
                if idx == 0:
                    solution_dict[machine, job, 0] = 1
                else: solution_dict[machine, job, self.S[machine][idx-1]] = 1
            solution_dict[machine,0,self.S[machine][-1]] = 1

        for i in self.M:
            for j in self.N0:
                for k in self.N0:
                    if (i,j,k) not in solution_dict:
                        solution_dict[i,j,k] = 0

        return solution_dict

    def shuffle(self, set_range): # Shuffle the set

        shuffled_list = [i for i in set_range]
        r.shuffle(shuffled_list)
        
        return shuffled_list
    
    def find_smallest_completion_time(self, j): # Find the machine with the smallest completion time
        makespan_for_machine = {}

        for key in self.S:
            sum_execution_times = 0
            sum_setup_times = 0

            for job in self.S[key]: # Calculate the makespan for each machine
                sum_execution_times += self.execution_times[key, job]
                for i in range(len(self.S[key])):
                    if i != 0:
                        sum_setup_times += self.setup_times[key, self.S[key][i], self.S[key][i-1]]

            makespan_for_machine[key] = sum_execution_times + sum_setup_times # Sum the execution and setup times

        # Find the machine(s) with the smallest makespan
        min_makespan = min(makespan_for_machine.values())
        best_machines = [machine for machine, makespan in makespan_for_machine.items() if makespan == min_makespan]

        # If there's a tie, choose the machine with the smallest processing time for job j
        if len(best_machines) > 1:
            best_machine = min(best_machines, key=lambda machine: self.execution_times[machine, j])
        elif best_machines:  # Check if best_machines is not empty
            best_machine = best_machines[0]
        else:  # If best_machines is empty, return a default machine
            best_machine = self.M[0]

        return best_machine

    def find_best_position(self, machine, job): # Find the best position of the queue
        best_time = np.Inf
        best_position = None
        job_queue = self.S[machine].copy()

        if len(job_queue) == 0: # If the queue is empty, add it at the beginning
            return 0

        for pos in range(len(job_queue) + 1):
            job_queue.insert(pos, job) # Try to insert the job in each position of the queue
            sum_execution_times = 0
            sum_setup_times = 0

            for job_index in range(len(job_queue)):
                sum_execution_times += self.execution_times[machine, job_queue[job_index]]
                if job_index != 0:
                    sum_setup_times += self.setup_times[machine, job_queue[job_index], job_queue[job_index-1]]

            total_time = sum_execution_times + sum_setup_times # Compute the total time 
            if total_time < best_time: # If it is an improvement, keep it
                best_time = total_time
                best_position = pos

            job_queue.remove(job) # Remove the job from the current position before trying the next one

        return best_position if best_position is not None else 0
    
                
            


