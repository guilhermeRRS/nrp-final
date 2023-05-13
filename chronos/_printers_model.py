from ._printers import print_by_pattern

def print_GurobiOptimizedOutput(obj):
    objVal = -1
    if obj.valid():
        objVal = obj.m.objVal
    
    fields = {
        "Status": obj.status, 
        "SolCount": obj.solCount, 
        "Valid": obj.valid(), 
        "Obj": objVal, 
    }

    return print_by_pattern(title = "GUROBI_OPTIMIZE_OUTPUT", fields = fields)

def print_NurseModel(obj):
    
    fields = {
        "Is there data": obj.data != None, 
        "Success data": obj.s_data, 
        "Is there model?": obj.model != None, 
        "Success model?": obj.s_model, 
        "Is there solution?": obj.solution != None, 
        "Success solution?": obj.s_solution, 
    }

    return print_by_pattern(title = "MEMBER_OF_MODEL", fields = fields)

def print_Solution(obj):
    
    fields = {
        "I": len(obj.solution), 
        "D": len(obj.solution[0]), 
        "T": len(obj.solution[0][0]), 
        "Hash": hash(str(obj.solution)), 
    }

    return print_by_pattern(title = "MEMBER_OF_SOLUTION", fields = fields)
