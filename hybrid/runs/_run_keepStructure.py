import random

def run_keep_seqNursesFromModel(self, numberOfNurses:int, rangeOfSequences:int, numberOfTries:int, worse:bool = False, better:bool = False, equal:bool = False):

    day = random.randint(0, self.nurseModel.D-1)

    possibleNurses = []
    for i in range(self.nurseModel.I):
        if day in self.helperVariables.workingDays[i]:
            possibleNurses.append(i)
            
    if len(possibleNurses) < numberOfNurses:
        return False, None
    
    if possibleNurses == numberOfNurses:
        numberOfTries = 1

    tries = 0
    while tries < numberOfTries and self.chronos.stillValidRestrict():

        nurses = random.sample(possibleNurses, k = numberOfNurses)
        
        moves = []
        oldShifts = {}
        newShifts = {}
        for nurse in nurses:
            s, move = self.internal_run_seqFromModel_fixed(nurse, day, rangeOfSequences)
            if not s:
                return False, None

            dayStart = move["d"]
            duration = len(move["s"])

            for d in range(dayStart, dayStart+duration):
                oldShift = self.helperVariables.projectedX[nurse][d]
                newShift = move["s"][d-dayStart]
                if not (d in oldShifts):
                    oldShifts[d] = [oldShift]
                    newShifts[d] = [newShift]
                else:
                    oldShifts[d].append(oldShift)
                    newShifts[d].append(newShift)
                
            moves.append({"n": nurse, "length": duration, "dayStart": dayStart, "s": move["s"]})
                    
        newPref, newDemand = self.math_seqMany(oldShifts, newShifts, moves)
        
        if self.evaluateFO(self.penalties.total, newPref + newDemand, worse, better, equal):
            return True, {"s": moves, "nP": newPref, "nD": newDemand}

        tries += 1

    return False, None