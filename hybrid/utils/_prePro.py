import json
from model import Solution

def preProcessFromSolution(self):
    
    self.helperVariables.shiftTypeCounter = []
    self.helperVariables.workloadCounter = []
    self.helperVariables.projectedX = []
    self.helperVariables.workingDays = []

    self.penalties.preference_total = 0
    
    self.penalties.numberNurses = []
    for d in range(self.nurseModel.D):
        self.penalties.numberNurses.append([])
        for t in range(self.nurseModel.T):
            self.penalties.numberNurses[-1].append(0)
    
    #print("Calculating")
    self.parallelModels = []
    self.currentSol = Solution().loadSolution(self.nurseModel.solution.solution)
    for i in range(self.nurseModel.I):
        self.helperVariables.shiftTypeCounter.append([])
        self.helperVariables.workloadCounter.append(0)
        self.helperVariables.projectedX.append([])
        self.helperVariables.workingDays.append([])
        
        m, x = self.generateSingleNurseModel(i)
        m.setParam("Solutionlimit", 1)
        m.setParam("OutputFlag", 0)
        self.parallelModels.append({"m": m, "x": x})
        
        for t in range(self.nurseModel.T):
            self.helperVariables.shiftTypeCounter[-1].append(0)
        
        for d in range(self.nurseModel.D):
            self.helperVariables.projectedX[-1].append(-1)
            for t in range(self.nurseModel.T):
                self.penalties.preference_total += self.nurseModel.data.parameters.p[i][d][t]*self.nurseModel.solution.solution[i][d][t]+self.nurseModel.data.parameters.q[i][d][t]*(1 - self.nurseModel.solution.solution[i][d][t])
    
                self.nurseModel.model.x[i][d][t].ub = self.nurseModel.solution.solution[i][d][t]
                self.nurseModel.model.x[i][d][t].lb = self.nurseModel.solution.solution[i][d][t]
                 
                if self.nurseModel.solution.solution[i][d][t] >= 0.5:
                    self.helperVariables.shiftTypeCounter[-1][t] += 1
                    self.helperVariables.workloadCounter[-1] += self.nurseModel.data.parameters.l_t[t]
                    self.helperVariables.projectedX[-1][d] = t
                    self.helperVariables.workingDays[-1].append(d)
                    self.penalties.numberNurses[d][t] += 1
    
    #print("Demanding & setting")
    self.penalties.demand = 0

    r_t_plain = []
    self.helperVariables.oneInnerJourney_rt = {"free": {"free": []}}
    
    #equivalence = []
    for t in range(self.nurseModel.T):
        #equivalence.append(self.nurseModel.data.sets.R_t.index(self.nurseModel.data.sets.R_t[t]))
        for d in range(self.nurseModel.D):
            numberNurses = self.penalties.numberNurses[d][t]
            neededNurses = self.nurseModel.data.parameters.u[d][t]
            addingPenalty = 0
            if numberNurses < neededNurses:
                addingPenalty = (neededNurses - numberNurses)*self.nurseModel.data.parameters.w_min[d][t]
                self.penalties.demand += addingPenalty
            elif numberNurses > neededNurses:
                addingPenalty = (numberNurses - neededNurses)*self.nurseModel.data.parameters.w_max[d][t]
                self.penalties.demand += addingPenalty

        r_t_plain.append([i for i, x in enumerate(self.nurseModel.data.sets.R_t[t]) if x == 0])

        self.helperVariables.oneInnerJourney_rt["free"]["free"].append({"s": [t], "w": self.computeLt([t])})

        self.helperVariables.oneInnerJourney_rt["free"][t] = []
        self.helperVariables.oneInnerJourney_rt[t] = {"free": []}
        #not needed more, the max of all instances is 6 workDays

        for t2 in range(self.nurseModel.T):
            self.helperVariables.oneInnerJourney_rt[t][t2] = []
            
    self.penalties.total = self.penalties.demand + self.penalties.preference_total

    #print("The monster")
    highest_cmax = max(self.nurseModel.data.parameters.c_max)
    self.highest_cmax = highest_cmax

    sizedTwoStarting = {}
    for t in range(self.nurseModel.T):
        sizedTwoStarting[t] = []
    
    #print("The monster for sized 2")
    sizedTwo = []
    for tStart in range(self.nurseModel.T):
        for tEnd in r_t_plain[tStart]:
            newSequence = [tStart, tEnd]
            sizedTwo.append(newSequence)
            sizedTwoStarting[tStart].append(newSequence)
            
            ##Setting the global vars
            freeFirst = [tStart]
            freeAfter = [tEnd]
            self.helperVariables.oneInnerJourney_rt["free"][tEnd].append({"s": freeFirst, "w": self.computeLt(freeFirst)})
            self.helperVariables.oneInnerJourney_rt[tStart]["free"].append({"s": freeAfter, "w": self.computeLt(freeAfter)})

    #print("The monster for sized 3")
    for sequence1 in sizedTwo:
        tEndingFirst = sequence1[-1]
        for sequence2 in sizedTwoStarting[tEndingFirst]:
            newSequence = [sequence1[0], sequence1[1], sequence2[1]]
            
            ##Setting the global vars
            innerSeq = [sequence1[1]]
            self.helperVariables.oneInnerJourney_rt[sequence1[0]][sequence2[-1]].append({"s": innerSeq, "w": self.computeLt(innerSeq)})
    

'''
def preProcess(self):
    self.preProcessFromSolution()
    self.solutionData = {
        "helperVariables": {
            "shiftTypeCounter": self.helperVariables.shiftTypeCounter,
            "workloadCounter": self.helperVariables.workloadCounter,
            "projectedX": self.helperVariables.projectedX,
            "workingDays": self.helperVariables.workingDays,
        },
        "penalties": {
            "preference_total": self.penalties.preference_total,
            "demand": self.penalties.demand,
            "numberNurses": self.penalties.numberNurses,
            "total": self.penalties.total,
        }
    }
    self.problemJourneyData = {
        "highest_cmax": self.highest_cmax,
        "oneInnerJourney_rt": self.helperVariables.oneInnerJourney_rt,
    } 

###################################################################

#########                   Getter

###################################################################

def getPreProcessData(self):
    instancia = self.instance
    f = open(f'{instancia}.solutionData.json')
    solutionData = json.load(f)
    
    self.helperVariables.shiftTypeCounter = solutionData["helperVariables"]["shiftTypeCounter"]
    self.helperVariables.workloadCounter = solutionData["helperVariables"]["workloadCounter"]
    self.helperVariables.projectedX = solutionData["helperVariables"]["projectedX"]
    self.helperVariables.workingDays = solutionData["helperVariables"]["workingDays"]
    
    self.penalties.preference_total = solutionData["penalties"]["preference_total"]
    self.penalties.numberNurses = solutionData["penalties"]["numberNurses"]
    self.penalties.demand = solutionData["penalties"]["demand"]
    self.penalties.total = solutionData["penalties"]["total"]

    f = open(f'{instancia}.problemJourneyData.json')
    problemJourneyData = json.load(f)
    
    self.highest_cmax = problemJourneyData["highest_cmax"]
    self.helperVariables.oneInnerJourney_rt = problemJourneyData["oneInnerJourney_rt"]

'''