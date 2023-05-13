from abc import ABC, abstractmethod
from model import Model
import gurobipy as gp
from gurobipy import GRB

from partition import Partition

class MipInterface(ABC):

    model:Model

    def __init__(self, model:Model):
        self.model = model

    def relaxWindow(self, partition: Partition):
        for d in range(partition.d0, partition.d9):
            for i in range(partition.i0, partition.i9):
                for t in range(partition.t0, partition.t9):
                    
                    self.model.x[i][d][t].vtype = GRB.CONTINUOUS
                    self.model.x[i][d][t].lb = 0
                    self.model.x[i][d][t].ub = 1

                    self.model.v[i][d][t].vtype = GRB.CONTINUOUS
                    self.model.v[i][d][t].lb = 0
                if d % 7 == 6:
                    w = int((d - 6)/7)
                    self.model.k[i][w].vtype = GRB.CONTINUOUS
                    self.model.k[i][w].lb = 0
                    self.model.k[i][w].ub = 1
            for t in range(partition.t0, partition.t9):
                self.model.y[d][t].vtype = GRB.CONTINUOUS
                self.model.y[d][t].lb = 0
                self.model.z[d][t].vtype = GRB.CONTINUOUS
                self.model.z[d][t].lb = 0

    def intWindow(self, partition: Partition):
        for d in range(partition.d0, partition.d9):
            for i in range(partition.i0, partition.i9):
                for t in range(partition.t0, partition.t9):
                    
                    self.model.x[i][d][t].vtype = GRB.BINARY

                    self.model.v[i][d][t].vtype = GRB.INTEGER
                if d % 7 == 6:
                    w = int((d - 6)/7)
                    self.model.k[i][w].vtype = GRB.BINARY
            for t in range(partition.t0, partition.t9):
                self.model.y[d][t].vtype = GRB.INTEGER
                self.model.z[d][t].vtype = GRB.INTEGER

    def fixWindows(self, partition: Partition):

        for i in range(partition.i0, partition.i9):
            for d in range(partition.d0, partition.d9):
                for t in range(partition.t0, partition.t9):
                    newVal = 1 if self.model.x[i][d][t].x >= 0.5 else 0
                    self.model.x[i][d][t].lb = newVal
                    self.model.x[i][d][t].ub = newVal

    def unfixWindows(self, partition: Partition):
        for i in range(partition.i0, partition.i9):
            for d in range(partition.d0, partition.d9):
                for t in range(partition.t0, partition.t9):
                    self.model.x[i][d][t].lb = 0
                    self.model.x[i][d][t].ub = 1