import random, copy

def run_single(self, worse:bool = False, better:bool = False, equal:bool = False): #this is random

    nurse = random.randint(0, self.nurseModel.I-1)
    day = random.choice(self.helperVariables.workingDays[nurse])

    ###the edge
    shiftBefore = "free"
    if day - 1 >= 0:
        shiftBefore = self.shiftFreeMark(self.helperVariables.projectedX[nurse][day-1])
    shifAfter = "free"
    if day + 1 < self.nurseModel.D:
        shifAfter = self.shiftFreeMark(self.helperVariables.projectedX[nurse][day+1])
    
    ###all options that fits constraints
    oldShift = self.helperVariables.projectedX[nurse][day]

    options = self.getSingle(shiftBefore, shifAfter, nurse, day, oldShift)
    
    if len(options) == 0:
        return False, None
    
    ###get a random option
    random.shuffle(options)
    oldObj = self.penalties.total
    for opt in options:
        newShift = opt["s"][0]
        newPref, newDemand = self.math_single(nurse, day, oldShift, newShift)
        
        if self.evaluateFO(oldObj, newPref + newDemand, worse, better, equal):
            return True, {"n": nurse, "d": day, "s": newShift, "nP": newPref, "nD": newDemand}
    
    return False, None