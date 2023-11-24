import gurobipy as gp
from gurobipy import GRB

def get_extremeShifts(self, nurse):

    allowed_l_t = []
    for i in range(self.nurseModel.T):
        if self.nurseModel.data.parameters.m_max[nurse][i] > 0:
            allowed_l_t.append(self.nurseModel.data.parameters.l_t[i])

    shortestShiftSize = min(allowed_l_t)
    longestShiftSize = max(allowed_l_t)
    return shortestShiftSize, longestShiftSize
