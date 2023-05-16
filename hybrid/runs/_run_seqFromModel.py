import random

from model import GurobiOptimizedOutput

def run_seqFromModel(self, rangeOfSequences:int, numberOfTries:int , worse:bool = False, better:bool = False, equal:bool = False): #this is random

    nurse = random.randint(0, self.nurseModel.I-1)
    day = random.choice(self.helperVariables.workingDays[nurse])
    
    x = self.parallelModels[nurse]["x"]
    m = self.parallelModels[nurse]["m"]

    restrictions = []
    workingDays = self.helperVariables.workingDays[nurse]
    freeDays = [i for i, x in enumerate(self.helperVariables.projectedX[nurse]) if x < 0]
    
    restrictions.append(m.addConstr(sum((1 - x[d][t]) for t in range(self.nurseModel.T) for d in workingDays) + sum(x[d][t] for t in range(self.nurseModel.T) for d in freeDays) >= 1))

    dayStart, dayEnd = self.getRangeRewrite(nurse, day, rangeOfSequences)
    
    freededDays = []
    for d in range(dayStart, dayEnd+1):
        freededDays.append(d)
        for t in range(self.nurseModel.T):
            x[d][t].lb = 0
            x[d][t].ub = 1

    tries = 0
    while tries < numberOfTries and self.chronos.stillValidRestrict():

        m.setParam("TimeLimit", self.chronos.timeLeft())
            
        m.update()
        self.chronos.startCounter(f"Internal optinization number {tries}")
        m.optimize()
        self.chronos.stopCounter()

        gurobiReturn = GurobiOptimizedOutput(m)

        self.chronos.printObj("SEQ_FROM_MODEL", "SOLVER_GUROBI_OUTPUT", gurobiReturn)

        if gurobiReturn.valid():
            newX = []
            for d in range(dayStart, dayEnd+1):
                newX.append(-1)
                for t in range(self.nurseModel.T):
                    if x[d][t].x >= 0.5:
                        newX[-1] = t
                        break
                    
            for d in range(dayStart, dayEnd+1):
                for t in range(self.nurseModel.T):
                    x[d][t].lb = self.currentSol.solution[nurse][d][t]
                    x[d][t].ub = self.currentSol.solution[nurse][d][t]
                    
            newPref, newDemand = self.math_sequence(nurse, dayStart, dayEnd, self.helperVariables.projectedX[nurse][dayStart:(dayEnd+1)], newX)
            if self.evaluateFO(self.penalties.total, newPref + newDemand, worse, better, equal):
                for restriction in restrictions:
                    m.remove(restriction)
                return True, {"n": nurse, "d": dayStart, "s": newX, "nP": newPref, "nD": newDemand}
            else:
                #here the restriction may be softer, it means, the day squence may be equal, but shifts must change
                workingDays = []
                freeDays = []
                for d in range(self.nurseModel.D):
                    for t in range(self.nurseModel.T):
                        if x[d][t].x >= 0.5:
                            workingDays.append(d)
                            break
                    if not (d in workingDays):
                        freeDays.append(d)
                restrictions.append(m.addConstr(sum((1 - x[d][t]) for t in range(self.nurseModel.T) for d in workingDays) + sum(x[d][t] for t in range(self.nurseModel.T) for d in freeDays) >= 1))

        else:
            for restriction in restrictions:
                m.remove(restriction)
                
            for d in range(dayStart, dayEnd+1):
                for t in range(self.nurseModel.T):
                    x[d][t].lb = self.currentSol.solution[nurse][d][t]
                    x[d][t].ub = self.currentSol.solution[nurse][d][t]
                    
            return False, None

        tries += 1

    for restriction in restrictions:
        m.remove(restriction)
        
    for d in range(dayStart, dayEnd+1):
        for t in range(self.nurseModel.T):
            x[d][t].lb = self.currentSol.solution[nurse][d][t]
            x[d][t].ub = self.currentSol.solution[nurse][d][t]
    return False, None