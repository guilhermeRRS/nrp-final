def calculateHelper(self):

    for d in range(self.nurseModel.D):
        for t in range(self.nurseModel.T):
            self.penalties.numberNurses[d][t] = 0

    self.penalties.preference_total = 0
    for i in range(self.nurseModel.I):
        self.helperVariables.workloadCounter[i] = 0
        self.helperVariables.workingDays[i] = []
        
        for t in range(self.nurseModel.T):
            self.helperVariables.shiftTypeCounter[i][t] = 0
        
        for d in range(self.nurseModel.D):
            self.helperVariables.projectedX[i][d] = -1
            for t in range(self.nurseModel.T):
                self.penalties.preference_total += self.nurseModel.data.parameters.p[i][d][t]*self.nurseModel.solution.solution[i][d][t]+self.nurseModel.data.parameters.q[i][d][t]*(1 - self.nurseModel.solution.solution[i][d][t])
    
                if self.nurseModel.solution.solution[i][d][t] >= 0.5:
                    self.helperVariables.shiftTypeCounter[i][t] += 1
                    self.helperVariables.workloadCounter[i] += self.nurseModel.data.parameters.l_t[t]
                    self.helperVariables.projectedX[i][d] = t
                    self.helperVariables.workingDays[i].append(d)
                    self.penalties.numberNurses[d][t] += 1
    
    self.penalties.demand = 0

    #equivalence = []
    for t in range(self.nurseModel.T):
        #equivalence.append(self.nurseModel.data.sets.R_t.index(self.nurseModel.data.sets.R_t[t]))
        for d in range(self.nurseModel.D):
            numberNurses = self.penalties.numberNurses[d][t]
            neededNurses = self.nurseModel.data.parameters.u[d][t]
            addingPenalty = 0
            if numberNurses < neededNurses:
                addingPenalty = (neededNurses - numberNurses)*self.nurseModel.data.parameters.w_min[d][t]
                self.penalties.demand += addingPenalty
            elif numberNurses > neededNurses:
                addingPenalty = (numberNurses - neededNurses)*self.nurseModel.data.parameters.w_max[d][t]
                self.penalties.demand += addingPenalty
            
    self.penalties.total = self.penalties.demand + self.penalties.preference_total
