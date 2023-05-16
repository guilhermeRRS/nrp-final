import math
import random


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
    while self.chronos.stillValidRestrict() and keepsDiving:
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
                
            if not self.chronos.stillValidRestrict():
                keepsDiving = False
                break

        print("11", numberSuccess)
        if numberSuccess < 10:
            keepsDiving = False

def manager_singleSearch(self, numberOfIters):
    self.startSingles()

    optionsNumberNurses = [2, 3, 4]

    numberNurses = list(dict.fromkeys(optionsNumberNurses))
    
    keepsDiving = True
    totalNumberOfSucces = 0
    while self.chronos.stillValidRestrict() and keepsDiving:
        totalNumberOfSucces = 0
        for numberNurses in optionsNumberNurses:
            numberSuccess = 0
            for i in range(numberOfIters):
                
                s, move = self.run_singleMany(numberOfNurses = numberNurses, worse = False, better = True, equal = True)

                if s:
                    if move["nD"] + move["nP"] < self.penalties.total:
                        numberSuccess += 1
                        
                    self.commit_singleMany(move)
                    print("1S", self.penalties.total, self.penalties.best)

                    if self.penalties.total < self.penalties.best:
                        self.penalties.best = self.penalties.total
                        for i in range(self.nurseModel.I):
                            for d in range(self.nurseModel.D):
                                for t in range(self.nurseModel.T):
                                    self.tmpBestSol.solution[i][d][t] = self.currentSol.solution[i][d][t]
                                    
                if not self.chronos.stillValidRestrict():
                    break
            print("1S", numberNurses, numberSuccess)
            totalNumberOfSucces += numberSuccess
            if not self.chronos.stillValidRestrict():
                break
        
        print("1S.", totalNumberOfSucces)
        if totalNumberOfSucces < 10:
            keepsDiving = False
            break

def manager_seqShorter(self):
    self.startSeqs()

    numberOfIters = 100
    optionsNumberNurses = [4]

    numberNurses = list(dict.fromkeys(optionsNumberNurses))
    rangeOfSequencesOptions = [3]
    
    for rangeOfSequences in rangeOfSequencesOptions:
        for numberNurses in optionsNumberNurses:
            numberSuccess = 0
            for i in range(numberOfIters):
                s, move = self.run_seqNursesFromModel(numberOfNurses = numberNurses, rangeOfSequences = rangeOfSequences, numberOfTries = 1, worse = False, better = True, equal = False)
        
                if s:
                    numberSuccess += 1
                    self.commit_sequenceMany(move)
                    print("SI", self.penalties.total, self.penalties.best)
                    if self.penalties.total < self.penalties.best:
                        self.penalties.best = self.penalties.total
                        for i in range(self.nurseModel.I):
                            for d in range(self.nurseModel.D):
                                for t in range(self.nurseModel.T):
                                    self.tmpBestSol.solution[i][d][t] = self.currentSol.solution[i][d][t]
                
                if not self.chronos.stillValidRestrict():
                    break
            print("SI", rangeOfSequences, numberNurses, numberSuccess)
        if not self.chronos.stillValidRestrict():
            break
        
    #print("SM", totalNumberOfSucces)
    
    #if totalNumberOfSucces < 10:
    #    keepsDiving = False
    #    break

def manager_seqHuge(self, beta):
    self.startSeqs()

    numberOfIters = 250
    optionsNumberNurses = [1,2,3,4]
    numberOfTries = 1

    numberNurses = list(dict.fromkeys(optionsNumberNurses))
    rangeOfSequencesOptions = [10000]
    
    for rangeOfSequences in rangeOfSequencesOptions:
        for numberNurses in optionsNumberNurses:
            numberSuccess = 0
            for i in range(numberOfIters):
                s, move = self.run_seqNursesFromModel(numberOfNurses = numberNurses, rangeOfSequences = rangeOfSequences, numberOfTries = numberOfTries, worse = True, better = True, equal = True)
                
                if s:
                    if self.penalties.total <= self.penalties.best:
                        self.penalties.best = self.penalties.total
                        #totalNumberOfSucces += 1
                        numberSuccess += 1
                            
                        self.commit_sequenceMany(move)
                        print("SH+", self.penalties.total, self.penalties.best)
                        if move["nD"] + move["nP"] < self.penalties.total:
                            for i in range(self.nurseModel.I):
                                for d in range(self.nurseModel.D):
                                    for t in range(self.nurseModel.T):
                                        self.tmpBestSol.solution[i][d][t] = self.currentSol.solution[i][d][t]

                    elif self.penalties.total <= max(self.penalties.best*1.1, self.penalties.best+1000):
                        print("SH~", self.penalties.total, self.penalties.best)
                        self.commit_sequenceMany(move)
                    else:  
                        newPenalty = move["nD"] + move["nP"]
                        randomFactor = random.random()
                        expFunction = math.e**(-(newPenalty - self.penalties.best)/(self.penalties.best*beta))
                        if randomFactor < expFunction:
                            print("SH--", self.penalties.total, self.penalties.best, newPenalty, randomFactor, expFunction)
                            self.commit_sequenceMany(move)
                        else:
                            print("SH-_", self.penalties.total, self.penalties.best, newPenalty, randomFactor, expFunction)


                if not self.chronos.stillValidRestrict():
                    break
            print("SH", rangeOfSequences, numberNurses, numberSuccess)
        if not self.chronos.stillValidRestrict():
            break
        
    #print("SM", totalNumberOfSucces)
    
    #if totalNumberOfSucces < 10:
    #    keepsDiving = False
    #    break