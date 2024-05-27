from MPA.Master import Master
from MPA.Sequence import Sequence
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

        self.thetas = {}
        self.C_max_h = {}
        self.N_h = {}

        self.best_decision_variables = {}

        # self.C_max_prev = {}
        # for i in self.M:
        #     self.C_max_prev[i] = 9999

        # self.N_machine_prev = {}


    def solve(self, t_max = 600, options={}):
        best_makespan = 99999
        iteration = 0
        t = t_max
        start_time = time.time()

        while t > 0:
            iteration += 1
            master = Master(execution_times=self.execution_times, setup_times=self.setup_times, M=self.M, N=self.N, N0=self.N0, 
                            C_max_h=self.C_max_h, thetas=self.thetas, N_h=self.N_h)
            self.decision_variables,completion_times,maximum_makespan_master,assignments, master_solution_is_optimal = master.solve(options=options)
            if maximum_makespan_master < best_makespan:
                sequence = Sequence(fixed_assignments=assignments, M=self.M, N=self.N, N0=self.N0, 
                                    setup_times=self.setup_times, execution_times=self.execution_times)
                maximum_makespan_sequence, self.decision_variables, _ = sequence.solve(options=options)

                if maximum_makespan_sequence is not None and maximum_makespan_sequence < best_makespan:
                    self.best_decision_variables = self.decision_variables
                    best_makespan = maximum_makespan_sequence

                if master_solution_is_optimal:
                    self.C_max_h[iteration] = master.compute_C_max(decision_variables= self.decision_variables, execution_times=self.execution_times, setup_times=self.setup_times)
                    self.thetas[iteration] = master.compute_thetas(assignments, self.setup_times)
                    self.N_h[iteration] = master.compute_N_h(assignments)
            else:
                if master_solution_is_optimal:
                    return self.best_decision_variables, best_makespan
                
            end_time = time.time()
            elapsed_time = end_time - start_time
            t -= elapsed_time

        return self.best_decision_variables, best_makespan









