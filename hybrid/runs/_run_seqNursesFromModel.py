import random

def run_seqNurseFromModel(self, numberOfNurses:int, rangeOfSequences:int, worse:bool = False, better:bool = False, equal:bool = False):

    day = random.randint(0, self.nurseModel.D-1)

    possibleNurses = []
    for i in range(self.nurseModel.I):
        if day in self.helperVariables.workingDays[i]:
            possibleNurses.append(i)
            
    if len(possibleNurses) < numberOfNurses:
        return False, None
    
    nurses = random.sample(possibleNurses, k = numberOfNurses)
    
    earliestDay = self.nurseModel.D
    latestDay = 0
    moves = []
    for nurse in nurses:
        s, move = self.run_seqFromModel_fixed(nurse, day, rangeOfSequences)
        if not s:
            return False, None
        if earliestDay > move["d"]:
            earliestDay = move["d"]
        if latestDay < move["d"] + len(move["s"]) - 1:
            latestDay = move["d"] + len(move["s"]) - 1
            
        moves.append({"n": nurse, "length": len(move["s"]), "dayStart": move["d"], "s": move["s"]})
        
    oldShifts = [] #notice: this oldShift is differente: it is the inverse of the other oldshifts - first info here is day, latter the nurse (this is useful fo quicker math)
    for d in range(earliestDay, latestDay+1):
        oldShifts.append([])
        for i in range(len(moves)):
            if d >= moves[i]["dayStart"] and d < moves[i]["dayStart"] + moves[i]["length"]:
                oldShifts[-1].append(self.helperVariables.projectedX[moves[i]["n"]][d])
            else:
                oldShifts[-1].append(-1)
                
    newObj = self.math_manyNurses_daySequence_withFree(oldShifts, earliestDay, moves)
    
    if self.evaluateFO(self.penalties.total, newObj, worse, better, equal):
        return True, {"s": moves}

    return False, None