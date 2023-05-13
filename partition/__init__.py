from typing import List
from chronos import *
from enum import Enum

class PartitionSize(Enum):

    ALL = 0

    UNITARY = 1
    COUPLE = 2

    QUARTER = 3
    HALF = 4

class Partition:
    i0: int
    i9: int
    d0: int
    d9: int
    t0: int
    t9: int

    def __init__(self, i0: int, i9: int, d0: int, d9: int, t0: int, t9: int):
        self.i0 = i0
        self.i9 = i9
        self.d0 = d0
        self.d9 = d9
        self.t0 = t0
        self.t9 = t9

    def __str__(self):
        return print_Partition(self)

class PartitionHolder:

    I: int
    D: int
    T: int

    partitions: List[Partition]

    def __init__(self, I, D, T):
        self.I = I
        self.D = D
        self.T = T

    def all(self):
        return Partition(i0 = 0, i9 = self.I, d0 = 0, d9 = self.D, t0 = 0, t9 = self.T)

    def _segmentPartition(self, size: int, step: PartitionSize, week: bool = False):
        
        if step == PartitionSize.ALL:
            return [[0, size]]

        if(week):
            size = int(size/7)

        if (step == PartitionSize.HALF and size < 2) or (step == PartitionSize.QUARTER and size < 4):
            step = PartitionSize.UNITARY

        output = []
        ###number
        if step == PartitionSize.UNITARY:
            for i in range(size):
                output.append([i, i+1])
        elif step == PartitionSize.COUPLE:
            for i in range(0, size, 2):
                output.append([i, min(i + 2, size)])
        ###percent
        elif step == PartitionSize.HALF:
            middle = int((size - (size % 2)) / 2)
            output = [[0, middle], [middle, size]]
        elif step == PartitionSize.QUARTER:
            littleStep = int((size - (size % 4)) / 4)
            firstMark = littleStep + (0 if size % 4 < 1 else 1)
            secondMark = firstMark + littleStep + (0 if size % 4 < 2 else 1)
            thirdMark = secondMark + littleStep + (0 if size % 4 < 3 else 1)
            output = [[0, firstMark], [firstMark, secondMark], [secondMark, thirdMark], [thirdMark, size]]

        if(week):
            for i in range(len(output)):
                output[i] = [7*output[i][0],7*output[i][1]]

        return output

    def createPartition(self, iPartitionSize: PartitionSize, dPartitionSize: PartitionSize, tPartitionSize: PartitionSize = None):
        if tPartitionSize == None:
            tPartitionSize = PartitionSize.ALL

        iSegments = self._segmentPartition(self.I, iPartitionSize)
        dSegments = self._segmentPartition(self.D, dPartitionSize, week=True)
        tSegments = self._segmentPartition(self.T, tPartitionSize)

        self.partitions = []
        for iSegment in iSegments:
            for dSegment in dSegments:
                for tSegment in tSegments:
                    self.partitions.append(Partition(i0 = iSegment[0], i9 = iSegment[1], d0 = dSegment[0], d9 = dSegment[1], t0 = tSegment[0], t9 = tSegment[1]))

    def popPartition(self):
        if len(self.partitions) > 0:
            output = self.partitions[0]
            self.partitions.remove(output)
            return output
        return None
        
    def __str__(self):
        output = "PartitionHolder\n"
        output += f"Size: {len(self.partitions)}\n"
        for partition in self.partitions:
            output += partition.__str__()
        return output
    
    def partitionSize(self):
        return len(self.partitions)