# coding=utf-8
import gurobipy as gp
from gurobipy import GRB
from typing import List, NewType
from chronos import *
import io
from ._contract_data import Sets

ThreeDimInt = NewType("ThreeDimInt", List[List[List[int]]]);
ThreeDimVar = NewType("threeDimVar", List[List[List[gp.Var]]]);

class Solution:
    solution: ThreeDimInt

    def loadSolution(self, solution: ThreeDimInt):
        self.solution = solution
        return self

    def printSolution(self, path: str, sets: Sets):
	
        if self.solution:
	    
            path = path
            x = self.solution
	    
            I = len(sets.I)
            D = len(sets.D)
            T = len(sets.T)

            output = ""
            for i in range(I):
                line = ""
                for d in range(D):
                    shift = ""
                    gotAShift = 0
                    for t in range(T):
                        if x[i][d][t] >= 0.5:
                            shift = sets.T[t]
                            gotAShift += 1
                    if gotAShift > 1:
                        raise Exception("There is more")
                    line = line+shift+"\t"
                output = output+line+"\n"
				
            solfile = io.open(path, "w+", encoding = "utf8")
            solfile.write(output)

            return True
		
        return False
    
    def getFromX(self, x: ThreeDimVar):
        solution = []
        I = len(x)
        D = len(x[0])
        T = len(x[0][0])
        for i in range(I):
            solution.append([])
            for d in range(D):
                solution[-1].append([])
                for t in range(T):
                    solution[-1][-1].append(0 if x[i][d][t].x < 0.5 else 1)
                    
        return self.loadSolution(solution)
    
    def getFromLb(self, x: ThreeDimVar):
        solution = []
        I = len(x)
        D = len(x[0])
        T = len(x[0][0])
        for i in range(I):
            solution.append([])
            for d in range(D):
                solution[-1].append([])
                for t in range(T):
                    if x[i][d][t].lb != x[i][d][t].ub:
                        raise Exception("Can't produce solution of not fixed sol")
                    solution[-1][-1].append(0 if x[i][d][t].lb < 0.5 else 1)
                    
        return self.loadSolution(solution)
    
    def generatePartialX(self, success: bool, x: ThreeDimVar, path: str, sets: Sets):
        solution = []
        I = len(x)
        D = len(x[0])
        T = len(x[0][0])
        for i in range(I):
            solution.append([])
            for d in range(D):
                solution[-1].append([])
                for t in range(T):
                    if(success):
                        solution[-1][-1].append([x[i][d][t].vType,x[i][d][t].x,x[i][d][t].lb == x[i][d][t].ub])
                    else:
                        solution[-1][-1].append([x[i][d][t].vType,None,x[i][d][t].lb == x[i][d][t].ub])
        
        output = ""
        for i in range(I):
            line = ""
            for d in range(D):
                shift = self.summarizePartial(solution[i][d], T)
                line = line+shift
            output = output+line+"\n"
            
        solfile = io.open(path, "w+", encoding = "utf8")
        solfile.write(output)

    def summarizePartial(self, solutionBlock, T:int):
        kind = solutionBlock[0][0]
        mixed = True
        rangedContinuous = False
        fixed = True
        for t in range(T):
            if kind != solutionBlock[t][0]:
                mixed = False
            if solutionBlock[t][1] != None:
                if solutionBlock[t][1] > 0.01 and solutionBlock[t][1] < 0.99:
                    rangedContinuous = True
            if not solutionBlock[t][2]:
                fixed = False
        if kind == GRB.CONTINUOUS:
            kind = "C"
        elif kind == GRB.INTEGER:
            kind = "I"
        else:
            kind = "B"
        rangedContinuous = "1" if rangedContinuous else "0"
        fixed = "1" if fixed else "0"
        return f'[{kind},{rangedContinuous},{fixed}]'

    def __str__(self):
        return print_Solution(self)