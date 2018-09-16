import re

VARNAME     = 0
ATTR        = 1
START       = 2
END         = 3
ASSIGNEDREG = 4

ATTR_TEMP = 0
ATTR_SAVE = 1
ATTR_RET  = 2
ATTR_ARG  = 3
ATTR_PTR_STATIC_LOCAL  = 4
ATTR_PTR_STATIC_GLOBAL = 5
ATTR_PTR_DYNAMIC_LOCAL = 6

ALG_NONE = 0

ADDR_PER_WORD = 0x04

INIT_SP_ADDR = 0x20000

FIRST_TIME = -1

#class FuncTable:
#    def __init__(self, funcName):
#    self.funcName = funcName
#    self.start = 0
#    self.end = 0
class MachineStatus:
    def __init__(self):
        self.sp = INIT_SP_ADDR

class RegisterTable:
    def __init__(self, name):
        self.funcName = name
        self.S = [True, True, True, True, True, True, True, True, True]
        self.T = [True, True, True, True, True, True, True, True, True]

    def setRegisterOccupy(self, regName):
        if regName == 'ME':
            return True
        
        ptn = re.match('[TS][0-8]', regName)
        if ptn is None:
            print('Reg ' + regName + ' is not implemented.')
            return False
        else:
            if (regName[0] == 'S'):
                self.S[int(regName[1])] = False
            if (regName[0] == 'T'):
                self.T[int(regName[1])] = False
            return True

    def releaseRegister(self, regName):
        if regName == 'ME':
            return True

        ptn = re.match('[TS][0-8]', regName)
        if ptn is None:
            print('Reg ' + regName + ' is not implemented.')
            return False
        else:
            if (regName[0] == 'S'):
                self.S[int(regName[1])] = True
            if (regName[0] == 'T'):
                self.T[int(regName[1])] = True
            return True
    
    def searchForTempVariable(self):
        for i in range(len(self.T)):
            if (self.T[i] == True):
                return 'T' + str(i) 
        for i in range(len(self.S)):
            if (self.S[i] == True):
                return 'S' + str(i)
        return 'ME'

    def searchForSaveVariable(self):
        for i in range(len(self.S)):
            if (self.S[i] == True):
                return 'S' + str(i)
        return 'ME'

#    def assignForTempVariable(self, assignedReg):
#        regName = self.searchForTempVariable()
#        self.setRegisterOccupy(regName)
#        assignedReg = regName
#            return True
#            return False

#class RegisterAssignmentList:
#    def __init__(self, varName, save, start, end, assignedReg):
#        self.varName = varName
#        self.save = save
#        self.start = start
#        self.end = end
#        self.assignedReg = assignedReg

class VariableTable:
    def __init__(self, name):
        self.funcName = name
        self.table = []
    def addRow(self, varName, attr, start, end, assignedReg): 
        self.table.append([varName, attr, start, end, assignedReg])
    def hasContainedVarName(self, varName):
        for i in range(len(self.table)):
            if (self.table[i][VARNAME] == varName):
                return True
        
        return False
    def searchVariable(self, varName):
        for i in range(len(self.table)):
            if (self.table[i][VARNAME] == varName):
                return i
        
        return FIRST_TIME
#class RegisterAssignmentTableList:
#    def __init__(self):
#        self = []
#    def add(self, funcName):
#        self.append(RegisterAssignmentTable(funcName))

    #def searchVal
#def assignRegister(variableTableList, machine, ALGORITHM):
#
#    for i in range(len(variableTableList)):
#        funcName = variableTableList[i].funcName
#        registerTable = RegisterTable(funcName)
#        
#        for j in range(len(variableTableList[i].table)):
#            if(variableTableList[i].table[j][ATTR] == ATTR_SAVE):
#                assignedreg = registerTable.searchForSaveVariable()
#
#            elif(variableTableList[i].table[j][ATTR] == ATTR_TEMP):
#                assignedreg = registerTable.searchForTempVariable()
#            
#            variableTableList[i].table[j][ASSIGNEDREG] = assignedreg
#            registerTable.getRegister(assignedreg)

def assignRegister(variableTableList, machine, ALGORITHM):

    for i in range(len(variableTableList)):
        assignRegisterInEachTable(variableTableList[i], machine)
         

def assignRegisterInEachTable(varTable, machine):
    regTable = RegisterTable(varTable.funcName)
    for i in range(len(varTable.table)):
        if(varTable.table[i][ATTR] == ATTR_SAVE):
            regName = regTable.searchForSaveVariable()
            varTable.table[i][ASSIGNEDREG] = regName
            regTable.setRegisterOccupy(regName)

        elif(varTable.table[i][ATTR] == ATTR_TEMP):
            regName = regTable.searchForTempVariable()
            varTable.table[i][ASSIGNEDREG] = regName
            regTable.setRegisterOccupy(regName)
        
        elif(varTable.table[i][ATTR] == ATTR_PTR_STATIC_LOCAL):
            machine.sp -= ADDR_PER_WORD * 1
            varTable.table[i][ASSIGNEDREG] = hex(machine.sp)

def makeAllocaInstList():
    alloca_inst_list0 = 'lw ASM FP 0x00'
    alloca_inst_list1 = 'iAddi ASM ASM ' + hex(ADDR_PER_WORD)
    alloca_inst_list2 = 'sw ASM FP 0x00'
    alloca_inst_list3 = 'iSubi SP SP ' + hex(ADDR_PER_WORD)
    alloca_inst_list = []
    alloca_inst_list.append(alloca_inst_list0)
    alloca_inst_list.append(alloca_inst_list1)
    alloca_inst_list.append(alloca_inst_list2)
    alloca_inst_list.append(alloca_inst_list3)
    return '\n'.join(alloca_inst_list)
#def makeAllocaInstList(assignedreg0):
#    alloca_inst_list0 = 'lw ' + assignedreg0 + ' FP 0x00'
#    alloca_inst_list1 = 'iAddi ' + assignedreg0 + ' ' + assignedreg0 + ' ' + hex(ADDR_PER_WORD)
#    alloca_inst_list2 = 'sw ' + assignedreg0 + ' FP 0x00'
#    alloca_inst_list3 = 'iSubi SP SP ' + hex(ADDR_PER_WORD)
#    alloca_inst_list4 = 'iAdd ' + assignedreg0 + ' SP ZERO'
#    alloca_inst_list = []
#    alloca_inst_list.append(alloca_inst_list0)
#    alloca_inst_list.append(alloca_inst_list1)
#    alloca_inst_list.append(alloca_inst_list2)
#    alloca_inst_list.append(alloca_inst_list3)
#    alloca_inst_list.append(alloca_inst_list4)
#    return '\n'.join(alloca_inst_list)

def makeStoreInstList(string):
    imm0 = string[2][0:-1]
    dst = string[4][0:-1]
    
    store_inst_list = []
    
    #pointer?
    if(string[3][-1:] == '*'):
        store_inst_list0 = 'iAddi ASM ZERO ' + hex(int(imm0) >> 16)
        store_inst_list1 = 'Lsfti ASM ASM 0x10'
        store_inst_list2 = 'iAddi ASM ASM ' + hex(int(imm0) & 0xFFFF)
        #hex value?
        if(dst[0:2] == '0x'):
            store_inst_list3 = 'iAddi R1 ZERO ' + hex(int(dst, 16) >> 16)
            store_inst_list4 = 'Lsfti R1 R1 0x10'
            store_inst_list5 = 'iAddi R1 R1 ' + hex(int(dst, 16) & 0xFFFF)
            store_inst_list6 = 'sw ASM R1 0x00'
        else:
            store_inst_list3 = 'iAddi R1 ZERO ' + hex(int(dst) >> 16)
            store_inst_list4 = 'Lsfti R1 R1 0x10'
            store_inst_list5 = 'iAddi R1 R1 ' + hex(int(dst) & 0xFFFF)
            store_inst_list6 = 'sw ASM R1 0x00'

        store_inst_list.append(store_inst_list0)
        store_inst_list.append(store_inst_list1)
        store_inst_list.append(store_inst_list2)
        store_inst_list.append(store_inst_list3)
        store_inst_list.append(store_inst_list4)
        store_inst_list.append(store_inst_list5)
        store_inst_list.append(store_inst_list6)
    else:

        store_inst_list0 = 'iAdd ASM ZERO ' + hex(int(imm0) >> 16)
        store_inst_list1 = 'sw ASM ' + dst + ' 0x00'
        store_inst_list.append(store_inst_list0)
        store_inst_list.append(store_inst_list1)
    return '\n'.join(store_inst_list)

#def makeRetInstList(imm0, funcname):
def makeRetInstList(string, funcname):
    ret = string[2]
    ret_inst_list = []
    #register?
    if(ret[0:1] == 'T' or ret[0:1] == 'S'):
    #if(ret[0:1] == 'T' or ret[0:1] == 'S'):
        ret_inst_list0  = 'iAdd R0 ZERO ' + ret
    else:
        ret_inst_list0  = 'iAddi R0 ZERO ' + hex(int(ret))

    if (funcname == '@main()'):
        ret_inst_list1  = 'j 0x00'
    else:
        ret_inst_list1  = 'return'
    
    ret_inst_list.append(ret_inst_list0)
    ret_inst_list.append(ret_inst_list1)
    return '\n'.join(ret_inst_list)

def makeLoadInstList(string):
    dst = string[0]
    src = string[5][0:-1]
    
    load_inst_list = []
    #pointer?
    #if(string[5][-1:] == '*'):
    #hex value?
    if(src[0:2] == '0x'):
        load_inst_list0 = 'iAddi ASM ZERO ' + hex(int(src, 16) >> 16)
        load_inst_list1 = 'Lsfti ASM ASM 0x10'
        load_inst_list2 = 'iAddi ASM ASM ' + hex(int(src, 16) & 0xFFFF)
        load_inst_list3 = 'lw ' + dst + ' ASM 0x00'
    else:
        load_inst_list0 = 'iAddi ASM ZERO ' + hex(int(src) >> 16)
        load_inst_list1 = 'Lsfti ASM ASM 0x10'
        load_inst_list2 = 'iAddi ASM ASM ' + hex(int(src) & 0xFFFF)
        load_inst_list3 = 'lw ' + dst + ' ASM 0x00'

    load_inst_list.append(load_inst_list0)
    load_inst_list.append(load_inst_list1)
    load_inst_list.append(load_inst_list2)
    load_inst_list.append(load_inst_list3)
    return '\n'.join(load_inst_list)
    

def isAllocaInst(string):
    if (len(string) > 3 and string[2] == 'alloca'):
        return True
    else:
        return False

def isStoreInst(string):
    if (len(string) > 1 and string[0] == 'store'):
        return True
    else:
        return False

def isRetInst(string):
    if (len(string) > 1 and string[0] == 'ret'):
        return True
    else:
        return False

def isLoadInst(string):
    if (len(string) > 3 and string[2] == 'load'):
        return True
    else:
        return False

def isPointerInst(string):
    if (isAllocaInst(string)):
        return True
    else:
        return False

def replaceVariable(const_line, variableTableList):
    listIndex = 0
    tableIndex = 0
    funcName = ''
    replaced_line = []
    bracket_deep = 0 
    for i, line in enumerate(const_line):
        instStr = ''
        string = line.split()
        for j in range(len(string)):
            if (string[j] == 'define'):
                funcName = string[2]
            if(string[j] == '{'):
                bracket_deep+=1
            if(string[j] == '}'):
                bracket_deep-=1

            #if (isFunc):
            ptn_var = re.match('^%.*', string[j])
            if ptn_var:
                varName = ptn_var.group()
                # erase "," from string
                if(varName[-1:]==','):
                    varName = varName[0:-1]
                    #tableIndex = searchVariable(varName, variableTableList[listIndex].table)
                    tableIndex = variableTableList[listIndex].searchVariable(varName)
                    string[j] = variableTableList[listIndex].table[tableIndex][ASSIGNEDREG] + ','
                else:
                    # Variable is detected
                    #tableIndex = searchVariable(varName, variableTableList[listIndex].table)
                    tableIndex = variableTableList[listIndex].searchVariable(varName)
                    string[j] = variableTableList[listIndex].table[tableIndex][ASSIGNEDREG]
            if(bracket_deep == 1 and string[j] == '}'):
                listIndex += 1

            instStr += string[j] + ' '

        instStr += '\n'
        replaced_line.append(instStr)
    return replaced_line

def searchVariable(varName, table):
    for i in range(len(table)):
        if (table[i][VARNAME] == varName):
            return i
    
    print('Error! there is no var: ' + varName)
    return ALREADY_CONTAINED
