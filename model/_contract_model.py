# coding=utf-8
from typing import List, NewType
import gurobipy as gp
from gurobipy import GRB

MEMBER_OF_MODEL = "MEMBER_OF_MODEL"

TwoDimVar = NewType("TwoDimVar", List[List[gp.Var]]);
ThreeDimVar = NewType("ThreeDimVar", List[List[List[gp.Var]]]);

class Model:
    m: gp.Model;
    x: ThreeDimVar;
    k: TwoDimVar;
    y: TwoDimVar;
    z: TwoDimVar;
    v: ThreeDimVar;

    def __init__(self, m: gp.Model, x: ThreeDimVar, k: TwoDimVar, y: TwoDimVar, z: TwoDimVar, v: ThreeDimVar):
        self.m = m
        self.x = x
        self.k = k
        self.y = y
        self.z = z
        self.v = v

    def __str__(self):
        output = f"===== {MEMBER_OF_MODEL} =====\nInfos:\n"
        output += f"I: {len(self.x)}\n"
        output += f"D: {len(self.x[0])}\n"
        output += f"T: {len(self.x[0][0])}\n"
        output += "==============="
        return output