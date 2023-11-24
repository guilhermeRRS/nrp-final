# coding=utf-8
import gurobipy as gp
from gurobipy import GRB

import logging
import sys
from model import NurseModel
from conquer import Conquer
from chronos import Chronos, ErrorExpectionObj
import sys, os

#error messages
ORIGIN_MAIN = "ORIGIN_MAIN"

FAILED_TO_SOLVE = "FAILED_TO_SOLVE"
SOLUTION_PRINTING_SUCCESS = "SOLUTION_PRINTING_SUCCESS"
SOLUTION_PRINTING_FAILED = "SOLUTION_PRINTING_FAILED"
SUCCESS_SOLVED = "SUCCESS_SOLVED"
FAILED_TO_SETUP = "FAILED_TO_SETUP"
UNEXPECTED_FAIL = "UNEXPECTED_FAIL"

#if we are running in a cluster only the needed parameters are send. otherwise, a fool parameter is sent
cluster = len((sys.argv[1:])) == 3

#the path to files changes whether you are running locally or in a cluster
PATH_DATA = "instances/dados/" if cluster else "instancias/"
PATH_MODEL = "instances/modelos/" if cluster else "modelos/"
PATH_SAVE_SOLUTION = "z_solutions/"
PAT_LOG = "z_logs/"

#the meaningful parameters are: instance number, the time limit (in seconds), the description of the test (change it to label different tests according to configs/heuristical seed you are using)
instance = str(int((sys.argv[1:])[0]))
timeLimit = int((sys.argv[1:])[1])
description = str(((sys.argv[1:])[2]))

logging.basicConfig(level=logging.DEBUG, filename=f'{PAT_LOG}{instance}_{description}.log', filemode='w', format='%(message)s')
logging.getLogger("gurobipy.gurobipy").disabled = True

nurse = NurseModel()

#before running the 
chronos = Chronos(timeLimit = timeLimit)
chronos.startCounter("SET_DATAPATH")
nurse.setPathData(f"{PATH_DATA}Instance{instance}.txt")
chronos.stopCounter()
chronos.startCounter("SET_MODELPATH")
nurse.setPathModel(f"{PATH_MODEL}modelo{instance}.lp")
chronos.stopCounter()

nurse.getData()

if nurse.s_data:

    nurse._write_model(path = f"{PATH_MODEL}modelo{instance}.lp", data = nurse.data)
    nurse.getModel()

    if nurse.s_model:
        conquer = Conquer(nurseModel = nurse, chronos = chronos)
        success, nurse = conquer.run()

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
