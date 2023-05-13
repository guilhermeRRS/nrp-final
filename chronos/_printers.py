import datetime


def print_ErrorExpectionObj(obj):

    fields = {
        "Type": obj.type, 
        "Filename": obj.fname, 
        "Line": obj.line, 
    }

    return print_by_pattern(title = "ERROR_EXCEPTION_OBJ", fields = fields)

def print_ChronosCounter(obj):

    fields = {
        "Name": obj.name, 
        "Log": obj.log, 
        "Start": obj.start, 
        "Stop Condition": obj.stop if obj.stop != None else 'Not set',
        "Valid": obj.stillValid() if obj.stop != None else 'Not set',
        "TimeLeft": obj.timeLeft() if obj.stillValid() == True else 0,
    }

    return print_by_pattern(title = "CHRONOS_COUNTER", fields = fields)


def print_Chronos(obj):

    fields = {
        "Root time": obj.rootTime, 
        "Time limit": obj.timeLimit, 
        "Valid": obj.stillValid(), 
        "TimeLeft": obj.timeLeft() if obj.stillValid() == True else 0,
        "Size": len(obj.timeMarks)
    }

    return print_by_pattern(title = "CHRONOS_MANAGER", fields = fields)

def print_by_pattern(title: str, fields: map):
    output = f"===== {title} =====\n"
    keysList = list(fields.keys())
    for key in keysList:
        output += f"{key}:\t\t{fields[key]}\n"
    output += "==============="
    return output