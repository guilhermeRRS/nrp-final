def math_singleMany(self, nurses, day, oldShifts, newShifts):
    
    preferenceDelta = 0
    
    for i in range(self.tmp.lNurses):
        nurse = nurses[i]
        preferenceDelta += self.math_single_preferenceDelta(nurse, day, oldShifts[i], newShifts[i])
        
    demandDelta = 0
    affectedShifts = list(dict.fromkeys(oldShifts + newShifts))
    for shift in affectedShifts:
        if shift >= 0:
            demandDelta += self.math_singleMany_demand(day, oldShifts, newShifts, shift)
                
    return self.penalties.preference_total + preferenceDelta, self.penalties.demand + demandDelta

def math_singleMany_demand(self, day, oldShifts, newShifts, shift):

    penalty = 0
    
    numberNurses = self.penalties.numberNurses[day]
    demand = self.nurseModel.data.parameters.u[day]

    w_min = self.nurseModel.data.parameters.w_min[day]
    w_max = self.nurseModel.data.parameters.w_max[day]

    if numberNurses[shift] > demand[shift]:
        penalty -= (numberNurses[shift] - demand[shift])*w_max[shift]
    if numberNurses[shift] < demand[shift]:
        penalty -= (demand[shift] - numberNurses[shift])*w_min[shift]
    
    newNumberOfNurses = numberNurses[shift] - oldShifts.count(shift) + newShifts.count(shift)
    if newNumberOfNurses > demand[shift]:
        penalty += (newNumberOfNurses - demand[shift])*w_max[shift]
    if newNumberOfNurses < demand[shift]:
        penalty += (demand[shift] - newNumberOfNurses)*w_min[shift]

    return penalty
