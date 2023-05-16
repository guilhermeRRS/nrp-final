# coding=utf-8
from chronos import Chronos
from model import NurseModel, Solution, GurobiOptimizedOutput
import gurobipy as gp
from gurobipy import GRB

ORIGIN_SOLVER = "ORIGIN_SOLVER"
START_OPTIMIZE = "START_OPTIMIZE"

SOLVER_GUROBI_OUTPUT = "SOLVER_GUROBI_OUTPUT"
SOLVER_ITERATION_NO_SOLUTION = "SOLVER_ITERATION_NO_SOLUTION"
SOLVER_ITERATION_NO_TIME = "SOLVER_ITERATION_NO_TIME"

class Solvei:

    nurseModel: NurseModel
    chronos: Chronos

    def __init__(self, nurseModel: NurseModel, chronos: Chronos):
        self.nurseModel = nurseModel
        self.chronos = chronos

    def run(self):
        m = self.nurseModel.model.m

        self.chronos.startCounter("START_SETTING_START")
        for i in range(self.nurseModel.I):
            for d in range(self.nurseModel.D):
                for t in range(self.nurseModel.T):
                    self.nurseModel.model.x[i][d][t].Start = self.nurseModel.solution.solution[i][d][t]
        self.chronos.stopCounter()
            
        if self.chronos.stillValidRestrict():
            
            m.setParam("TimeLimit", self.chronos.timeLeft())
            
            m.update()
            self.chronos.startCounter(START_OPTIMIZE)
            m.optimize()
            self.chronos.stopCounter()

            gurobiReturn = GurobiOptimizedOutput(m)

            self.chronos.printObj(ORIGIN_SOLVER, SOLVER_GUROBI_OUTPUT, gurobiReturn)

            if gurobiReturn.valid():

                self.nurseModel.solution = Solution().getFromX(self.nurseModel.model.x)
                self.nurseModel.s_solution = True
                return True, self.nurseModel
            
            else:
                self.chronos.printMessage(ORIGIN_SOLVER, SOLVER_ITERATION_NO_SOLUTION, False)
            
        else:
            self.chronos.printMessage(ORIGIN_SOLVER, SOLVER_ITERATION_NO_TIME, False)
            
        return False, self.nurseModel