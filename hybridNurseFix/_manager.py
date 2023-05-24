import math
import random

from model import GurobiOptimizedOutput


def startSingles(self):
    self.solToX()
    self.calculateHelper()

def startSeqs(self):
    self.solToParallel()
    self.calculateHelper()

def manager_singleDeep(self):
    self.startSingles()

    numberOfIters = 10000
    keepsDiving = True
    while self.chronos.stillValidMIP() and keepsDiving:
        numberSuccess = 0
        for i in range(numberOfIters):
            s, move = self.run_single(worse = False, better = True, equal = False)

            if s:
                self.commit_single(move)
                self.chronos.printMessage("11", self.penalties.total)
                print("11", self.penalties.total, self.penalties.best)
                if self.penalties.total < self.penalties.best:
                    self.penalties.best = self.penalties.total
                    for i in range(self.nurseModel.I):
                        for d in range(self.nurseModel.D):
                            for t in range(self.nurseModel.T):
                                self.tmpBestSol.solution[i][d][t] = self.currentSol.solution[i][d][t]
                numberSuccess += 1
                
            if not self.chronos.stillValidMIP():
                keepsDiving = False
                break

        print("11", numberSuccess)
        if numberSuccess < 2:
            keepsDiving = False

def manager_singleSearch(self, numberOfIters, tol):
    self.startSingles()

    optionsNumberNurses = [2, 3, 4]

    numberNurses = list(dict.fromkeys(optionsNumberNurses))
    
    keepsDiving = True
    totalNumberOfSucces = 0
    while self.chronos.stillValidMIP() and keepsDiving:
        totalNumberOfSucces = 0
        for numberNurses in optionsNumberNurses:
            numberSuccess = 0
            for i in range(numberOfIters):
                
                s, move = self.run_singleMany(numberOfNurses = numberNurses, worse = False, better = True, equal = True)
                
                if s:
                    newObj = move["nD"] + move["nP"]
                    if newObj < self.penalties.total:
                        numberSuccess += 1
                        
                    self.commit_singleMany(move)
                    print("1S", self.penalties.total, self.penalties.best)
                    self.chronos.printMessage("1S", self.penalties.total)

                    if newObj < self.penalties.best:
                        self.penalties.best = newObj
                        for i in range(self.nurseModel.I):
                            for d in range(self.nurseModel.D):
                                for t in range(self.nurseModel.T):
                                    self.tmpBestSol.solution[i][d][t] = self.currentSol.solution[i][d][t]
                                    
                if not self.chronos.stillValidMIP():
                    break
            print("1S", numberNurses, numberSuccess)
            totalNumberOfSucces += numberSuccess
            if not self.chronos.stillValidMIP():
                break
        
        print("1S.", totalNumberOfSucces)
        if totalNumberOfSucces < tol:
            keepsDiving = False
            break

def run_internal_innerFix(self, time, numberOfNurses: int, runRandom: bool = True, pos:int = 0):

    if runRandom:
        allNurses = list(range(self.nurseModel.I))
        nursesFree = random.sample(allNurses, k = math.floor(numberOfNurses))
    else:
        nursesFree = []
        i = pos
        while len(nursesFree) < numberOfNurses:
            i = i % self.nurseModel.I
            nursesFree.append(i)
            i += 1

    for i in range(self.nurseModel.I):
        if i in nursesFree:
            for d in range(self.nurseModel.D):
                for t in range(self.nurseModel.T):
                    self.nurseModel.model.x[i][d][t].lb = 0
                    self.nurseModel.model.x[i][d][t].ub = 1
                    self.nurseModel.model.x[i][d][t].start = self.currentSol.solution[i][d][t]
    
            
    self.nurseModel.model.m.setParam("TimeLimit", time)
    self.nurseModel.model.m.setParam("BestObjStop", 0)
    
    self.nurseModel.model.m.update()
    self.chronos.startCounter("OPTIMIZE_INNER")
    self.nurseModel.model.m.optimize()
    self.chronos.stopCounter()
    
    gurobiReturn = GurobiOptimizedOutput(self.nurseModel.model.m)

    self.chronos.printObj("ORIGIN_SOLVER", "SOLVER_GUROBI_OUTPUT", gurobiReturn)

    if gurobiReturn.valid():
        newObj = self.nurseModel.model.m.objVal
        print(self.penalties.best, newObj)
        if newObj < self.penalties.best: #here changes both
            #input("@")
            self.penalties.best = newObj
            self.chronos.printMessage("Fixs+", newObj)
            for i in range(self.nurseModel.I):
                for d in range(self.nurseModel.D):
                    for t in range(self.nurseModel.T):
                        self.currentSol.solution[i][d][t] = 1 if self.nurseModel.model.x[i][d][t].x >= 0.5 else 0
                        
    
    for i in range(self.nurseModel.I):
        if i in nursesFree:
            for d in range(self.nurseModel.D):
                for t in range(self.nurseModel.T):
                    self.nurseModel.model.x[i][d][t].lb = self.currentSol.solution[i][d][t]
                    self.nurseModel.model.x[i][d][t].ub = self.currentSol.solution[i][d][t]
                    
def run_internal_dayInnerFix(self, time, numberOfDays:int, numberOfNurses: int):

    d = random.randint(0, self.nurseModel.D-1)
    
    nursesWorking = []
    for i in range(self.nurseModel.I):
        if sum(self.currentSol.solution[i][d]) > 0:
            nursesWorking.append(i)

    if numberOfNurses > len(nursesWorking):
        nursesFree = nursesWorking
    else:
        nursesFree = random.sample(nursesWorking, k = math.floor(numberOfNurses))

    limitsNurse = []
        
    for i in nursesFree:
        dayStart, dayEnd = self.getRangeRewrite(i, d, math.floor(numberOfDays))
        limitsNurse.append([dayStart, dayEnd])
        for d in range(dayStart, dayEnd):
            for t in range(self.nurseModel.T):
                self.nurseModel.model.x[i][d][t].lb = 0
                self.nurseModel.model.x[i][d][t].ub = 1
                self.nurseModel.model.x[i][d][t].start = self.currentSol.solution[i][d][t]
    
            
    self.nurseModel.model.m.setParam("TimeLimit", min(self.chronos.timeLeftForVND(), time))
    self.nurseModel.model.m.setParam("BestObjStop", 0)
    
    self.nurseModel.model.m.update()
    self.chronos.startCounter("START_OPTIMIZE_INNER")
    self.nurseModel.model.m.optimize()
    self.chronos.stopCounter()
    
    gurobiReturn = GurobiOptimizedOutput(self.nurseModel.model.m)

    self.chronos.printObj("ORIGIN_SOLVER", "SOLVER_GUROBI_OUTPUT", gurobiReturn)

    if gurobiReturn.valid():
        newObj = self.nurseModel.model.m.objVal
        print(self.penalties.best, newObj)
        if newObj <= self.penalties.best: #here changes both
            #input("@")
            self.penalties.best = newObj
            self.chronos.printMessage("Fixs+", newObj)
            for index in range(len(nursesFree)):
                dayStart = limitsNurse[index][0]
                dayEnd = limitsNurse[index][1]
                i = nursesFree[index]
                for d in range(dayStart, dayEnd):
                    for t in range(self.nurseModel.T):
                        self.currentSol.solution[i][d][t] = 1 if self.nurseModel.model.x[i][d][t].x >= 0.5 else 0
                        
    
    for i in nursesFree:
        dayStart, dayEnd = self.getRangeRewrite(i, d, math.floor(numberOfDays))
        limitsNurse.append([dayStart, dayEnd])
        for d in range(dayStart, dayEnd):
            for t in range(self.nurseModel.T):
                self.nurseModel.model.x[i][d][t].lb = self.currentSol.solution[i][d][t]
                self.nurseModel.model.x[i][d][t].ub = self.currentSol.solution[i][d][t]


def run_internal_all(self, time):

    for i in range(self.nurseModel.I):
        for d in range(self.nurseModel.D):
            for t in range(self.nurseModel.T):
                self.nurseModel.model.x[i][d][t].lb = 0
                self.nurseModel.model.x[i][d][t].ub = 1
                self.nurseModel.model.x[i][d][t].start = self.currentSol.solution[i][d][t]
    
            
    self.nurseModel.model.m.setParam("TimeLimit", time)
    self.nurseModel.model.m.setParam("BestObjStop", 0)
    
    self.nurseModel.model.m.update()
    self.chronos.startCounter("OPTIMIZE_ALL")
    self.nurseModel.model.m.optimize()
    self.chronos.stopCounter()
    
    gurobiReturn = GurobiOptimizedOutput(self.nurseModel.model.m)

    self.chronos.printObj("ORIGIN_SOLVER", "SOLVER_GUROBI_OUTPUT", gurobiReturn)

    if gurobiReturn.valid():
        newObj = self.nurseModel.model.m.objVal
        print(self.penalties.best, newObj)
        if newObj < self.penalties.best: #here changes both
            #input("@")
            self.penalties.best = newObj
            self.chronos.printMessage("Fixs+", newObj)
            for i in range(self.nurseModel.I):
                for d in range(self.nurseModel.D):
                    for t in range(self.nurseModel.T):
                        self.currentSol.solution[i][d][t] = 1 if self.nurseModel.model.x[i][d][t].x >= 0.5 else 0
                        

    for i in range(self.nurseModel.I):
        for d in range(self.nurseModel.D):
            for t in range(self.nurseModel.T):
                self.nurseModel.model.x[i][d][t].lb = self.currentSol.solution[i][d][t]
                self.nurseModel.model.x[i][d][t].ub = self.currentSol.solution[i][d][t]