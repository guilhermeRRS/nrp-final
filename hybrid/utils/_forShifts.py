def get_extremeShifts(self, nurse):

    allowed_l_t = []
    for i in range(self.nurseModel.T):
        if self.nurseModel.data.parameters.m_max[nurse][i] > 0:
            allowed_l_t.append(self.nurseModel.data.parameters.l_t[i])

    shortestShiftSize = min(allowed_l_t)
    longestShiftSize = max(allowed_l_t)
    return shortestShiftSize, longestShiftSize

def computeLt(self, sequence):
    return sum([self.nurseModel.data.parameters.l_t[sequence[i]] for i in range(len(sequence))])

def computeWorkloadNewSeq(self, sequence):
    return sum([(0 if sequence[i] < 0 else self.nurseModel.data.parameters.l_t[sequence[i]]) for i in range(len(sequence))])

def computeWorkloadSeq(self, nurse, dayStart, dayEnd):
    soma = 0
    for day in range(dayStart, dayEnd+1):
        shift = self.helperVariables.projectedX[nurse][day]
        if shift >= 0:
            soma += self.nurseModel.data.parameters.l_t[shift]
    return soma

def shiftFreeMark(self, shift):
    if shift == -1:
        return "free"
    return str(shift)
def shiftFreeUnMark(self, shift):
    if shift == "free":
        return -1
    return str(shift)

def getSequenceWorkMarks(self, nurse, day):
    dayStart = day
    dayEnd = day
    iter = dayStart
    while iter in self.helperVariables.workingDays[nurse]:
        iter -= 1
    dayStart = iter + 1
    iter = dayEnd
    while iter in self.helperVariables.workingDays[nurse]:
        iter += 1
    dayEnd = iter - 1
    
    return dayStart, dayEnd

def getRangeRewrite(self, nurse, day, rangeOfSequences):
    
    dayStart, dayEnd = self.getSequenceWorkMarks(nurse, day)
    
    iter = dayStart - 1
    while not (iter in self.helperVariables.workingDays[nurse]) and iter >= 0:
        iter -= 1
    dayStart = iter + 1
    
    iter = dayEnd + 1
    while not (iter in self.helperVariables.workingDays[nurse]) and iter < self.nurseModel.D:
        iter += 1
    dayEnd = iter - 1
    
    for i in range(1,rangeOfSequences):
        if i % 2 == 0:
            iter = dayStart - 1
            while iter in self.helperVariables.workingDays[nurse] and iter >= 0:
                iter -= 1
                
            while not (iter in self.helperVariables.workingDays[nurse]) and iter >= 0:
                iter -= 1
            dayStart = iter + 1
        else:
            iter = dayEnd + 1
            while iter in self.helperVariables.workingDays[nurse] and iter < self.nurseModel.D:
                iter += 1
                
            while not (iter in self.helperVariables.workingDays[nurse]) and iter < self.nurseModel.D:
                iter += 1
            dayEnd = iter - 1

    return dayStart, dayEnd
