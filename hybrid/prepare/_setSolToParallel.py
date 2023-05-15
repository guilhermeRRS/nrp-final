def solToParallel(self):
    for nurse in range(self.nurseModel.I):
        for d in range(self.nurseModel.D):
            for t in range(self.nurseModel.T):
                self.parallelModels[nurse]["x"][d][t].lb = self.currentSol.solution[nurse][d][t]
                self.parallelModels[nurse]["x"][d][t].ub = self.currentSol.solution[nurse][d][t]
        self.parallelModels[nurse]["m"].update()