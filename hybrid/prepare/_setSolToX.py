def make_parallel_to_x(self):
    for nurse in range(self.nurseModel.I):
        for d in range(self.nurseModel.D):
            for t in range(self.nurseModel.T):
                self.parallelModels[nurse]["x"][d][t].lb = self.nurseModel.model.x[nurse][d][t].lb
                self.parallelModels[nurse]["x"][d][t].ub = self.nurseModel.model.x[nurse][d][t].lb
        self.parallelModels[nurse]["m"].update()