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