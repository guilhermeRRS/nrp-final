# coding=utf-8
import io, logging
from typing import Union
from ._contract_data import Data

def readFile(path):
    sucess = True
    fileConteds = []
    try:	
        with io.open(path, "r", encoding = "utf8") as file:		
            nLine = 1
            for line in file:			
                line = str(line).strip()
                if len(line) > 0:
                    if line[0] != "#":
                        fileConteds.append(line)
                nLine += 1				
            if(nLine == 1):
                sucess = False
                logging.error("Empty file "+path)
    except:
        sucess = False
        logging.exception("File not found "+path)

    return sucess, fileConteds
    
def splitFile(file):
    expectedFields = ["SECTION_HORIZON","SECTION_SHIFTS","SECTION_STAFF","SECTION_DAYS_OFF","SECTION_SHIFT_ON_REQUESTS","SECTION_SHIFT_OFF_REQUESTS","SECTION_COVER"]
    sections = [[],[],[],[],[],[],[]]
    
    i = -1
    for field in expectedFields:
        started = False
        for line in file:
            if not started:
                if line.upper().strip() == field:
                    started = True
                    i += 1
            else:
                if expectedFields.count(line.upper().strip()) == 1:
                    break
                else:
                    sections[i].append(line)
                    
    s_horizon = sections[0]
    s_shift = sections[1]
    s_staff = sections[2]
    s_daysOff = sections[3]
    s_shiftOnRequests = sections[4]
    s_shiftOffRequests = sections[5]
    s_cover = sections[6]
                    
    return s_horizon, s_shift, s_staff, s_daysOff, s_shiftOnRequests, s_shiftOffRequests, s_cover

def work_horizon(block):
    return int(block[0])
        
def work_shift(block):
    shifts = []
    durations = []
    r_t = []
    for line in block:
        line = line.split(",")
        shifts.append(line[0])
        durations.append(int(line[1]))
        r_t.append(line[2])
        
    for i in range(len(r_t)):
        if len(r_t[i]) > 0:
            seq = r_t[i].split("|")
            r_t[i] = []
            for shift in seq:
                r_t[i].append(shifts.index(shift))
        else:
            r_t[i] = []
    
    matrix_r_t = []
    i = 0
    for shift in shifts:
        matrix_r_t.append([])
        for shift in shifts: #yes, the variable shift will be rewriten
            matrix_r_t[-1].append(0)
        for shift in r_t[i]:
            matrix_r_t[i][shift] = 1
        i += 1
        
    return shifts, durations, matrix_r_t
    
def work_staff(block, shifts, horizon):
    nurses = []
    m_max = []
    b_max = []
    b_min = []
    c_max = []
    c_min = []
    o_min = []
    a_max = []
    for line in block:
        line = line.split(",")
        nurses.append(line[0])
        line[1] = line[1].split("|")
        m_max.append([])
        for shift in shifts:
            m_max[-1].append(horizon)
        for data in line[1]:
            data = data.split("=")
            m_max[-1][shifts.index(data[0])] = int(data[1])
        b_max.append(int(line[2]))
        b_min.append(int(line[3]))
        c_max.append(int(line[4]))
        c_min.append(int(line[5]))
        o_min.append(int(line[6]))
        a_max.append(int(line[7]))
        
    return nurses, m_max, b_max, b_min, c_max, c_min, o_min, a_max

def work_daysOff(block, nurses):
    n_i = []
    for nurse in nurses:
        n_i.append([])
        
    for line in block:
        line = line.split(",")
        nurse = nurses.index(line[0])
        line = line[1:]
        for dia in line:
            n_i[nurse].append(int(dia))
            
    return n_i
    
def work_shiftOn_or_OffRequests(block, nurses, horizon, shifts):
    matrix = []
    for nurse in nurses:
        matrix.append([])
        for i in range(horizon):
            matrix[-1].append([])
            for shift in shifts:
                matrix[-1][-1].append(0)
    
    for line in block:
        line = line.split(",")
        matrix[nurses.index(line[0])][int(line[1])][shifts.index(line[2])] = int(line[3])
        
    return matrix
    
def work_cover(block, horizon, shifts):
    demands = []
    w_min = []
    w_max = []
    for i in range(horizon):
        demands.append([])
        w_min.append([])
        w_max.append([])
        for shift in shifts:
            demands[-1].append(0)
            w_min[-1].append(0)
            w_max[-1].append(0)
            
    for line in block:
        line = line.split(",")
        dia = int(line[0])
        shift = shifts.index(line[1])
        demands[dia][shift] = int(line[2])
        w_min[dia][shift] = int(line[3])
        w_max[dia][shift] = int(line[4])
        
    return demands, w_min, w_max
    
def _get_data(self):

    sucess, fileConteds = readFile(self.pathData)
    
    if(sucess):
        s_horizon, s_shift, s_staff, s_daysOff, s_shiftOnRequests, s_shiftOffRequests, s_cover = splitFile(fileConteds)
        
        allData = {}
        
        allData["horizon"] = work_horizon(s_horizon)
        allData["shifts"], allData["durations"], allData["r_t"] = work_shift(s_shift)
        allData["nurses"], allData["m_max"], allData["b_max"], allData["b_min"], allData["c_max"], allData["c_min"], allData["o_min"], allData["a_max"] = work_staff(s_staff, allData["shifts"], allData["horizon"])
        allData["n_i"] = work_daysOff(s_daysOff, allData["nurses"])
        allData["q"] = work_shiftOn_or_OffRequests(s_shiftOnRequests, allData["nurses"], allData["horizon"], allData["shifts"])
        allData["p"] = work_shiftOn_or_OffRequests(s_shiftOffRequests, allData["nurses"], allData["horizon"], allData["shifts"])
        allData["demands"], allData["w_min"], allData["w_max"] = work_cover(s_cover, allData["horizon"], allData["shifts"])
        
        sucess, sets, parameters = convertFormat(allData)
        
        return True, Data(D = sets["D"], W = sets["W"], I = sets["I"], T = sets["T"], R_t = sets["R_t"], N_i = sets["N_i"],
                                l_t = parameters["l_t"], m_max = parameters["m_max"], b_min = parameters["b_min"], b_max = parameters["b_max"],
                                c_min = parameters["c_min"], c_max = parameters["c_max"], o_min = parameters["o_min"], a_max = parameters["a_max"],
                                q = parameters["q"], p = parameters["p"], u = parameters["u"], w_min = parameters["w_min"], w_max = parameters["w_max"])
        
    return False, None
    
def convertFormat(data):

    sets = {}
    parameters = {}
    #set of days
    sets["D"] = []
    for i in range(data["horizon"]):
        sets["D"].append(i)
    #set of weeks
    sets["W"] = []
    for i in range(int(data["horizon"] / 7)):
        sets["W"].append(i)
    #set of nurses
    sets["I"] = data["nurses"]
    #set of shifts
    sets["T"] = data["shifts"]
        
    
    #set(in fact, a matrix) of forbbiden sequence of shifts
    sets["R_t"] = data["r_t"]
    
    #set of days a nurse i \in I cant be allocated
    sets["N_i"] = data["n_i"]
    
    #duration of shift t \in T in minutes
    parameters["l_t"] = data["durations"]
        
    #maximum number of shifts of type t \in T that a nurse i \in I can be allocated
    parameters["m_max"] = data["m_max"]
    
    #minimum TIME a nurse i \in I must work in the horizon
    parameters["b_min"] = data["b_min"]
    #maximum TIME a nurse i \in I must work in the horizon
    parameters["b_max"] = data["b_max"]
    #minimum number of consecutive shifts (days of job) a nurse i \in I must work
    parameters["c_min"] = data["c_min"]
    #maximum number of consecutive shifts (days of job) a nurse i \in I must work
    parameters["c_max"] = data["c_max"]
    #minimum number of consecutive free days a nurse i \in I must work
    parameters["o_min"] = data["o_min"]
    #maximum number of weekends a nurse i \in I can work
    parameters["a_max"] = data["a_max"]
    
    parameters["q"] = data["q"]
    parameters["p"] = data["p"]
    parameters["u"] = data["demands"]
    parameters["w_min"] = data["w_min"]
    parameters["w_max"] = data["w_max"]
    
    return True, sets, parameters