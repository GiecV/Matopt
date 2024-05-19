import gurobipy as gb

class Sequence:

    def __init__(self, fixed_assignments):
        self.fixed_assignments = fixed_assignments

    def solve(self):
        
        sequence = gb.Model()
        sequence.Params.OutputFlag = 0 # Avoid verbose output

        X = sequence.addVars( # Add sequence variables
            [(i,j,k) 
             for i in self.M
             for j in self.N0
             for k in self.N0
             if j != k], vtype = gb.GRB.CONTINUOUS
        )

        U = sequence.addVars( # Add assignment variables
            [j for j in self.N0], vtype = gb.GRB.BINARY
        )

        C = sequence.addVars( # Add completion time variables
            [j for j in self.N0], vtype = gb.GRB.CONTINUOUS
        )

        C_max = sequence.addVar(vtype=gb.GRB.CONTINUOUS) # Add makespan variable

        #2. Each job assigned exactly to one machine
        for k in self.N:
            sequence.addConstr(
                gb.quicksum( Y[i,k] for i in self.M ) == 1 
        )
            
        #3. Each job has exactly one predecessor and both of them assigned to the same machine
        for k in self.N:
            for i in self.M:
                sequence.addConstr(
                    gb.quicksum( X[i,j,k] for j in self.N0 if j != k) == Y[i,k]
                )

        #4. Each job has exactly one successor and both of them assigned to the same machine
        for j in self.N:
            for i in self.M:
                sequence.addConstr(
                    gb.quicksum( X[i,j,k] for k in self.N0 if k != j ) == Y[i,j]
                )
        #5. At most one job is scheduled as the first job on each machine
        for i in self.M:
            sequence.addConstr(
                gb.quicksum( X[i,0,k] for k in self.N) <= 1
            )

        # Set U domain
        for j in self.N0:
            sequence.addConstr(
                        U[j] >= 0
            )