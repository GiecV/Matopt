import gurobipy as gb
from gurobipy import GRB

class Master:
    
    def __init__(self, execution_times, setup_times, M, N, N0):
        
        self.execution_times = execution_times
        self.setup_times = setup_times
        self.M = M
        self.N = N
        self.N0 = N0

    def solve(self, C_max_h, theta, N_h, options = {}, iteration = 0, t_max = 60):
        
        env = gb.Env(params=options)
        master = gb.Model(env=env)
        master.Params.OutputFlag = 0 # Avoid verbose output
        master.Params.TimeLimit = t_max
        
        if iteration == 1: # Set gap <2% or time limit 90% of the total time
            master.Params.MIPGap = 0.02
            master.Params.TimeLimit = 0.9 * t_max

        X_continuous = {(i,j,k): master.addVar(vtype=gb.GRB.CONTINUOUS, lb=0, ub=1)
                        for i in self.M
                        for j in self.N0
                        for k in self.N0
                        if j != k}

        X_binary = {(i,j,k): master.addVar(vtype=gb.GRB.BINARY)
                    for i in self.M
                    for j in self.N0
                    for k in self.N0
                    if j == k}

        X = {**X_continuous, **X_binary} # Create the X variables

        Y = master.addVars( # Add assignment variables
            [(i,k)
             for i in self.M
             for k in self.N0], vtype = gb.GRB.BINARY
        )

        C = master.addVars( # Add completion time variables
            [j for j in self.N0], vtype = gb.GRB.CONTINUOUS
        )

        C_max = master.addVar(vtype=gb.GRB.CONTINUOUS) # Add makespan variable

        #10. Objective function
        master.setObjective(C_max, gb.GRB.MINIMIZE)

        #2. Each job assigned exactly to one machine
        for k in self.N:
            master.addConstr(
                gb.quicksum( Y[i,k] for i in self.M ) == 1 
        )
            
        #3. Each job has exactly one predecessor and both of them assigned to the same machine
        for k in self.N:
            for i in self.M:
                master.addConstr(
                    gb.quicksum( X[i,j,k] for j in self.N0 if j != k) == Y[i,k]
                )

        #4. Each job has exactly one successor and both of them assigned to the same machine
        for j in self.N:
            for i in self.M:
                master.addConstr(
                    gb.quicksum( X[i,j,k] for k in self.N0 if k != j ) == Y[i,j]
                )
        #5. At most one job is scheduled as the first job on each machine
        for i in self.M:
            master.addConstr(
                gb.quicksum( X[i,0,k] for k in self.N) <= 1
            )

        #9. Valid inequalities
        for i in self.M:
            master.addConstr(
                gb.quicksum(
                    gb.quicksum((self.setup_times[i,j,k] * X[i,j,k]) for k in self.N)
                    for j in self.N0 if j!= k) +
                gb.quicksum((self.execution_times[i,k] * Y[i,k]) for k in self.N)
                <= C_max
            )
        
        #12. CUTS     
        for h in C_max_h:
            for i in self.M:
                master.addConstr(
                    C_max >= C_max_h[h][i] - gb.quicksum( (1 - Y[i,j]) * theta[h][i,j] 
                                                        for j in N_h[h][i] )
                )

        # Solve the problem
        master.optimize()

        decision_variables = {}
        completion_times = {}
        maximum_makespan = {}
        assignments = {}
            
        for i in self.M:
            for j in self.N0:
                for k in self.N0:
                    decision_variables[i,j,k] = X[i,j,k].X
        for j in self.N0:
            completion_times[j] = C[j].X
        for i in self.M:
            for k in self.N0:
                assignments[i,k] = Y[i,k].X
            
        maximum_makespan = C_max.X    
          
        return decision_variables, assignments, maximum_makespan, master.Status
    