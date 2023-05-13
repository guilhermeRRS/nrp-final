import random, copy

def run_singleMany(self, numberOfNurses:int, worse:bool = False, better:bool = False, equal:bool = False): #this is random

    day = random.randint(0, self.nurseModel.D-1)

    possibleNurses = []
    for i in range(self.nurseModel.I):
        if day in self.helperVariables.workingDays[i]:
            possibleNurses.append(i)
            
    if len(possibleNurses) < numberOfNurses:
        return False, None
    
    nurses = random.sample(possibleNurses, k = numberOfNurses)

    oldShifts = []
    allNurseOptions = []
    for nurse in nurses:

        ###the edge
        shiftBefore = "free"
        if day - 1 >= 0:
            shiftBefore = self.shiftFreeMark(self.helperVariables.projectedX[nurse][day-1])
        shiftAfter = "free"
        if day + 1 < self.nurseModel.D:
            shiftAfter = self.shiftFreeMark(self.helperVariables.projectedX[nurse][day+1])
        
        ###all options that fits constraints
        oldShift = self.helperVariables.projectedX[nurse][day]

        nurseOptions = self.getSingle(shiftBefore, shiftAfter, nurse, day, oldShift)
        
        if len(nurseOptions) == 0:
            return False, None
        
        random.shuffle(nurseOptions)

        oldShifts.append(oldShift)
        allNurseOptions.append(nurseOptions)
        
    self.tmp.oldObj = self.penalties.total

    self.tmp.oldShifts = oldShifts
    self.tmp.allNurseOptions = allNurseOptions
    self.tmp.nurses = nurses
    self.tmp.lNurses = len(nurses)
    self.tmp.day = day

    self.tmp.worse = worse
    self.tmp.better = better
    self.tmp.equal = equal

    return self.investigate_singleMany(journey = [])

def investigate_singleMany(self, journey, index:int = 0):
    if index == self.tmp.lNurses:
        newPref, newDemand = self.math_singleMany(self.tmp.nurses, self.tmp.day, self.tmp.oldShifts, journey)
        if self.evaluateFO(self.tmp.oldObj, newPref + newDemand, self.tmp.worse, self.tmp.better, self.tmp.equal):
            return True, {"ns": self.tmp.nurses, "d": self.tmp.day, "s": journey, "nP": newPref, "nD": newDemand}
        return False, None
    for option in self.tmp.allNurseOptions[index]:
        s, move = self.investigate_singleMany(journey + option["s"], index+1)
        if s:
            return s, move
    return False, None
