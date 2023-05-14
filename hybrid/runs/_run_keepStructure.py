import random

from model import GurobiOptimizedOutput

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

    dayStarts = []
    dayEnds = []
    for i in range(self.nurseModel.I):
        dayStart, dayEnd = self.getRangeRewrite(nurse, day, rangeOfSequences)
        dayStarts.append(dayStart)
        dayEnds.append(dayEnd)

    sm_x = self.modelShift.sm_x
    m = self.modelShift.m

    tries = 0
    while tries < numberOfTries and self.chronos.stillValidRestrict():

        nurses = random.sample(possibleNurses, k = numberOfNurses)
        constraints = []
        for i in range(numberOfNurses):
            
            dayStart = dayStarts[i]
            dayEnd = dayEnds[i]
            for d in range(dayStart, dayEnd+1):
                if d in self.helperVariables.projectedX[i]:
                    constraints.append(m.addConstr(sum(sm_x[i][d][t] for t in range(self.nurseModel.T)) == 1))
                else:
                    constraints.append(m.addConstr(sum(sm_x[i][d][t] for t in range(self.nurseModel.T)) == 0))

        ##run here
        
        self.chronos.startCounter(f"Internal optinization number {tries}")
        m.optimize()
        self.chronos.stopCounter()

        gurobiReturn = GurobiOptimizedOutput(m)

        self.chronos.printObj("SEQ_FROM_MODEL", "SOLVER_GUROBI_OUTPUT", gurobiReturn)

        if gurobiReturn.valid():
        
            if self.evaluateFO(self.penalties.total, self.modelShift.preference_total + self.modelShift.demand, worse, better, equal):
                return True

        tries += 1

    return False, None