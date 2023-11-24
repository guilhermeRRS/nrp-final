# coding=utf-8
import gurobipy as gp
from gurobipy import GRB
import random
import logging
import sys
from model import NurseModel
from hybridUltimate import Hybrid
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

bestTimes = [0.075, 0.121, 0.207, 0.146, 0.256, 0.334, 0.344, 0.56, 0.645, 0.847, 1.245, 0.199, 8.528, 1.199, 1.741, 0.655, 1.175, 1.122, 2.554, 8.055, 16.07, 20.81, 93.818, 300.149]
objs = [1733,3695,6224,6948,8583,10739,12343,20660,16631,24489,32164,55234,103182,25916,51909,21424,38522,35089,63766,213777,420432,539844,937751,1480537]

PATH_DATA = "instances/dados/" if cluster else "instancias/"
PATH_MODEL = "instances/modelos/" if cluster else "modelos/"
PATH_INITIAL = "instances/initial/" if cluster else "initial/"
PATH_SAVE_SOLUTION = "z_solutions/"
PAT_LOG = "z_logs/"

instance = str(int((sys.argv[1:])[0]))
timeLimit = int((sys.argv[1:])[1])
seed = int((sys.argv[1:])[2])
description = str(((sys.argv[1:])[3]))

random.seed(seed)

logging.basicConfig(level=logging.DEBUG, filename=f'{PAT_LOG}{instance}_{description}.log', filemode='w', format='%(message)s')
logging.getLogger("gurobipy.gurobipy").disabled = True

nurse = NurseModel()

nurse.setPathData(f"{PATH_DATA}Instance{instance}.txt")
nurse.setPathModel(f"{PATH_MODEL}modelo{instance}.lp")
nurse.setPathSolution(f"{PATH_INITIAL}{instance}.sol")

chronos = Chronos(timeLimit = (timeLimit - bestTimes[int(instance)-1]))
#chronos = Chronos(timeLimit = timeLimit)


if True:

    nurse.getData()
    nurse.getModel()
    nurse.getSolution()

    if nurse.s_data and nurse.s_model and nurse.s_solution:
        hybrid = Hybrid(nurseModel = nurse, instance = instance, chronos = chronos)

        success, nurse = hybrid.run(objs[int(instance)-1], numberOfNurses_fixDay = 6*0.02, numberOfNurses_fixNurse = 2*0.02, numberOfDays = 0.01)

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

else:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    
    chronos.printMessage(ORIGIN_MAIN, UNEXPECTED_FAIL, True)
    chronos.printObj(ORIGIN_MAIN, UNEXPECTED_FAIL, ErrorExpectionObj(type = exc_type, fname = fname, line = exc_tb.tb_lineno))