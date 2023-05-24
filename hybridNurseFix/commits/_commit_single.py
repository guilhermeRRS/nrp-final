def commit_single(self, move):
    nurse = move["n"]
    day = move["d"]
    oldShift = self.helperVariables.projectedX[nurse][day]
    newShift = move["s"]


    self.penalties.demand = move["nD"]
    self.penalties.preference_total = move["nP"]

    self.penalties.total = self.penalties.demand + self.penalties.preference_total
    
    self.currentSol.solution[nurse][day][oldShift] = 0
    
    self.currentSol.solution[nurse][day][newShift] = 1

    self.helperVariables.projectedX[nurse][day] = newShift


    self.helperVariables.shiftTypeCounter[nurse][oldShift] -= 1
    self.helperVariables.workloadCounter[nurse] -= self.nurseModel.data.parameters.l_t[oldShift]
    self.penalties.numberNurses[day][oldShift] -= 1

    self.helperVariables.shiftTypeCounter[nurse][newShift] += 1
    self.helperVariables.workloadCounter[nurse] += self.nurseModel.data.parameters.l_t[newShift]
    self.penalties.numberNurses[day][newShift] += 1