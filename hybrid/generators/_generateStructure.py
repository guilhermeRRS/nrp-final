import random

def generate_structure(self, nurse, dayStart, dayEnd, maximumDaysWorking, minimumDaysWorking, range_min, range_max):

    newStructure = []
    workingDays = []

    iter = dayStart
    if dayStart == 0:
        while random.random() >= 0.5:
            newStructure.append(0)
            iter += 1

    while len(workingDays) < dayEnd - dayStart and maximumDaysWorking - len(workingDays) >= self.nurseModel.data.parameters.c_min[nurse]:
        daysToWork = random.randint(self.nurseModel.data.parameters.c_min[nurse], min(self.nurseModel.data.parameters.c_max[nurse], maximumDaysWorking - len(workingDays)))
        nextN_i = -1
        ableToWork = 0
        for d in range(iter, iter + daysToWork):
            if d in self.nurseModel.data.sets.N_i[nurse]:
                nextN_i = d
                break
            else:
                ableToWork += 1
        if nextN_i >= 0:
            if ableToWork >= self.nurseModel.data.parameters.c_min[nurse]:
                daysToWork = ableToWork
            else:
                daysToWork = 0
        for d in range(daysToWork):
            workingDays.append(iter)
            newStructure.append(1)
            iter += 1
        daysToFree = self.nurseModel.data.parameters.o_min[nurse]
        for d in range(daysToFree):
            newStructure.append(0)
            iter += 1
        while random.random() >= 0.5:
            newStructure.append(0)
            iter += 1

    #here we set the right size
    while iter <= dayEnd:
        newStructure.append(0)
        iter += 1

    iter -= 1
    while iter > dayEnd:
        newStructure.pop()
        if iter in workingDays:
            workingDays.remove(iter)
        iter -= 1

    #here we garantee the interval will fit without break any restriction
    iter = len(newStructure) - 1
    daysFree = 0
    if dayEnd < self.nurseModel.D - 1:
        while iter >= 0:
            if newStructure[iter] == 0:
                daysFree += 1
            else:
                break
            iter -= 1
        if daysFree < self.nurseModel.data.parameters.o_min[nurse]:
            iter = len(newStructure) - 1
            daysFree = 0
            while daysFree < self.nurseModel.data.parameters.o_min[nurse]:
                if newStructure[iter] != 0:
                    newStructure[iter] = 0
                    workingDays.remove(iter+dayStart)
                daysFree += 1
                iter -= 1

            #now we verify if the change didnt affect the minimum number of days working
            lastDayWorking = workingDays[-1]
            mustBeworking = lastDayWorking - self.nurseModel.data.parameters.c_min[nurse] + 1
            if not (mustBeworking in workingDays):
                iter = lastDayWorking - dayStart
                while iter >= 0:
                    if newStructure[iter] == 0:
                        break
                    else:
                        newStructure[iter] = 0
                        workingDays.remove(iter+dayStart)

    numberOfDaysWorking = sum(newStructure)

    #self.calibrate(newStructure, workingDays, numberOfDaysWorking, dayStart, dayEnd, nurse, range_min, range_max)

    if numberOfDaysWorking < minimumDaysWorking or numberOfDaysWorking > maximumDaysWorking:
        return False, None, None

    #here we verify restriction 10 -> days thar the nurse must rest
    '''
    for day in self.nurseModel.data.sets.N_i[nurse]:
        if day in workingDays:
            input("++")
            return False, None, None
    input("--")'''
    return True, newStructure, workingDays
    
def calibrate(self, newStructure, workingDays, numberOfDaysWorking, dayStart, dayEnd, nurse, range_min, range_max):
    
    '''
    if numberOfDaysWorking < range_min or numberOfDaysWorking > range_max:        
        durationOfJourneys = []

        iter = dayStart
        while iter <= dayEnd:
            
            sizeWork = 0
            if newStructure[iter-dayStart] == 1:
                firstJourney = iter
                while iter <= dayEnd and newStructure[iter-dayStart] == 1:
                    sizeWork += 1
                    iter += 1
                lastJourney = iter - 1
                durationOfJourneys.append({"d": sizeWork, "f": firstJourney, "l": lastJourney})
            else:
                iter += 1
    '''

    if numberOfDaysWorking < range_min:
        return self.insertMode(newStructure, workingDays, numberOfDaysWorking, nurse, dayStart, range_min)
    
    elif numberOfDaysWorking > range_max:
        return self.removeMode(newStructure, workingDays, numberOfDaysWorking, nurse)

    return newStructure, workingDays

def insertMode(self, newStructure, workingDays, numberOfDaysWorking, nurse, dayStart, range_min):
    
    freeDays = [i for i, x in enumerate(newStructure) if x == 0]
    while iter < 10*len(newStructure) and numberOfDaysWorking < range_min:

        dayIndex = random.choice(freeDays)
        day = dayIndex+ dayStart
        #the first day of schedule
        if day == 0:
            if newStructure[dayIndex+1] == 0:
                numberOfDaysWorking, newStructure, workingDays = self.tryBefore()
            else:
                numberOfDaysWorking, newStructure, workingDays = self.tryAfter()
        #the last day of the schedule
        elif day == self.nurseModel.D-1:
            if newStructure[dayIndex-1] == 0:
                numberOfDaysWorking, newStructure, workingDays = self.tryBefore()
            else:
                numberOfDaysWorking, newStructure, workingDays = self.tryAfter()
        #any other day
        else:
            #any other day tha follows o_min to outer region
            if dayIndex >= self.nurseModel.data.parameters.o_min[nurse] and dayIndex < len(newStructure)-self.nurseModel.data.parameters.o_min[nurse]:
                numberOfDaysWorking, newStructure, workingDays = self.tryBefore()
                numberOfDaysWorking, newStructure, workingDays = self.tryAfter()

        iter += 1

    return newStructure, workingDays

def removeMode(self, newStructure, workingDays, numberOfDaysWorking, durationOfJourneys, nurse):
    print("@@")
    input(durationOfJourneys)