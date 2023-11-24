# coding=utf-8
import gurobipy as gp
from gurobipy import GRB
from ._contract_data import Data

def _write_model(self, path, data: Data, name = "Model"):

    sets = {}

    sets["I"] = data.sets.I
    sets["D"] = data.sets.D
    sets["T"] = data.sets.T
    sets["W"] = data.sets.W
    sets["R_t"] = data.sets.R_t
    sets["N_i"] = data.sets.N_i
    
    parameters = {}

    parameters["l_t"] = data.parameters.l_t
    parameters["m_max"] = data.parameters.m_max
    parameters["b_min"] = data.parameters.b_min
    parameters["b_max"] = data.parameters.b_max
    parameters["c_min"] = data.parameters.c_min
    parameters["c_max"] = data.parameters.c_max
    parameters["o_min"] = data.parameters.o_min
    parameters["a_max"] = data.parameters.a_max
    parameters["q"] = data.parameters.q
    parameters["p"] = data.parameters.p
    parameters["u"] = data.parameters.u
    parameters["w_min"] = data.parameters.w_min
    parameters["w_max"] = data.parameters.w_max
        
    
    I = len(sets["I"])
    D = len(sets["D"])
    T = len(sets["T"])
    W = len(sets["W"])
    
    m = gp.Model(name)
    
    x = []
    k = []
    y = []
    z = []
    v = []
    for i in range(I):
        x.append([])
        v.append([])
        for d in range(D):
            x[-1].append([])
            v[-1].append([])
            for t in range(T):
                x[-1][-1].append(m.addVar(vtype=GRB.BINARY, name = "x["+str(i)+"]["+str(d)+"]["+str(t)+"]"))
                v[-1][-1].append(m.addVar(vtype=GRB.INTEGER, name = "v["+str(i)+"]["+str(d)+"]["+str(t)+"]"))
                
        k.append([])
        for w in range(W):
            k[-1].append(m.addVar(vtype=GRB.BINARY, name = "k["+str(i)+"]["+str(w)+"]"))
    
    for d in range(D):
        y.append([])
        z.append([])
        for t in range(T):
            y[-1].append(m.addVar(vtype=GRB.INTEGER, name = "y["+str(d)+"]["+str(t)+"]"))
            z[-1].append(m.addVar(vtype=GRB.INTEGER, name = "z["+str(d)+"]["+str(t)+"]"))
    
    for i in range(I):
        for d in range(D - 1):
            m.addConstr(sum(x[i][d][t] for t in range(T)) <= 1, name = "HC1["+str(i)+"]["+str(d)+"]")
            for t1 in range(T):
                m.addConstr(parameters["q"][i][d][t1]*(1 - x[i][d][t1]) + parameters["p"][i][d][t1]*x[i][d][t1] == v[i][d][t1], name = "SC1["+str(i)+"]["+str(d)+"]["+str(t1)+"]")
                for t2 in range(T):
                    if(sets["R_t"][t1][t2]):
                        m.addConstr(x[i][d][t1] + x[i][d+1][t2] <= 1, name = "HC2["+str(i)+"]["+str(d)+"]["+str(t1)+"]["+str(t2)+"]")
                        
        for d in range(D-1,D):
            m.addConstr(sum(x[i][d][t] for t in range(T)) <= 1, name = "HC1["+str(i)+"]["+str(d)+"]")
            for t in range(T):
                m.addConstr(parameters["q"][i][d][t]*(1 - x[i][d][t]) + parameters["p"][i][d][t]*x[i][d][t] == v[i][d][t], name = "SC1["+str(i)+"]["+str(d)+"]["+str(t)+"]")
                        
        for t in range(T):
            m.addConstr(sum(x[i][d][t] for d in range(D)) <= parameters["m_max"][i][t], name = "HC3["+str(i)+"]["+str(t)+"]")
            
        m.addConstr(parameters["b_min"][i] <= sum(x[i][d][t]*parameters["l_t"][t] for d in range(D) for t in range(T)), name = "HC4["+str(i)+"]")
        
        m.addConstr(sum(x[i][d][t]*parameters["l_t"][t] for d in range(D) for t in range(T)) <= parameters["b_max"][i], name = "HC5["+str(i)+"]")
        
        c_max = parameters["c_max"][i]
        for d in range(D-c_max):
            m.addConstr(sum(x[i][j][t] for j in range(d,d+c_max+1) for t in range(T)) <= c_max, name = "HC6["+str(i)+"]["+str(d)+"]")
            
        for c in range(1,parameters["c_min"][i]):
            for d in range(D - c - 1):
                m.addConstr(sum(x[i][d][t] for t in range(T)) + c - 1 - sum(x[i][j][t] for t in range(T) for j in range(d + 1, d + c + 1)) + sum(x[i][d+c+1][t] for t in range(T)) >= 0, name = "HC7["+str(i)+"]["+str(c)+"]["+str(d)+"]")
                
        for b in range(1,parameters["o_min"][i]):
            for d in range(D - b - 1):
                m.addConstr(1 - sum(x[i][d][t] for t in range(T)) + sum(x[i][j][t] for t in range(T) for j in range(d + 1, d + b + 1)) - sum(x[i][d+b+1][t] for t in range(T)) >= 0, name = "HC8["+str(i)+"]["+str(b)+"]["+str(d)+"]")
                
        for w in range(W):
            m.addConstr(k[i][w] <= sum(x[i][7*(w+1)-2][t] for t in range(T)) + sum(x[i][7*(w+1)-1][t] for t in range(T)), name = "HC9a["+str(i)+"]["+str(w)+"]")
            m.addConstr(sum(x[i][7*(w+1)-2][t] for t in range(T)) + sum(x[i][7*(w+1)-1][t] for t in range(T)) <= 2*k[i][w], name = "HC9b["+str(i)+"]["+str(w)+"]")
            
        m.addConstr(sum(k[i][w] for w in range(W)) <= parameters["a_max"][i], name = "HC9c["+str(i)+"]["+str(w)+"]")
        
        for d in sets["N_i"][i]:
            for t in range(T):
                m.addConstr(x[i][d][t] == 0, name = "HC10["+str(i)+"]["+str(d)+"]["+str(t)+"]")
            
    for d in range(D):
        for t in range(T):
            m.addConstr(sum(x[i][d][t] for i in range(I)) - z[d][t] + y[d][t] == parameters["u"][d][t], name = "SC2["+str(i)+"]["+str(d)+"]["+str(t)+"]")
    
    #Objetivo
    m.setObjective(sum(v[i][d][t] for i in range(I) for d in range(D) for t in range(T)) + sum(y[d][t]*parameters["w_min"][d][t] for d in range(D) for t in range(T)) + sum(z[d][t]*parameters["w_max"][d][t] for d in range(D) for t in range(T)), GRB.MINIMIZE)
    

    try:
        m.write(path)
    except:
        return False
    return True