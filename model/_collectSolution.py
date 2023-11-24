# coding=utf-8
import io, logging
from typing import Union
from ._contract_data import Data
from ._contract_solution import Solution

'''
This function is responsable for collecting a solution, saved in a file as if it would be tested in RosterViewer

ANY BROKEN SOLTUION (NOT FOLLOWING THE 'STANDARDS') WILL CAUSE UNEXPECTED BEHAVIOR

'''

def readFile(path):
    sucess = True
    fileConteds = []

    try:	
        with io.open(path, "r", encoding = "utf8") as file:		
            fileConteds = file.read()
    except:
        sucess = False
        logging.exception("File not found "+path)
        
    return sucess, fileConteds
    
def _get_solution(self, path, data: Data):

    solution = []
    
    sucess, fileConteds	= readFile(path)
    if(sucess):
    
        I = len(data.sets.I)
        D = len(data.sets.D)
        T = len(data.sets.T)

        fileConteds = fileConteds.split("\n")
        
        if len(fileConteds) < I:
            sucess = False
        
        if sucess:
        
            for i in range(I):
                solution.append([])
                line = fileConteds[i].split("\t")
                for d in range(D):
                    solution[-1].append([])
                    for t in range(T):
                        solution[-1][-1].append(0)
                    if line[d] != "":
                        solution[-1][-1][data.sets.T.index(line[d])] = 1
        
            return sucess, Solution().loadSolution(solution)
        
    return sucess, None