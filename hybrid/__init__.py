# coding=utf-8
import json
from chronos import Chronos
from model import NurseModel, Solution, GurobiOptimizedOutput
from typing import List, Dict, NewType
import random
import gurobipy as gp
from gurobipy import GRB

ORIGIN_SOLVER = "ORIGIN_SOLVER"
START_OPTIMIZE = "START_OPTIMIZE"

SOLVER_GUROBI_OUTPUT = "SOLVER_GUROBI_OUTPUT"
SOLVER_ITERATION_NO_SOLUTION = "SOLVER_ITERATION_NO_SOLUTION"
SOLVER_ITERATION_NO_TIME = "SOLVER_ITERATION_NO_TIME"

OneDimInt = NewType("oneDimInt", List[int])
TwoDimInt = NewType("twoDimInt", List[List[int]])
TwoDimVar = NewType("twoDimVar", List[List[gp.Var]])
ThreeDimInt = NewType("threeDimInt", List[List[List[int]]])
ThreeDimVar = NewType("threeDimVar", List[List[List[gp.Var]]])

class penalties:

    numberNurses: TwoDimInt
    demand: int
    preference_total: int

    total: int
    best: int

class tmp:

    zero = 0

class HelperVariables:

    shiftTypeCounter: TwoDimInt
    workloadCounter: OneDimInt
    weekendCounter: TwoDimInt #yes, this is the same as K variable
    projectedX: TwoDimInt

    oneInnerJourney_rt: Dict[int, Dict[int, OneDimInt]]
    twoInnerJourney_rt: Dict[int, Dict[int, TwoDimInt]]

class Hybrid:

    nurseModel: NurseModel
    chronos: Chronos
    helperVariables: HelperVariables
    currentSol: Solution

    #####utils
    from .utils._prePro import preProcessFromSolution
    from .utils._forShifts import computeLt, computeWorkloadNewSeq, shiftFreeMark, shiftFreeUnMark
    from .utils._forShifts import getSequenceWorkMarks, getRangeRewrite

    #####prepare
    from .prepare._calculateHelper import calculateHelper
    from .prepare._setSolToX import solToX
    from .prepare._setSolToParallel import solToParallel
    from .prepare._setBestSolToX import bestSolToX
    from .prepare._setBestAsCurrent import setBestAsCurrent
    
    #####generators
    from .generators._generateSingleNurseModel import generateSingleNurseModel
    from .generators._generateShiftModel import generateShiftModel

    ####maths
    from .maths._forSingle import math_single, math_single_demandDelta
    from .maths._forSingle import math_single_preferenceDelta, math_single_preference
    from .maths._forSingle import math_single_demandDelta, math_single_demand

    from .maths._forSingleMany import math_singleMany, math_singleMany_demand

    from .maths._forSeq import math_sequence
    from .maths._forSeqMany import math_seqMany

    #####options
    from .getters._forSingle import getSingle

    #####fo
    from .foEvaluate._simple import evaluateFO

    #####run
    from .runs._run_single import run_single
    from .runs._run_singleMany import run_singleMany, investigate_singleMany

    from .runs._run_seqFromModel import run_seqFromModel
    from .runs._run_seqNursesFromModel import run_seqNursesFromModel

    from .runs._internal_run_seqFromModel_fixed import internal_run_seqFromModel_fixed

    #####commits
    from .commits._commit_single import commit_single
    from .commits._commit_singleMany import commit_singleMany
    from .commits._commit_seq import commit_sequence
    from .commits._commit_seqMany import commit_sequenceMany

    #####main runner
    from ._mainRunner import main_runSingle, main_runSingleMany, main_seqFromModel,  main_seqNursesFromModel

    from ._manager import startSeqs, startSingles, manager_singleDeep, manager_singleSearch, manager_seqShorterBetter, manager_seqShorterWorser, manager_seqHugeWorser, run_internal_shiftAll, run_internal_innerFix, run_internal_balanced

    def __init__(self, nurseModel: NurseModel, instance, chronos: Chronos):
        
        self.nurseModel = nurseModel
        self.instance = instance
        self.chronos = chronos
        self.helperVariables = HelperVariables()
        self.penalties = penalties()
        self.tmp = tmp()

    
    def run(self, startObj):
        m = self.nurseModel.model.m
        self.startObj = startObj
        self.currentObj = startObj
        self.chronos.startCounter("SETTING_START")
        self.preProcessFromSolution()
        self.SA_shift_model, self.SA_sm_x, self.SA_preference_total, self.SA_demand = self.generateShiftModel()
        self.chronos.stopCounter()
        print("Start working")
        
        self.manager_singleDeep()
        beta = 0.1
        fbeta = 0.1
        numberOfIters = 1000
        numberNurses = 2
        fNumberNurses = 0.25
        keepVND = True
        triesVNDmax = 2
        triesOfFixMax = 10
        while self.chronos.stillValidMIP() and keepVND:
            begginBest = self.penalties.best
            self.setBestAsCurrent()

            #self.manager_seqHugeWorser(beta, numberNurses)
            #self.manager_singleSearch(numberOfIters, numberOfIters*0.01)
            #triesVND = 0
            #while self.chronos.stillValidMIP() and triesVND < triesVNDmax:
            #    self.manager_seqShorterWorser()
            #    self.manager_singleSearch(numberOfIters, numberOfIters*0.025)
            #    triesVND += 1
            #triesVNDmax += 0.5

            if self.chronos.stillValidMIP():
                #input("Shift all")
                self.run_internal_shiftAll(200)
            if self.chronos.stillValidMIP():
                #input("Interanl balanced")
                self.run_internal_balanced(200)

            self.setBestAsCurrent()
            
            triesOfFix = 0
            while self.chronos.stillValidMIP() and triesOfFix < triesOfFixMax:
                #input("Interanl Fix")
                self.nurseModel.model.m.setParam("MIPGap", 1/100)
                self.run_internal_innerFix(200, numberNurses)
                self.nurseModel.model.m.setParam("MIPGap", 1/10000)
                triesOfFix += 1


            beta *= fbeta
            numberNurses += fNumberNurses


            endBest = self.penalties.best

            if begginBest - endBest < 1000:
                if triesOfFixMax < 20:
                    triesOfFixMax += 1

                    triesVND = 0
                    while self.chronos.stillValidMIP() and triesVND < triesVNDmax:
                        self.manager_seqShorterWorser()
                        self.manager_singleSearch(numberOfIters, numberOfIters*0.001)
                        triesVND += 1

                else:
                    #input("Escape")
                    keepVND = False
                
        print("Got in universal improving",keepVND)

        ########################################

        ########## HERE WE FINISH THE ALGORITHM IN ORDER TO LATER PRINT, DONT EDIT IT
        ########## THE TIME COST MAY BE REALY SMALL, SO IT IS FIXED A HUGE TIMELIMIT FOR THE SOLVER

        ########################################
        print("-->",self.startObj, self.penalties.best)
        self.bestSolToX()
        m.setParam("TimeLimit", self.chronos.timeLeft())
        m.setParam("BestObjStop", 0)
        
        m.update()
        self.chronos.startCounter("START_OPTIMIZE_LAST")
        m.optimize()
        self.chronos.stopCounter()

        gurobiReturn = GurobiOptimizedOutput(m)

        self.chronos.printObj(ORIGIN_SOLVER, SOLVER_GUROBI_OUTPUT, gurobiReturn)

        if gurobiReturn.valid():

            self.nurseModel.solution = Solution().getFromX(self.nurseModel.model.x)
            #self.nurseModel.solution = Solution().getFromLb(self.nurseModel.model.x)
            #self.nurseModel.solution.printSolution("failed.sol", self.nurseModel.data.sets)
            self.nurseModel.s_solution = True
            return True, self.nurseModel
        
        else:
            self.nurseModel.solution = Solution().getFromLb(self.nurseModel.model.x)
            self.nurseModel.solution.printSolution("failed.sol", self.nurseModel.data.sets)
            self.chronos.printMessage(ORIGIN_SOLVER, SOLVER_ITERATION_NO_SOLUTION, False)
            
        self.chronos.printMessage(ORIGIN_SOLVER, "NOT_ABLE_TO_SAVE", True)
            
        return False, self.nurseModel