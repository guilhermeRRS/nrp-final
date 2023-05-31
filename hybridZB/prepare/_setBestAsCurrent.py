def setBestAsCurrent(self):
    for nurse in range(self.nurseModel.I):
        for d in range(self.nurseModel.D):
            for t in range(self.nurseModel.T):
                self.currentSol.solution[nurse][d][t] = self.tmpBestSol.solution[nurse][d][t]