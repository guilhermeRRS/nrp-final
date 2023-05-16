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

class Solver:

    nurseModel: NurseModel
    chronos: Chronos

    def __init__(self, nurseModel: NurseModel, chronos: Chronos):
        self.nurseModel = nurseModel
        self.chronos = chronos

    def run(self, fast:bool = False):
        m = self.nurseModel.model.m
            
        if fast:
            m.setParam("Solutionlimit", 1)
            
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