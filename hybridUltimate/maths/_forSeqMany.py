def math_seqMany(self, oldShifts, newShifts, moves):
    
    affectedDays = list(dict.fromkeys(oldShifts))
    
    preferenceDelta = 0
    for i in range(len(moves)):
        dayStart = moves[i]["dayStart"]
        duration = moves[i]["length"]
        nurse = moves[i]["n"]
        nurseOld = self.helperVariables.projectedX[nurse]
        nurseNew = moves[i]["s"]
        for d in range(dayStart, dayStart+duration):
            preferenceDelta += self.math_single_preferenceDelta(moves[i]["n"], d, nurseOld[d], nurseNew[d-dayStart])
                
    demandDelta = 0
    for d in affectedDays:
        affectedShifts = list(dict.fromkeys(oldShifts[d] + newShifts[d]))
        for shift in affectedShifts:
            if shift >= 0:
                demandDelta += self.math_singleMany_demand(d, oldShifts[d], newShifts[d], shift)

    return self.penalties.preference_total + preferenceDelta, self.penalties.demand + demandDelta