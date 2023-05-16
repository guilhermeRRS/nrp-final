def commit_sequence(self, move):
    nurse = move["n"]
    dayStart = move["d"]
    duration = len(move["s"])
    oldShifts = self.helperVariables.projectedX[nurse][dayStart:(dayStart+len(move["s"]))]
    newShifts = move["s"]

    self.penalties.demand = move["nD"]
    self.penalties.preference_total = move["nP"]

    self.penalties.total = self.penalties.demand + self.penalties.preference_total
    
    for day in range(dayStart, dayStart+duration):

        dayIndex = day - dayStart

        oldShift = oldShifts[dayIndex]
        newShift = newShifts[dayIndex]
        
        self.helperVariables.projectedX[nurse][day] = newShift

        if oldShift >= 0:
            
            self.parallelModels[nurse]["x"][day][oldShift].lb = 0
            self.parallelModels[nurse]["x"][day][oldShift].ub = 0
            self.currentSol.solution[nurse][day][oldShift] = 0
    
            self.penalties.numberNurses[day][oldShift] -= 1

            self.helperVariables.workingDays[nurse].remove(day)
        
        if newShift >= 0:
            
            self.parallelModels[nurse]["x"][day][newShift].lb = 1
            self.parallelModels[nurse]["x"][day][newShift].ub = 1
            self.currentSol.solution[nurse][day][newShift] = 1
            
            self.penalties.numberNurses[day][newShift] += 1
                
            self.helperVariables.workingDays[nurse].append(day)


