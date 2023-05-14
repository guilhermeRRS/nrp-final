def main_runSingle(self):
    
    numberOfIters = 2*self.nurseModel.I*self.nurseModel.D*self.nurseModel.T
    while self.chronos.stillValidRestrict():
        numberSuccess = 0
        for i in range(numberOfIters):
            s, move = self.run_single(worse = False, better = True, equal = False)
            
            if s:
                self.commit_single(move)
                numberSuccess += 1
                
            if not self.chronos.stillValidRestrict():
                break

        print(numberSuccess)
        if numberSuccess < 0.001*numberOfIters:
            break

def main_runSingleMany(self):

    numberOfNurses = 5
    numberOfIters = 1000
    while self.chronos.stillValidRestrict():
        numberSuccess = 0
        for i in range(numberOfIters):
            
            s, move = self.run_singleMany(numberOfNurses = numberOfNurses, worse = False, better = True, equal = False)
            
            if s:
                self.commit_singleMany(move)
                numberSuccess += 1
                
            if not self.chronos.stillValidRestrict():
                break

        print(numberSuccess)
        if numberSuccess < 0.001*numberOfIters:
            break

def main_seqFromModel(self):
    
    while self.chronos.stillValidRestrict():
        rangeOfSequences = 100
        s, move = self.run_seqFromModel(rangeOfSequences = rangeOfSequences, numberOfTries = 1, worse = False, better = True, equal = False)
        
        if s:
            self.commit_sequence(move)
            print(self.penalties.total)
            #numberSuccess += 1

def main_seqNursesFromModel(self):
    
    sTries = 0
    while self.chronos.stillValidRestrict() and sTries < 13:
        rangeOfSequences = 100
        numberOfNurses = 2
        s, move = self.run_seqNursesFromModel(numberOfNurses = numberOfNurses, rangeOfSequences = rangeOfSequences, numberOfTries = 1, worse = False, better = True, equal = False)
        
        if s:
            self.commit_sequenceMany(move)
            sTries += 1
            print(move)
            print(self.penalties.total)
            #numberSuccess += 1
        