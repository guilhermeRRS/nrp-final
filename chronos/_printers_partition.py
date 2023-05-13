from ._printers import print_by_pattern

def print_Partition(obj):

    fields = {
        "I": f"[{obj.i0}, {obj.i9}]", 
        "D": f"[{obj.d0}, {obj.d9}]", 
        "T": f"[{obj.t0}, {obj.t9}]", 
    }

    return print_by_pattern(title = "PARTITION", fields = fields)
