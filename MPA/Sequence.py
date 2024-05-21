import gurobipy as gb
from MPA.Master import Master

class Sequence:

    def __init__(self, fixed_assignments, M, N, N0, setup_times, execution_times, makespan_upper_bound = 10_000):

        self.fixed_assignments = fixed_assignments
        self.M = M
        self.N = N
        self.N0 = N0
        self.setup_times = setup_times
        self.execution_times = execution_times
        self.makespan_upper_bound = makespan_upper_bound

    def solve(self): #fix solve method it does not work

        sequence = gb.Model()
        sequence.Params.OutputFlag = 0 # Avoid verbose output

        X = sequence.addVars( # Add sequence variables
            [(i,j,k) 
             for i in self.M
             for j in self.N0
             for k in self.N0
            ], vtype = gb.GRB.BINARY
        )

        U = sequence.addVars( # Add assignment variables
            [j for j in self.N], vtype = gb.GRB.CONTINUOUS
        )

        #16. Objective function
        sequence.setObjective(
            gb.quicksum( gb.quicksum( gb.quicksum( self.setup_times[i,j,k] * X[i,j,k] for k in self.N if k != j) for j in self.N0) for i in self.M) + 
            gb.quicksum( gb.quicksum( self.execution_times[i,j] * self.fixed_assignments[i,j] for j in self.N) for i in self.M), gb.GRB.MINIMIZE)

        #17. At most one job is scheduled as the first job on each machine
        for i in self.M:
            sequence.addConstr(
                gb.quicksum( X[i,0,k] for k in self.N ) <= 1 
        )
            
        #18. Each job has exactly one predecessor and both of them assigned to the same machine
        for i in self.M:
            for k in self.N:
                sequence.addConstr(
                    gb.quicksum( X[i,j,k] for j in self.N0 if j != k) == self.fixed_assignments[i,k]
                ) 
        
        #19. Each job has exactly one successor and both of them assigned to the same machine
        for i in self.M:
            for j in self.N:
                sequence.addConstr(
                    gb.quicksum( X[i,j,k] for k in self.N0 if j != k) == self.fixed_assignments[i,j]
                ) 
        
        #20. Sub-tour elimination
        for j in self.N:
            for k in self.N:
                if j != k:
                    sequence.addConstr(
                        U[j] - U[k] + self.makespan_upper_bound * gb.quicksum( X[i,j,k] for i in self.M) <= self.makespan_upper_bound - 1
                    ) 
        
        #21. Sub-tour elimination
        for j in self.N:
            sequence.addConstr(
                U[j] + gb.quicksum( X[i,0,j] for i in self.M) >= 1
            )
        
        #22. Sub-tour elimination
        for i in self.M:
            sequence.addConstr(
                U[j] + (self.makespan_upper_bound - 1) * gb.quicksum( X[i,0,j] for i in self.M) <= self.makespan_upper_bound - 1
            )

        #24. Set U domain
        for j in self.N:
            sequence.addConstr(
                        U[j] >= 0
            )

        # Solve the problem
        sequence.optimize()

        # Save the results if the problem is feasible, otherwise return None
        if sequence.Status == gb.GRB.OPTIMAL:
            decision_variables = {}
            jobs_before = {}
            
            for i in self.M:
                for j in self.N0:
                    for k in self.N0:
                        decision_variables[i,j,k] = X[i,j,k].X
            for j in self.N:
                jobs_before[j] = U[j].X

            m = Master(None,None,range(1,3),range(1,5),range(0,5),None,None,None)
            makespans = m.compute_C_max(decision_variables= decision_variables, execution_times=self.execution_times, setup_times=self.setup_times)

            max_makespan = 0
            for key in makespans:
                if makespans[key] > max_makespan:
                    max_makespan = makespans[key]

            return max_makespan, decision_variables,jobs_before
        
        else: 
            print('Sequence problem did not return a feasible solution')
            return None, None, None