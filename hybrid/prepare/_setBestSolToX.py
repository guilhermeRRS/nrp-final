def bestSolToX(self):
    for nurse in range(self.nurseModel.I):
        for d in range(self.nurseModel.D):
            for t in range(self.nurseModel.T):
                self.nurseModel.model.x[nurse][d][t].lb = 0
                self.nurseModel.model.x[nurse][d][t].ub = 1
                self.nurseModel.model.x[nurse][d][t].Start = self.tmpBestSol.solution[nurse][d][t]