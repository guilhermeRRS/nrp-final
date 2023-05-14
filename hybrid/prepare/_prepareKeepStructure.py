def prepareKeepStructure(self):

    for i in range(self.nurseModel.I):
        for d in range(self.nurseModel.D):
            for t in range(self.nurseModel.T):
                self.modelShift.sm_x[i][d][t] = self.nurseModel.model.x[i][d][t].lb