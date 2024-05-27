import random as r

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
            min_makespan = 10_000
            best_machines = []
            best_machine = None
            
            for job in self.S[key]: # Calculate the makespan for each machine
                sum_execution_times += self.execution_times[key, job]
                for i in range(len(self.S[key])):
                    if i != 0:
                        sum_setup_times += self.setup_times[key, self.S[key][i], self.S[key][i-1]]

            makespan_for_machine[key] = sum_execution_times + sum_setup_times # Sum the execution and setup times

            for key in makespan_for_machine: #Find the minimum makespan machine
                if makespan_for_machine[key] == min_makespan:
                    best_machines.append(key)
                elif makespan_for_machine[key] < min_makespan:
                    min_makespan = makespan_for_machine[key]
                    best_machines = []
                    best_machines.append(key)

            if len(best_machines) > 1: #Resolve draw if necessary
                best_execution_time = 10_000
                for key in best_machines:
                    if self.execution_times[key, j] < best_execution_time:
                        best_execution_time = self.execution_times[key, j]
                        best_machine = key

            else:
                best_machine = best_machines[0]
        return best_machine

    def find_best_position(self, machine, job): # Find the best position of the queue
        
        best_time = 10_000
        best_position = None
        job_queue = self.S[machine].copy()

        if len(job_queue) == 0: # If the queue is empty, add it at the beginning
            best_position = 0
            return best_position

        for i in range(len(job_queue)):
            job_queue.insert(i, job) # Try to insert the job in each position of the queue
            sum_execution_times = 0
            sum_setup_times = 0

            for job in job_queue:
                sum_execution_times += self.execution_times[machine, job]
                for i in range(len(job_queue)):
                    if i != 0:
                        sum_setup_times += self.setup_times[machine, job_queue[i], job_queue[i-1]]

            total_time = sum_execution_times + sum_setup_times # Compute the total time 
            if total_time < best_time: # If it is an improvement, keep it
                best_time = total_time
                best_position = i
        
        return best_position
                
            


