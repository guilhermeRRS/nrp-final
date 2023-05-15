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
        
                self.helperVariables.shiftTypeCounter[nurse][oldShift] -= 1
                self.helperVariables.workloadCounter[nurse] -= self.nurseModel.data.parameters.l_t[oldShift]
        
                self.penalties.numberNurses[day][oldShift] -= 1

                self.helperVariables.workingDays[nurse].remove(day)
            
            if newShift >= 0:
                
                self.parallelModels[nurse]["x"][day][newShift].lb = 1
                self.parallelModels[nurse]["x"][day][newShift].ub = 1
                
                self.helperVariables.shiftTypeCounter[nurse][newShift] += 1
                self.helperVariables.workloadCounter[nurse] += self.nurseModel.data.parameters.l_t[newShift]
                
                self.helperVariables.workingDays[nurse].append(day)
                
                self.penalties.numberNurses[day][newShift] += 1
        
    self.parallelModels[nurse]["m"].update()