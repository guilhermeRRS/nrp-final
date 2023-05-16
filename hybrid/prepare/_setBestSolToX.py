def bestSolToX(self):
    for nurse in range(self.nurseModel.I):
        for d in range(self.nurseModel.D):
            for t in range(self.nurseModel.T):
                self.parallelModels[nurse]["x"][d][t].lb = self.tmpBestSol.solution[nurse][d][t]
                self.parallelModels[nurse]["x"][d][t].ub = self.tmpBestSol.solution[nurse][d][t]