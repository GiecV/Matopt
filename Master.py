import gurobipy as gb

class Master:
    
    def __init__(self, execution_times, setup_times, M, N, N0, C_max_h, thetas, N_h):
        self.execution_times = execution_times
        self.setup_times = setup_times
        self.M = M
        self.N = N
        self.N0 = N0
        self.C_max_h = C_max_h
        self.thetas = thetas
        self.N_h = N_h

    def get_theta(self):
        return self.thetas

    def solve(self):
        master = gb.Model()
        master.Params.OutputFlag = 0 # Avoid verbose output

        X = master.addVars( # Add sequence variables
            [(i,j,k) 
             for i in self.M
             for j in self.N0
             for k in self.N0], vtype = gb.GRB.CONTINUOUS
        )

        Y = master.addVars( # Add assignment variables
            [(i,k)
             for i in self.M
             for k in self.N0], vtype = gb.GRB.BINARY
        )

        C = master.addVars( # Add completion time variables
            [j for j in self.N0], vtype = gb.GRB.CONTINUOUS
        )

        C_max = master.addVar(vtype=gb.GRB.CONTINUOUS) # Add makespan variable

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
        for h in self.thetas:
            for i in self.M:
                if not self.N_h[h][i] == []:
                    master.addConstr(
                        self.C_max_h[h][i] - 
                        gb.quicksum((1 - Y[i,j]) * self.thetas[h][i,j] for j in self.N_h[h][i]) <= C_max
                    )

        #13. Integrality relaxation

        for i in self.M:
            for j in self.N0:
                for k in self.N0:
                    master.addConstr(
                        X[i,j,k] >= 0
                    )
                    master.addConstr(
                        X[i,j,k] <= 1
                    )

        # Solve the problem
        master.optimize()

        # Save the results if the problem is feasible, otherwise return None
        if master.Status == gb.GRB.OPTIMAL:

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
                    

            return decision_variables,completion_times,maximum_makespan,assignments, True
        else: return None

    def compute_thetas(self, assignments, setup_times):

        thetas = {}
        for i in self.M:
            for j in self.N: #! FORSE N0
                max_setup_time = 0
                for k in self.N:
                    if assignments[i,j] == 1: #!forse i,k
                        if setup_times[i,j,k] > max_setup_time:
                                max_setup_time = setup_times[i,j,k]
                thetas[i,j] = self.execution_times[i,j] + max_setup_time
        return thetas

    def compute_C_max(self, assignments, completion_times):

        machines_and_times = {}
        C_max_h = {}

        for i in self.M:
            machines_and_times[i] = []
            for k in self.N:
                if assignments[i,k] == 1:
                    machines_and_times[i].append(k)

        for key in self.M:
            maximum = 0
            for item in machines_and_times[key]:
                if completion_times[key, item] > maximum:
                    maximum = completion_times[key, item]
            
            C_max_h[key] = maximum

        return C_max_h

    def compute_N_h(self, assignments):

        jobs_at_each_machine = {}
        for i in self.M:
            jobs_at_each_machine[i] = []
            for k in self.N:
                if assignments[i,k] == 1:
                    jobs_at_each_machine[i].append(k)
        return jobs_at_each_machine

    