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
        if numberSuccess < 10:
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

def manager_seqShorterBetter(self):
    self.startSeqs()

    numberOfIters = 100
    optionsNumberNurses = [2]

    numberNurses = list(dict.fromkeys(optionsNumberNurses))
    rangeOfSequencesOptions = [1,2]
    
    for rangeOfSequences in rangeOfSequencesOptions:
        for numberNurses in optionsNumberNurses:
            numberSuccess = 0
            for i in range(numberOfIters):
                s, move = self.run_seqNursesFromModel(numberOfNurses = numberNurses, rangeOfSequences = rangeOfSequences, numberOfTries = 10, worse = False, better = True, equal = True)
        
                if s:
                    newObj = move["nD"] + move["nP"]
                    if newObj < self.penalties.best:
                        print("+",self.penalties.best,newObj)
                        numberSuccess += 1
                        self.commit_sequenceMany(move)
                        print("SI", self.penalties.total, self.penalties.best)
                        if self.penalties.total < self.penalties.best:
                            self.penalties.best = self.penalties.total
                            for i in range(self.nurseModel.I):
                                for d in range(self.nurseModel.D):
                                    for t in range(self.nurseModel.T):
                                        self.tmpBestSol.solution[i][d][t] = self.currentSol.solution[i][d][t]
                    else:
                        print("~",self.penalties.best,newObj)
                else:
                    print("-")
                
                if not self.chronos.stillValidMIP():
                    break
            print("SI", rangeOfSequences, numberNurses, numberSuccess)
        if not self.chronos.stillValidMIP():
            break

def manager_seqShorterWorser(self, beta:int = 1):
    self.startSeqs()

    numberOfIters = 1000
    optionsNumberNurses = [2]

    numberNurses = list(dict.fromkeys(optionsNumberNurses))
    rangeOfSequencesOptions = [2]
    
    for rangeOfSequences in rangeOfSequencesOptions:
        for numberNurses in optionsNumberNurses:
            numberSuccess = 0
            for i in range(numberOfIters):
                s, move = self.run_seqNursesFromModel(numberOfNurses = numberNurses, rangeOfSequences = rangeOfSequences, numberOfTries = 1, worse = True, better = True, equal = True)
        
                if s:
                    newObj = move["nD"] + move["nP"]
                    if newObj < self.penalties.best:
                        numberSuccess += 1
                        self.commit_sequenceMany(move)
                        print("SW", self.penalties.total, self.penalties.best)
                        if self.penalties.total < self.penalties.best:
                            self.penalties.best = self.penalties.total
                            for i in range(self.nurseModel.I):
                                for d in range(self.nurseModel.D):
                                    for t in range(self.nurseModel.T):
                                        self.tmpBestSol.solution[i][d][t] = self.currentSol.solution[i][d][t]
                
                    elif newObj <= max(self.penalties.best*1.1, self.penalties.best+1000):
                        print("SW~", self.penalties.total, self.penalties.best, newObj)
                        self.commit_sequenceMany(move)
                    elif newObj <= self.penalties.total:
                        print("SW=", self.penalties.total, self.penalties.best, newObj)
                        self.commit_sequenceMany(move)
                    else:  
                        randomFactor = random.random()
                        expFunction = math.e**(-(newObj - self.penalties.best)/(self.penalties.best*beta))
                        if randomFactor < expFunction:
                            print("SW--", self.penalties.total, self.penalties.best, newObj, randomFactor, expFunction)
                            self.commit_sequenceMany(move)
                        else:
                            print("SW-_", self.penalties.total, self.penalties.best, newObj, randomFactor, expFunction)

                if not self.chronos.stillValidMIP():
                    break
            print("SW", rangeOfSequences, numberNurses, numberSuccess)
        if not self.chronos.stillValidMIP():
            break

def manager_seqHugeWorser(self, beta, numberNurses):
    self.startSeqs()

    numberOfIters = 250
    optionsNumberNurses = [math.floor(numberNurses)]
    numberOfTries = 1

    numberNurses = list(dict.fromkeys(optionsNumberNurses))
    rangeOfSequencesOptions = [10000]
    
    for rangeOfSequences in rangeOfSequencesOptions:
        for numberNurses in optionsNumberNurses:
            numberSuccess = 0
            for i in range(numberOfIters):
                s, move = self.run_seqNursesFromModel(numberOfNurses = numberNurses, rangeOfSequences = rangeOfSequences, numberOfTries = numberOfTries, worse = True, better = True, equal = True)
                
                if s:
                    newObj = move["nD"] + move["nP"]
                    if newObj < self.penalties.best:
                        self.penalties.best = newObj
                        #totalNumberOfSucces += 1
                        numberSuccess += 1
                            
                        self.commit_sequenceMany(move)
                        print("SH+", self.penalties.total, self.penalties.best, newObj)
                        for i in range(self.nurseModel.I):
                            for d in range(self.nurseModel.D):
                                for t in range(self.nurseModel.T):
                                    self.tmpBestSol.solution[i][d][t] = self.currentSol.solution[i][d][t]

                    elif newObj <= max(self.penalties.best*1.25, self.penalties.best+1000):
                        print("SH~", self.penalties.total, self.penalties.best, newObj)
                        self.commit_sequenceMany(move)
                    elif newObj <= self.penalties.total:
                        print("SH=", self.penalties.total, self.penalties.best, newObj)
                        self.commit_sequenceMany(move)
                    else:  
                        randomFactor = random.random()
                        expFunction = math.e**(-(newObj - self.penalties.best)/(self.penalties.best*beta))
                        if randomFactor < expFunction:
                            print("SH--", self.penalties.total, self.penalties.best, newObj, randomFactor, expFunction)
                            self.commit_sequenceMany(move)
                        else:
                            print("SH-_", self.penalties.total, self.penalties.best, newObj, randomFactor, expFunction)


                if not self.chronos.stillValidMIP():
                    break
            print("SH", rangeOfSequences, numberNurses, numberSuccess)
        if not self.chronos.stillValidMIP():
            break
        
    #print("SM", totalNumberOfSucces)
    
    #if totalNumberOfSucces < 10:
    #    keepsDiving = False
    #    break

def run_inner(self, time):
    restrictions = []
    for i in range(self.nurseModel.I):
        for d in range(self.nurseModel.D):
            restrictions.append(self.SA_shift_model.addConstr(sum(self.SA_sm_x[i][d][t] for t in range(self.nurseModel.T)) == sum(self.currentSol.solution[i][d][t] for t in range(self.nurseModel.T))))
            for t in range(self.nurseModel.T):
                self.SA_sm_x[i][d][t].Start = self.currentSol.solution[i][d][t]
    self.SA_shift_model.setParam("TimeLimit", min(self.chronos.timeLeft(), time))
    
    self.SA_shift_model.update()
    self.chronos.startCounter("START_OPTIMIZE_INNER")
    self.SA_shift_model.optimize()
    self.chronos.stopCounter()
    
    gurobiReturn = GurobiOptimizedOutput(self.SA_shift_model)

    self.chronos.printObj("ORIGIN_SOLVER", "SOLVER_GUROBI_OUTPUT", gurobiReturn)

    if gurobiReturn.valid():
        newObj = self.SA_preference_total.x + self.SA_demand.x
        if newObj < self.penalties.best: #here changes both
            self.penalties.best = newObj
            for i in range(self.nurseModel.I):
                for d in range(self.nurseModel.D):
                    for t in range(self.nurseModel.T):
                        self.tmpBestSol.solution[i][d][t] = 1 if self.SA_sm_x[i][d][t].x >= 0.5 else 0
                        self.currentSol.solution[i][d][t] = 1 if self.SA_sm_x[i][d][t].x >= 0.5 else 0
        else: #here only current
            self.penalties.total = newObj
            for i in range(self.nurseModel.I):
                for d in range(self.nurseModel.D):
                    for t in range(self.nurseModel.T):
                        self.currentSol.solution[i][d][t] = 1 if self.SA_sm_x[i][d][t].x >= 0.5 else 0
    else:
        print("Discarded inner solution")

    for restriction in restrictions:
        self.SA_shift_model.remove(restriction)