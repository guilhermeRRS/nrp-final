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
                val = 1 if self.nurseModel.model.x[nurse][day][oldShift].x >= 0.5 else 0
                self.nurseModel.model.x[nurse][day][oldShift].lb = val
                self.nurseModel.model.x[nurse][day][oldShift].ub = val
        
                self.helperVariables.shiftTypeCounter[nurse][oldShift] -= 1
                self.helperVariables.workloadCounter[nurse] -= self.nurseModel.data.parameters.l_t[oldShift]
        
                self.penalties.numberNurses[day][oldShift] -= 1

                self.helperVariables.workingDays[nurse].remove(day)
            
            if newShift >= 0:
                val = 1 if self.nurseModel.model.x[nurse][day][newShift].x >= 0.5 else 0
                self.nurseModel.model.x[nurse][day][newShift].lb = val
                self.nurseModel.model.x[nurse][day][newShift].ub = val
                
                self.helperVariables.shiftTypeCounter[nurse][newShift] += 1
                self.helperVariables.workloadCounter[nurse] += self.nurseModel.data.parameters.l_t[newShift]
                
                self.helperVariables.workingDays[nurse].append(day)
                
                self.penalties.numberNurses[day][newShift] += 1

