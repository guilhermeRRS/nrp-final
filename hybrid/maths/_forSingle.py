def math_single_preferenceDelta(self, nurse, day, oldShift, newShift):

    q = self.nurseModel.data.parameters.q[nurse][day]
    p = self.nurseModel.data.parameters.p[nurse][day]

    penalty = 0
    if oldShift >= 0:
        penalty += (q[oldShift] - p[oldShift])
    if newShift >= 0:
        penalty += (p[newShift] - q[newShift])

    return penalty

def math_single_preference(self, nurse, day, oldShift, newShift):
    return self.penalties.preference_total + self.math_single_preferenceDelta(nurse, day, oldShift, newShift)

def math_single_demandDelta(self, day, oldShift, newShift):

    if oldShift == newShift:
        return 0

    penaltyOld = 0
    penaltyNew = 0

    numberNurses = self.penalties.numberNurses[day]
    demand = self.nurseModel.data.parameters.u[day]

    w_min = self.nurseModel.data.parameters.w_min[day]
    w_max = self.nurseModel.data.parameters.w_max[day]

    if oldShift >= 0:
        if numberNurses[oldShift] > demand[oldShift]:
            penaltyOld -= (numberNurses[oldShift] - demand[oldShift])*w_max[oldShift]
        if numberNurses[oldShift] < demand[oldShift]:
            penaltyOld -= (demand[oldShift] - numberNurses[oldShift])*w_min[oldShift]
    
    if newShift >= 0:
        if numberNurses[newShift] > demand[newShift]:
            penaltyNew -= (numberNurses[newShift] - demand[newShift])*w_max[newShift]
        if numberNurses[newShift] < demand[newShift]:
            penaltyNew -= (demand[newShift] - numberNurses[newShift])*w_min[newShift]
    
    if oldShift >= 0:
        if numberNurses[oldShift] - 1 > demand[oldShift]:
            penaltyOld += (numberNurses[oldShift] - 1 - demand[oldShift])*w_max[oldShift]
        if numberNurses[oldShift] - 1 < demand[oldShift]:
            penaltyOld += (demand[oldShift] - numberNurses[oldShift] + 1)*w_min[oldShift]
    
    if newShift >= 0:
        if numberNurses[newShift] + 1> demand[newShift]:
            penaltyNew += (numberNurses[newShift] + 1 - demand[newShift])*w_max[newShift]
        if numberNurses[newShift] + 1 < demand[newShift]:
            penaltyNew += (demand[newShift] - numberNurses[newShift] - 1)*w_min[newShift]

    return penaltyOld + penaltyNew

def math_single_demand(self, day, oldShift, newShift):

    return self.penalties.demand + self.math_single_demandDelta(day, oldShift, newShift)


def math_single(self, nurse, day, oldShift, newShift):
    
    return self.math_single_preference(nurse, day, oldShift, newShift), self.math_single_demand(day, oldShift, newShift)