import itertools


def generate_cover(self, newStructure, workingDays, forbidden, nurse, dayStart, dayEnd, minWorkload, maxWorkload, range_min, range_max, maxTries:int):

    durationOfJourneys = []

    iter = dayStart
    while iter <= dayEnd:
        
        sizeWork = 0
        if newStructure[iter-dayStart] == 1:
            while iter <= dayEnd and newStructure[iter-dayStart] == 1:
                sizeWork += 1
                iter += 1
            durationOfJourneys.append(sizeWork)
        else:
            iter += 1

    tryCounter = 0
    smaller = 0
    bigger = 0
    while tryCounter < maxTries:
        
        theCover = []
        addWorkLoad = 0
        allShifts = []
        failed = False
        for duration in durationOfJourneys:
            s, littleCover = self.getOptionBySize(duration, forbidden, nurse, dayStart, dayEnd, allShifts)
            if not s:
                print("$$$")
                failed = True
                break
            allShifts += littleCover["s"]
            theCover.append(littleCover)
            addWorkLoad += theCover[-1]["w"]
            theCover[-1] = theCover[-1]["s"]

        if not failed:
            if addWorkLoad >= minWorkload and addWorkLoad <= maxWorkload:
                if self.verify_generateCover_mmax(nurse, dayStart, theCover, allShifts):
                    input("!!!")
                    return True, range_min, range_max, {"n": nurse, "dayStart": dayStart, "s": theCover, "w": addWorkLoad}
                else:
                    input("@@")
            else:
                if addWorkLoad < minWorkload:
                    smaller += 1
                if addWorkLoad > maxWorkload:
                    bigger += 1
        tryCounter += 1

    if smaller / (bigger+1) > 1.8:
        range_min += 1
    if bigger / (smaller+1) > 1.8:
        range_max -= 1
        
    return False, range_min, range_max, None

def verify_generateCover_mmax(self, nurse, dayStart, theCover, allShifts):
    print(theCover)
    oldShifts = self.helperVariables.projectedX[nurse][dayStart:(dayStart+len(theCover))]
    affectedShifts = list(dict.fromkeys(allShifts))
    for shift in affectedShifts:
        if self.helperVariables.shiftTypeCounter[nurse][shift] - oldShifts.count(shift) + allShifts.count(shift) > self.nurseModel.data.parameters.m_max[nurse][shift]:
            print(self.helperVariables.shiftTypeCounter[nurse][shift], self.nurseModel.data.parameters.m_max[nurse][shift])
            print( oldShifts.count(shift), allShifts.count(shift))
            return False
    return True