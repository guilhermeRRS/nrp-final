# coding=utf-8
import gurobipy as gp
from gurobipy import GRB

def generateSingleNurseModel(self, nurse:int):

    sets = {}

    sets["D"] = self.nurseModel.data.sets.D
    sets["T"] = self.nurseModel.data.sets.T
    sets["W"] = self.nurseModel.data.sets.W
    sets["R_t"] = self.nurseModel.data.sets.R_t
    sets["N_i"] = self.nurseModel.data.sets.N_i
    
    parameters = {}

    parameters["l_t"] = self.nurseModel.data.parameters.l_t
    parameters["m_max"] = self.nurseModel.data.parameters.m_max
    parameters["b_min"] = self.nurseModel.data.parameters.b_min
    parameters["b_max"] = self.nurseModel.data.parameters.b_max
    parameters["c_min"] = self.nurseModel.data.parameters.c_min
    parameters["c_max"] = self.nurseModel.data.parameters.c_max
    parameters["o_min"] = self.nurseModel.data.parameters.o_min
    parameters["a_max"] = self.nurseModel.data.parameters.a_max
    parameters["q"] = self.nurseModel.data.parameters.q
    parameters["p"] = self.nurseModel.data.parameters.p
    parameters["u"] = self.nurseModel.data.parameters.u
    parameters["w_min"] = self.nurseModel.data.parameters.w_min
    parameters["w_max"] = self.nurseModel.data.parameters.w_max
        
    
    D = len(sets["D"])
    T = len(sets["T"])
    W = len(sets["W"])
    
    m = gp.Model(f"Nurse {nurse}")
    
    x = []
    k = []
    
    for d in range(D):
        x.append([])
        for t in range(T):
            x[-1].append(m.addVar(vtype=GRB.BINARY))

            if parameters["m_max"][nurse][t] == 0:
                m.addConstr(x[d][t] == 0)
        m.addConstr(sum(x[d][t] for t in range(T)) <= 1)
            
    for w in range(W):
        k.append(m.addVar(vtype=GRB.BINARY))
    
    for d in range(D - 1):
        for t1 in range(T):
            if parameters["m_max"][nurse][t1] > 0:
                for t2 in range(T):
                    if(sets["R_t"][t1][t2]):
                        m.addConstr(x[d][t1] + x[d+1][t2] <= 1)
                    
    for t in range(T):
        m.addConstr(sum(x[d][t] for d in range(D)) <= parameters["m_max"][nurse][t])
        
    m.addConstr(parameters["b_min"][nurse] <= sum(x[d][t]*parameters["l_t"][t] for d in range(D) for t in range(T)))
    
    m.addConstr(sum(x[d][t]*parameters["l_t"][t] for d in range(D) for t in range(T)) <= parameters["b_max"][nurse])
    
    c_max = parameters["c_max"][nurse]
    for d in range(D-c_max):
        m.addConstr(sum(x[j][t] for j in range(d,d+c_max+1) for t in range(T)) <= c_max)
        
    for c in range(1,parameters["c_min"][nurse]):
        for d in range(D - c - 1):
            m.addConstr(sum(x[d][t] for t in range(T)) + c - 1 - sum(x[j][t] for t in range(T) for j in range(d + 1, d + c + 1)) + sum(x[d+c+1][t] for t in range(T)) >= 0)
            
    for b in range(1,parameters["o_min"][nurse]):
        for d in range(D - b - 1):
            m.addConstr(1 - sum(x[d][t] for t in range(T)) + sum(x[j][t] for t in range(T) for j in range(d + 1, d + b + 1)) - sum(x[d+b+1][t] for t in range(T)) >= 0)
            
    for w in range(W):
        m.addConstr(k[w] <= sum(x[7*(w+1)-2][t] for t in range(T)) + sum(x[7*(w+1)-1][t] for t in range(T)))
        m.addConstr(sum(x[7*(w+1)-2][t] for t in range(T)) + sum(x[7*(w+1)-1][t] for t in range(T)) <= 2*k[w])
        
    m.addConstr(sum(k[w] for w in range(W)) <= parameters["a_max"][nurse])
    
    for d in sets["N_i"][nurse]:
        for t in range(T):
            m.addConstr(x[d][t] == 0)
            

    return m, x