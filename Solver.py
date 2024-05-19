import gurobipy as gb
import numpy as np
import random as r
import matplotlib as plt

class Solver:

    def __init__(self, execution_times: dict, setup_times: dict, makespan_upper_bound = 10_000):
        
        self.execution_times = execution_times 
        self.setup_times = setup_times

        # Get all keys in a list for the computation of the required sets
        keys = []
        for key in execution_times:
            keys.append(key)
        max_key = max(keys, key=lambda item: item)

        self.M = range(1,max_key[0]+1)
        self.N = range(1,max_key[1]+1)
        self.N0 = range(max_key[1]+1) # N0 has to start from 0

        self.makespan_upper_bound = makespan_upper_bound

        for i in self.M: # Setting the setup time for dummy jobs to 0
            for k in self.N:
                self.setup_times[i,0,k] = 0

    def solve(self):

        model = gb.Model()
        model.Params.OutputFlag = 0 # Avoid verbose output

        X = model.addVars( # Add sequence variables
            [(i,j,k) 
             for i in self.M
             for j in self.N0
             for k in self.N0], vtype = gb.GRB.BINARY
        )

        Y = model.addVars( # Add assignment variables
            [(i,k)
             for i in self.M
             for k in self.N0], vtype = gb.GRB.BINARY
        )

        C = model.addVars( # Add completion time variables
            [j for j in self.N0], vtype = gb.GRB.CONTINUOUS
        )

        C_max = model.addVar(vtype=gb.GRB.CONTINUOUS) # Add makespan variable


        #1. Objective function
        model.setObjective(C_max, gb.GRB.MINIMIZE)

        #2. Each job assigned exactly to one machine
        for k in self.N:
            model.addConstr(
                gb.quicksum( Y[i,k] for i in self.M ) == 1 
        )
            
        #3. Each job has exactly one predecessor and both of them assigned to the same machine
        for k in self.N:
            for i in self.M:
                model.addConstr(
                    gb.quicksum( X[i,j,k] for j in self.N0 if j != k) == Y[i,k]
                )

        #4. Each job has exactly one successor and both of them assigned to the same machine
        for j in self.N:
            for i in self.M:
                model.addConstr(
                    gb.quicksum( X[i,j,k] for k in self.N0 if k != j ) == Y[i,j]
                )
        #5. At most one job is scheduled as the first job on each machine
        for i in self.M:
            model.addConstr(
                gb.quicksum( X[i,0,k] for k in self.N) <= 1
            )

        #6. Sub-tour elimination constraints
        for j in self.N0:
            for k in self.N:
                if j != k:
                    for i in self.M:
                        model.addConstr(
                            C[k] - C[j] + (self.makespan_upper_bound * (1 - X[i,j,k])) >= self.setup_times[i,j,k] + self.execution_times[i,k] 
                        )

        #7. Completion time for dummy job is 0
        model.addConstr(
            C[0] == 0
        )

        #8. Linearization of the objective function
        for j in self.N:
            model.addConstr(
                C[j] <= C_max
            )

        #9. Valid inequalities
        for i in self.M:
            model.addConstr(
                gb.quicksum(
                    gb.quicksum((self.setup_times[i,j,k] * X[i,j,k]) for k in self.N)
                    for j in self.N0 if j!= k) +
                gb.quicksum((self.execution_times[i,k] * Y[i,k]) for k in self.N)
                <= C_max
            )

        # Set Cj domain
        for j in self.N0:
            model.addConstr(
                C[j] >= 0
            )

        # Set Cmax domain
        model.addConstr(
            C_max >= 0
        )

        # Solve the problem
        model.optimize()

        # Save the results if the problem is feasible, otherwise return None
        if model.Status == gb.GRB.OPTIMAL:
            decision_variables = [[[X[i, j, k].X for k in self.N0] for j in self.N0] for i in self.M]
            completion_times = [C[j].X for j in self.N0]
            maximum_makespan = C_max.X
            assignments = [[Y[i,k].X for k in self.N0] for i in self.M]

            return decision_variables,completion_times,maximum_makespan,assignments
        else: return None


        


    