# coding=utf-8
import gurobipy as gp
from gurobipy import GRB

def setDays(self, m, dm_x, minimumNumberOfDays, maximumNumberOfDays):

    numberOfDays = 0
    
    numberOfDaysConstraint_min = m.addConstr(minimumNumberOfDays <= gp.quicksum(dm_x[j] for j in range(self.nurseModel.D)))
    numberOfDaysConstraint_max = m.addConstr(gp.quicksum(dm_x[j] for j in range(self.nurseModel.D)) <= maximumNumberOfDays)
    
    
    if not self.chronos.stillValidRestrict():
        return -1

    m.update()
    m.optimize()
    
    m.remove(numberOfDaysConstraint_min)
    m.remove(numberOfDaysConstraint_max)
    
    if m.SolCount == 0:
        return -1
            
    return m.objVal
        
def setShifts(self, m, sm_x, dm_x, i:int = -1):

    numberOfHours = 0
    
    constraintsToDelete = []
    for j in range(self.nurseModel.D):
        constraintsToDelete.append(m.addConstr(gp.quicksum(sm_x[j][k] for k in range(self.nurseModel.T)) == (1 if dm_x[j].x >= 0.5 else 0)))
    
    if i != -1:
        #H10
        for j in range(len(self.nurseModel.data.sets.N_i[i])):
            constraintsToDelete.append(m.addConstr(gp.quicksum(sm_x[self.nurseModel.data.sets.N_i[i][j]][k] for k in range(self.nurseModel.T)) == 0))
        #HC4, HC5
        constraintsToDelete.append(m.addConstr(self.nurseModel.data.parameters.b_min[i] <= gp.quicksum(sm_x[j][k]*self.nurseModel.data.parameters.l_t[k] for j in range(self.nurseModel.D) for k in range(self.nurseModel.T))))
        constraintsToDelete.append(m.addConstr(gp.quicksum(sm_x[j][k]*self.nurseModel.data.parameters.l_t[k] for j in range(self.nurseModel.D) for k in range(self.nurseModel.T)) <= self.nurseModel.data.parameters.b_max[i]))
    
    if not self.chronos.stillValidRestrict():
        return -1

    m.update()
    m.optimize()
    
    for constraintToDelete in constraintsToDelete:
        m.remove(constraintToDelete)
    
    if m.SolCount == 0:
        return -1
            
    return m.objVal