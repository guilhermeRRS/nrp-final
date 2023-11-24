# coding=utf-8
from chronos import Chronos
from interface import MipInterface
from model import GurobiOptimizedOutput, NurseModel, Solution
import math
import gurobipy as gp
from gurobipy import GRB

ORIGIN_RELAX = "ORIGIN_RELAX"

START_ITERATION = "START_ITERATION"
SOLVER_GUROBI_OUTPUT = "SOLVER_GUROBI_OUTPUT"
SOLVER_ITERATION_NO_SOLUTION = "SOLVER_ITERATION_NO_SOLUTION"
SOLVER_ITERATION_NO_TIME = "SOLVER_ITERATION_NO_TIME"

class Conquer(MipInterface):

    from ._utils import get_extremeShifts
    from ._heuristicsSetters import setDays, setShifts
    from ._createModels import create_days_model, create_clean_days_model, create_shift_model, create_clean_shift_model

    chronos: Chronos

    def __init__(self, nurseModel: NurseModel, chronos: Chronos):
        super().__init__(nurseModel.model)

        self.nurseModel = nurseModel
        self.chronos = chronos

    cleanHistoryDayModel = {}
    cleanHistoryShiftModel = []

    def run(self):
        
        success = True
        m = self.nurseModel.model.m
        
        self.chronos.startCounter("CREATE_SHIFT_MODEL")
        shift_model, sm_x = self.create_clean_shift_model(self.nurseModel.data.sets, self.nurseModel.data.parameters)
        self.cleanHistoryShiftModel = [shift_model, sm_x]
        self.chronos.stopCounter()

        currentNurse = 0
        tries = 0
        while currentNurse < self.nurseModel.I and self.chronos.stillValidRestrict() and success:

            characteristics = [self.nurseModel.data.parameters.c_min[currentNurse], self.nurseModel.data.parameters.o_min[currentNurse]]
            if not (str(characteristics) in self.cleanHistoryDayModel.keys()):
                self.chronos.startCounter(f"CREATING_DAYS_MODEL {str(characteristics)}")
                days_model, dm_x, dm_k = self.create_clean_days_model(characteristics[0], characteristics[1], self.nurseModel.data.sets, self.nurseModel.data.parameters)
                self.cleanHistoryDayModel[str(characteristics)] = [days_model, dm_x, dm_k]
                self.chronos.stopCounter()
            characteristics = str(characteristics)
            
            self.chronos.startCounter(f"NURSE_GENERATION {currentNurse}")
            success, constraintsDay, constraintsShift, triesNurse = self.generateNurse(currentNurse, characteristics)
            self.chronos.stopCounter()

            self.chronos.startCounter("CLEANING_CONSTRAINT")
            for contraintShift in constraintsShift:
                self.cleanHistoryShiftModel[0].remove(contraintShift)
            for constraintDay in constraintsDay:
                self.cleanHistoryDayModel[characteristics][0].remove(constraintDay)
            self.chronos.stopCounter()
            currentNurse += 1
            tries += triesNurse
            
        if self.chronos.stillValidRestrict() and success:
            
            m.update()

            m.setParam("TimeLimit", self.chronos.timeLeft())
            m.setParam("Solutionlimit", 1)
            
            m.optimize()

            gurobiReturn = GurobiOptimizedOutput(m)
            self.chronos.printObj("ORIGIN_CONQUER", "SOLVER_GUROBI_OUTPUT", gurobiReturn)

            if gurobiReturn.valid() and currentNurse == self.nurseModel.I:

                self.nurseModel.solution = Solution().getFromX(self.nurseModel.model.x)
                self.nurseModel.s_solution = True
                return True, self.nurseModel

        return False, self.nurseModel
        
    def generateNurse(self, currentNurse, characteristics):

        success = False
        shortestShiftSize, longestShiftSize = self.get_extremeShifts(currentNurse)

        self.chronos.startCounter("CONFIG_DAY_MODEL")
        constraintsDay, days_model, dm_x = self.create_days_model(self.cleanHistoryDayModel[characteristics][0], self.cleanHistoryDayModel[characteristics][1], self.cleanHistoryDayModel[characteristics][2], currentNurse, self.nurseModel.data.sets, self.nurseModel.data.parameters)
        self.chronos.stopCounter()
        days_model.setParam('Solutionlimit', 1)
        days_model.setParam('OutputFlag', 0)

        self.chronos.startCounter("CONFIG_SHIFT_MODEL")
        constraintsShift, shift_model, sm_x = self.create_shift_model(self.cleanHistoryShiftModel[0], self.cleanHistoryShiftModel[1], currentNurse, self.nurseModel.data.sets, self.nurseModel.data.parameters)
        self.chronos.stopCounter()
        shift_model.setParam('Solutionlimit', 1)
        shift_model.setParam('OutputFlag', 0)
        
        minimumNumberOfDays = math.ceil(self.nurseModel.data.parameters.b_min[currentNurse]/longestShiftSize)
        maximumNumberOfDays = math.floor(self.nurseModel.data.parameters.b_max[currentNurse]/shortestShiftSize)
        
        zero_minimumNumberOfDays = minimumNumberOfDays
        zero_maximumNumberOfDays = maximumNumberOfDays

        minimumNumberOfDays = maximumNumberOfDays#min(math.floor(1.1*minimumNumberOfDays), zero_maximumNumberOfDays)
        #maximumNumberOfDays = min(math.floor(0.9*maximumNumberOfDays), zero_minimumNumberOfDays)

        tries = 0
        while self.chronos.stillValidRestrict() and not success:
            tries += 1
            days_model.setParam("Timelimit", self.chronos.timeLeft())
            self.chronos.startCounter("SET_DAYS")
            numberOfDays = self.setDays(days_model, dm_x, minimumNumberOfDays, maximumNumberOfDays)
            self.chronos.stopCounter()
            
            if numberOfDays > -1 and self.chronos.stillValidRestrict():
                days_model.setParam("Timelimit", self.chronos.timeLeft())
                self.chronos.startCounter("SET_SHIFTS")
                numberOfHours = self.setShifts(shift_model, sm_x, dm_x)
                self.chronos.stopCounter()
				
                if numberOfHours > -1:
                    success = True
                    for d in self.nurseModel.data.sets.D:
                        for t in range(len(self.nurseModel.data.sets.T)):
                            self.nurseModel.model.x[currentNurse][d][t].lb = sm_x[d][t].x
                            self.nurseModel.model.x[currentNurse][d][t].ub = sm_x[d][t].x
                    break

                else:
                    if numberOfHours < self.nurseModel.data.parameters.b_min[currentNurse]:
                        minimumNumberOfDays += 0.25
                    else:
                        maximumNumberOfDays += 0.25

            else:
                minimumNumberOfDays = max(zero_minimumNumberOfDays, minimumNumberOfDays-1)
                maximumNumberOfDays = min(zero_maximumNumberOfDays, maximumNumberOfDays+1)
        
        return success, constraintsDay, constraintsShift, tries