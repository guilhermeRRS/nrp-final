# coding=utf-8
import gurobipy as gp
from gurobipy import GRB

def create_days_model(self, days_model, dm_x, dm_k, i, sets, parameters):

	constraintsDay = []

	#HC6
	for d in range(len(sets.D) - parameters.c_max[i]):
		constraintsDay.append(days_model.addConstr(gp.quicksum(dm_x[d+j] for j in range(parameters.c_max[i] + 1)) <= parameters.c_max[i]))
				
	for j in range(1, 1 + len(sets.W)):
		constraintsDay.append(days_model.addConstr(dm_k[j-1] <= dm_x[7*j-1-1] + dm_x[7*j-1]))
		constraintsDay.append(days_model.addConstr(dm_x[7*j-1-1] + dm_x[7*j-1] <= 2*dm_k[j-1]))
	constraintsDay.append(days_model.addConstr(gp.quicksum(dm_k[j] for j in range(len(sets.W))) <= parameters.a_max[i]))
		
	for j in range(len(sets.N_i[i])):
		constraintsDay.append(days_model.addConstr(dm_x[sets.N_i[i][j]] == 0))

	return constraintsDay, days_model, dm_x

def create_clean_days_model(self, c_min, o_min, sets, parameters):

	days_model = gp.Model()

	dm_x = [days_model.addVar(vtype=GRB.BINARY, name = "x["+str(j)+"]") for j in range(len(sets.D))]
	dm_k = [days_model.addVar(vtype=GRB.BINARY, name = "k["+str(sets.W[j])+"]") for j in range(len(sets.W))]
		
	#HC7
	for c in range(1, c_min):
		for d in range(len(sets.D) - c - 1):
			j = d + 1
			days_model.addConstr(dm_x[d] + c - 1 - gp.quicksum(dm_x[m] for m in range(j, d + c +1)) + dm_x[d+c+1] >= 0)
				
	#HC8
	for b in range(1, o_min):
		for d in range(len(sets.D) - b - 1):
			j = d + 1
			days_model.addConstr(1 - dm_x[d] + gp.quicksum(dm_x[m] for m in range(j, d + b +1)) - dm_x[d+b+1] >= 0)
			
	#FO -> saves the number of days working
	days_model.setObjective(gp.quicksum(dm_x[d] for d in range(len(sets.D))), GRB.MINIMIZE)

	return days_model, dm_x, dm_k
	
def create_shift_model(self, shift_model, sm_x, i, sets, parameters, garantee:bool = False):

	constraintsShift = []

	#HC3
	for k in range(len(sets.T)):
		constraintsShift.append(shift_model.addConstr(gp.quicksum(sm_x[j][k] for j in range(len(sets.D))) <= parameters.m_max[i][k]))
	
	#HC4, HC5
	constraintsShift.append(shift_model.addConstr(parameters.b_min[i] <= gp.quicksum(sm_x[j][k]*parameters.l_t[k] for j in range(len(sets.D)) for k in range(len(sets.T)))))
	constraintsShift.append(shift_model.addConstr(gp.quicksum(sm_x[j][k]*parameters.l_t[k] for j in range(len(sets.D)) for k in range(len(sets.T))) <= parameters.b_max[i]))
	
	return constraintsShift, shift_model, sm_x
	
def create_clean_shift_model(self, sets, parameters):

	shift_model = gp.Model()
	sm_x = [[shift_model.addVar(vtype=GRB.BINARY, name = "x["+str(j)+"]["+sets.T[k]+"]") for k in range(len(sets.T))] for j in range(len(sets.D))]
	
	#HC2
	for j in range(len(sets.D) - 1):
		for k in range(len(sets.T)):
			for l in range(len(sets.T)):
				if(sets.R_t[k][l]):
					shift_model.addConstr(sm_x[j][k] + sm_x[j+1][l] <= 1)
			
	#FO -> saves the workload
	shift_model.setObjective(gp.quicksum(sm_x[j][k]*parameters.l_t[k] for j in range(len(sets.D)) for k in range(len(sets.T))), GRB.MINIMIZE)
		
	return shift_model, sm_x