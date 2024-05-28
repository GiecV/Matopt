import gurobipy as gb
from MPA.Master import Master

class Sequence:

    def __init__(self, fixed_assignments: dict, M, N, N0, setup_times, execution_times, makespan_upper_bound = 10_000, time_limit = 60):

        self.fixed_assignments = fixed_assignments
        self.M = M
        self.N = N
        self.N0 = N0
        self.setup_times = setup_times
        self.execution_times = execution_times
        self.U = makespan_upper_bound
        self.t_max = time_limit

    def solve(self, options = {}): #fix solve method it does not work

        env = gb.Env(params=options)
        sequence = gb.Model(env=env)
        sequence.Params.OutputFlag = 0 # Avoid verbose output
        sequence.Params.TimeLimit = self.t_max

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
            gb.quicksum( gb.quicksum( self.execution_times[i,j] * self.fixed_assignments[i,j] for j in self.N ) for i in self.M), 
            gb.GRB.MINIMIZE)

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
                        U[j] - U[k] + self.U * gb.quicksum( X[i,j,k] for i in self.M) <= self.U - 1
                    ) 
        
        #21. Sub-tour elimination
        for j in self.N:
            sequence.addConstr(
                U[j] + gb.quicksum( X[i,0,j] for i in self.M) >= 1
            )
        
        #22. Sub-tour elimination
        for i in self.M:
            sequence.addConstr(
                U[j] + (self.U - 1) * gb.quicksum( X[i,0,j] for i in self.M) <= self.U - 1
            )

        #24. Set U domain
        for j in self.N:
            sequence.addConstr(
                        U[j] >= 0
            )

        # Solve the problem
        sequence.optimize()

        # Save the results if the problem is feasible, otherwise return None
        decision_variables = {}
        jobs_before = {}
        
        for i in self.M:
            for j in self.N0:
                for k in self.N0:
                    decision_variables[i,j,k] = X[i,j,k].X
                    
        for j in self.N:
            jobs_before[j] = U[j].X
        
        return decision_variables, self.compute_makespan(decision_variables, jobs_before)

    def compute_makespan(self, decision_variables, jobs_before):
        makespans = {}
    
        for i in self.M:
            makespan_i = 0
            for j in self.N:
                for k in self.N0:
                    if decision_variables[i,j,k] == 1:
                        makespan_i += self.execution_times[i,j]
                        if k != 0:
                            makespan_i += self.setup_times[i,j,k]
            makespans[i] = makespan_i

        max_makespan = max(makespans.values())
    
        return max_makespan