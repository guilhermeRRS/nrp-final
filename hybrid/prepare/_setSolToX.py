def solToX(self):
    for nurse in range(self.nurseModel.I):
        for d in range(self.nurseModel.D):
            for t in range(self.nurseModel.T):
                self.nurseModel.model.x[nurse][d][t].lb = self.currentSol.solution[nurse][d][t]
                self.nurseModel.model.x[nurse][d][t].ub = self.currentSol.solution[nurse][d][t]
    self.nurseModel.model.m.update()