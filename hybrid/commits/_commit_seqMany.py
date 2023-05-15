def commit_sequenceMany(self, moves):
    
    self.penalties.demand = moves["nD"]
    self.penalties.preference_total = moves["nP"]

    self.penalties.total = self.penalties.demand + self.penalties.preference_total
    
    for move in moves["s"]:
        
        nurse = move["n"]
        dayStart = move["dayStart"]
        duration = move["length"]

        newShifts = move["s"]

        for dayIndex in range(duration):

            day = dayIndex + dayStart

            oldShift = self.helperVariables.projectedX[nurse][day]
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
        
    self.parallelModels[nurse]["m"].update()