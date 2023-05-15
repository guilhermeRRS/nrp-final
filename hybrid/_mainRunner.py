def main_runSingle(self):
    
    numberOfIters = 2*self.nurseModel.I*self.nurseModel.D*self.nurseModel.T
    while self.chronos.stillValidRestrict():
        numberSuccess = 0
        for i in range(numberOfIters):
            s, move = self.run_single(worse = True, better = True, equal = True)
            
            if s:
                print(move["nD"]+move["nP"])
                self.commit_single(move)
                numberSuccess += 1
                
            if not self.chronos.stillValidRestrict():
                break

        print(numberSuccess)
        break
        if numberSuccess < 0.001*numberOfIters:
            break

def main_runSingleMany(self):

    numberOfNurses = 2
    numberOfIters = 10000
    while self.chronos.stillValidRestrict():
        numberSuccess = 0
        for i in range(numberOfIters):
            
            s, move = self.run_singleMany(numberOfNurses = numberOfNurses, worse = True, better = True, equal = False)
            
            if s:
                self.commit_singleMany(move)
                numberSuccess += 1
                
            if not self.chronos.stillValidRestrict():
                break

        print(numberSuccess)
        break
        if numberSuccess < 0.001*numberOfIters:
            break

def main_seqFromModel(self):
    
    sTries = 0
    while self.chronos.stillValidRestrict() and sTries < 10:
        rangeOfSequences = 2
        s, move = self.run_seqFromModel(rangeOfSequences = rangeOfSequences, numberOfTries = 1, worse = False, better = True, equal = False)
        if s:
            #print(move["nD"]+move["nP"])
            sTries += 1
            self.commit_sequence(move)
            #numberSuccess += 1
    print(sTries)

def main_seqNursesFromModel(self):
    
    sTries = 0
    while self.chronos.stillValidRestrict() and sTries < 100:
        rangeOfSequences = 10
        numberOfNurses = 3
        s, move = self.run_seqNursesFromModel(numberOfNurses = numberOfNurses, rangeOfSequences = rangeOfSequences, numberOfTries = 1, worse = True, better = True, equal = True)
        
        if s:
            print(sTries)
            #print(move["nD"]+move["nP"])
            self.commit_sequenceMany(move)
            sTries += 1
    print(sTries)

        