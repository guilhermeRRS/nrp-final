def evaluateFO(self, oldObj, newObj, worse:bool = False, better:bool = True, equal:bool = False):

    if better and oldObj > newObj:
        return True
    if worse and oldObj < newObj:
        return True
    if equal and oldObj == newObj:
        return True
    return False
