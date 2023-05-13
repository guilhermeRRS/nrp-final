def commit_sequence(self, move):
    nurse = move["n"]
    dayStart = move["d"]
    oldShifts = self.helperVariables.projectedX[nurse][dayStart:(dayStart+len(move["s"]))]
    newShifts = move["s"]

    self.penalties.demand = move["nD"]
    self.penalties.preference_total = move["nP"]

    self.penalties.total = self.penalties.demand + self.penalties.preference_total
    
    for day in range(dayStart, dayStart+len(move["s"])):

        dayIndex = day - dayStart

        oldShift = oldShifts[dayIndex]
        newShift = newShifts[dayIndex]
        
        self.helperVariables.projectedX[nurse][day] = newShift

        if oldShift >= 0:
            self.nurseModel.model.x[nurse][day][oldShift].lb = 0
            self.nurseModel.model.x[nurse][day][oldShift].ub = 0
    
            self.helperVariables.shiftTypeCounter[nurse][oldShift] -= 1
            self.helperVariables.workloadCounter[nurse] -= self.nurseModel.data.parameters.l_t[oldShift]
    
            self.penalties.numberNurses[day][oldShift] -= 1
        
        if newShift >= 0:
            self.nurseModel.model.x[nurse][day][newShift].lb = 1
            self.nurseModel.model.x[nurse][day][newShift].ub = 1
            
            self.helperVariables.shiftTypeCounter[nurse][newShift] += 1
            self.helperVariables.workloadCounter[nurse] += self.nurseModel.data.parameters.l_t[newShift]
            
            self.penalties.numberNurses[day][newShift] += 1

