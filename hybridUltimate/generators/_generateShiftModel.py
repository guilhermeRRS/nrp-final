# coding=utf-8
import gurobipy as gp
from gurobipy import GRB

def generateShiftModel(self):

    sets = self.nurseModel.data.sets
    parameters = self.nurseModel.data.parameters
    
    I = len(sets.I)
    D = len(sets.D)
    T = len(sets.T)

    shift_model = gp.Model()
    sm_x = [[[shift_model.addVar(vtype=GRB.BINARY) for k in range(len(sets.T))] for j in range(len(sets.D))] for i in range(len(sets.I))]
    v = [[[shift_model.addVar(vtype=GRB.INTEGER) for k in range(len(sets.T))] for j in range(len(sets.D))] for i in range(len(sets.I))]
    z = [[shift_model.addVar(vtype=GRB.INTEGER) for k in range(len(sets.T))] for j in range(len(sets.D))]
    y = [[shift_model.addVar(vtype=GRB.INTEGER) for k in range(len(sets.T))] for j in range(len(sets.D))]    

    demand = shift_model.addVar(vtype=GRB.INTEGER)
    preference_total = shift_model.addVar(vtype=GRB.INTEGER)

    for i in range(len(sets.I)):
    
        shift_model.addConstr(parameters.b_min[i] <= gp.quicksum(sm_x[i][j][k]*parameters.l_t[k] for j in range(len(sets.D)) for k in range(len(sets.T))))
        shift_model.addConstr(gp.quicksum(sm_x[i][j][k]*parameters.l_t[k] for j in range(len(sets.D)) for k in range(len(sets.T))) <= parameters.b_max[i])
        
        for j in range(len(sets.D) - 1):
            for k in range(len(sets.T)):
                shift_model.addConstr(parameters.q[i][j][k]*(1 - sm_x[i][j][k]) + parameters.p[i][j][k]*sm_x[i][j][k] == v[i][j][k])

                if parameters.m_max[i][k] == 0:
                    shift_model.addConstr(sm_x[i][j][k] == 0)
                else:
                    for l in range(len(sets.T)):
                        if(sets.R_t[k][l]):
                            shift_model.addConstr(sm_x[i][j][k] + sm_x[i][j+1][l] <= 1)
    
        d = len(sets.D) - 1
        for k in range(len(sets.T)):
            shift_model.addConstr(parameters.q[i][d][k]*(1 - sm_x[i][d][k]) + parameters.p[i][d][k]*sm_x[i][d][k] == v[i][d][k])
            if parameters.m_max[i][k] == 0:
                shift_model.addConstr(sm_x[i][d][k] == 0)
                
            shift_model.addConstr(gp.quicksum(sm_x[i][j][k] for j in range(len(sets.D))) <= parameters.m_max[i][k])
	
    for d in range(D):
        for t in range(T):
            shift_model.addConstr(sum(sm_x[i][d][t] for i in range(I)) - z[d][t] + y[d][t] == parameters.u[d][t])

    shift_model.addConstr(sum(v[i][d][t] for i in range(I) for d in range(D) for t in range(T)) == preference_total)
    shift_model.addConstr(sum(y[d][t]*parameters.w_min[d][t] for d in range(D) for t in range(T)) + sum(z[d][t]*parameters.w_max[d][t] for d in range(D) for t in range(T)) == demand)
    
    shift_model.setObjective(preference_total + demand, GRB.MINIMIZE)
    

    return shift_model, sm_x, preference_total, demand