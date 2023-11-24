def getSingle(self, shiftBefore, shifAfter, nurse, day, oldShift):
    
    minWorkload = self.nurseModel.data.parameters.b_min[nurse] - (self.helperVariables.workloadCounter[nurse] - self.nurseModel.data.parameters.l_t[oldShift])
    maxWorkload = self.nurseModel.data.parameters.b_max[nurse] - (self.helperVariables.workloadCounter[nurse] - self.nurseModel.data.parameters.l_t[oldShift])
    
    allOptions = self.helperVariables.oneInnerJourney_rt[shiftBefore][shifAfter]
    validOptions = []
    for option in allOptions:
        if option["s"] != oldShift:
            if minWorkload <= option["w"] and maxWorkload >= option["w"]:
                t = option["s"][0]
                if self.nurseModel.data.parameters.m_max[nurse][t] >= self.helperVariables.shiftTypeCounter[nurse][t] + 1:
                    validOptions.append(option)
    
    return validOptions