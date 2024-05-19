import gurobipy as gb
from Master import Master
from Sequence import Sequence
import time

class MPA:
    def __init__(self, execution_times:dict, setup_times:dict):

        self.execution_times = execution_times 
        self.setup_times = setup_times

        keys = []
        for key in execution_times:
            keys.append(key)
        max_key = max(keys, key=lambda item: item)

        self.M = range(1,max_key[0]+1)
        self.N = range(1,max_key[1]+1)
        self.N0 = range(max_key[1]+1) # N0 has to start from 0

        # self.C_max_prev = {}
        # for i in self.M:
        #     self.C_max_prev[i] = 9999

        # self.N_machine_prev = {}


    def solve(self, t_max = 600):
        best_makespan = 99999
        iteration = 0
        t = t_max
        start_time = time.time()
        master = Master(self.execution_times, self.setup_times, self.M, self.N, self.N0)

        while t > 0:
            iteration += 1
            decision_variables,completion_times,maximum_makespan_master,assignments, master_solution_is_optimal = master.solve()
            if maximum_makespan_master < best_makespan:
                sequence = Sequence()
                maximum_makespan_sequence = sequence.solve(assignments)

                if maximum_makespan_sequence < best_makespan:
                    best_makespan = maximum_makespan_sequence

                if master_solution_is_optimal:
                    # add cuts
                    a = 1
            else:
                if master_solution_is_optimal:
                    return decision_variables,completion_times,best_makespan,assignments
                
            end_time = time.time()
            elapsed_time = end_time - start_time
            t -= elapsed_time

        return decision_variables,completion_times,best_makespan,assignments









