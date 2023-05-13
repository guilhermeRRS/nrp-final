# coding=utf-8
import gurobipy as gp
from gurobipy import GRB

import logging
import sys
from model import NurseModel
from solver import Solver
from chronos import Chronos, ErrorExpectionObj
import sys, os

ORIGIN_MAIN = "ORIGIN_MAIN"

FAILED_TO_SOLVE = "FAILED_TO_SOLVE"
SOLUTION_PRINTING_SUCCESS = "SOLUTION_PRINTING_SUCCESS"
SOLUTION_PRINTING_FAILED = "SOLUTION_PRINTING_FAILED"
SUCCESS_SOLVED = "SUCCESS_SOLVED"
FAILED_TO_SETUP = "FAILED_TO_SETUP"
UNEXPECTED_FAIL = "UNEXPECTED_FAIL"

cluster = len((sys.argv[1:])) == 4

PATH_DATA = "instances/dados/" if cluster else "../instancias/"
PATH_MODEL = "instances/modelos/" if cluster else "../modelos/"
PATH_SAVE_SOLUTION = "z_solutions/"
PAT_LOG = "z_logs/"

instance = str(int((sys.argv[1:])[0]))
timeLimit = int((sys.argv[1:])[1])
description = str(((sys.argv[1:])[2]))
fast = True if str(((sys.argv[1:])[3])) == "1" else False

logging.basicConfig(level=logging.DEBUG, filename=f'{PAT_LOG}{instance}_{description}.log', filemode='w', format='%(message)s')
logging.getLogger("gurobipy.gurobipy").disabled = True

nurse = NurseModel()

chronos = Chronos(timeLimit = 7200)
chronos.startCounter("GET_DATA")
nurse.setPathData(f"{PATH_DATA}Instance{instance}.txt")
chronos.stopCounter()
chronos = Chronos(timeLimit = 7200)
chronos.startCounter("GET_MODEL")
nurse.setPathModel(f"{PATH_MODEL}modelo{instance}.lp")
chronos.stopCounter()

chronos = Chronos(timeLimit = timeLimit)

try:

    nurse.getData()
    nurse.getModel()

    if nurse.s_data and nurse.s_model:
        
        solver = Solver(nurseModel = nurse, chronos = chronos)
        success, nurse = solver.run(fast = fast)

        if success:
            chronos.printMessage(ORIGIN_MAIN, SUCCESS_SOLVED)
            if(nurse.solution.printSolution(f"{PATH_SAVE_SOLUTION}{instance}_{description}.sol", nurse.data.sets)):
                chronos.printMessage(ORIGIN_MAIN, SOLUTION_PRINTING_SUCCESS, False)
            else:
                chronos.printMessage(ORIGIN_MAIN, SOLUTION_PRINTING_FAILED, True)
        else:
            chronos.printMessage(ORIGIN_MAIN, FAILED_TO_SOLVE, True)
        
        chronos.done()

    else:
        chronos.printMessage(ORIGIN_MAIN, FAILED_TO_SETUP, True)

except:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    
    chronos.printMessage(ORIGIN_MAIN, UNEXPECTED_FAIL, True)
    chronos.printObj(ORIGIN_MAIN, UNEXPECTED_FAIL, ErrorExpectionObj(type = exc_type, fname = fname, line = exc_tb.tb_lineno))