def math_sequence(self, nurse, dayStart, dayEnd, oldShifts, newShifts):
    penaltyPreference = 0
    penaltyDemand = 0
    for i in range(len(oldShifts)):
        penaltyPreference += self.math_single_preferenceDelta(nurse, dayStart+i, oldShifts[i], newShifts[i])
        penaltyDemand += self.math_single_demandDelta(dayStart+i, oldShifts[i], newShifts[i])
    return self.penalties.preference_total + penaltyPreference, self.penalties.demand + penaltyDemand
