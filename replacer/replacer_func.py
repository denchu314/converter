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

ALG_NONE = 0

ADDR_PER_WORD = '0x04'

#class FuncTable:
#    def __init__(self, funcName):
#    self.funcName = funcName
#    self.start = 0
#    self.end = 0

class RegisterTable:
    def __init__(self, name):
        self.funcName = name
        self.S = [True, True, True, True, True, True, True, True, True]
        self.T = [True, True, True, True, True, True, True, True, True]

    def getRegister(self, regName):
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
        return None

    def searchForSaveVariable(self):
        for i in range(len(self.S)):
            if (self.S[i] == True):
                return 'S' + str(i)
        return None

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
        
        return -1
#class RegisterAssignmentTableList:
#    def __init__(self):
#        self = []
#    def add(self, funcName):
#        self.append(RegisterAssignmentTable(funcName))

    #def searchVal
def assignRegister(variableTableList, ALGORITHM):

    for i in range(len(variableTableList)):
        funcName = variableTableList[i].funcName
        registerTable = RegisterTable(funcName)
        
        for j in range(len(variableTableList[i].table)):
            if(variableTableList[i].table[j][ATTR] == ATTR_SAVE):
                assignedreg = registerTable.searchForSaveVariable()
                if(assignedreg is None):
                    variableTableList[i].table[j][ASSIGNEDREG] = 'ME'
                else:
                    variableTableList[i].table[j][ASSIGNEDREG] = assignedreg

            elif(variableTableList[i].table[j][ATTR] == ATTR_TEMP):
                assignedreg = registerTable.searchForTempVariable()
                if(assignedreg is None):
                    variableTableList[i].table[j][ASSIGNEDREG] = 'ME'
                else:
                    variableTableList[i].table[j][ASSIGNEDREG] = assignedreg


def makeAllocaInstList(assignedreg0):
    alloca_inst_list0 = 'lw ' + assignedreg0 + ' FP 0x00'
    alloca_inst_list1 = 'iAddi ' + assignedreg0 + ' ' + assignedreg0 + ' ' + ADDR_PER_WORD
    alloca_inst_list2 = 'sw ' + assignedreg0 + ' FP 0x00'
    alloca_inst_list3 = 'iSubi SP SP ' + ADDR_PER_WORD
    alloca_inst_list4 = 'iAdd ' + assignedreg0 + ' SP ZERO'
    alloca_inst_list = []
    alloca_inst_list.append(alloca_inst_list0)
    alloca_inst_list.append(alloca_inst_list1)
    alloca_inst_list.append(alloca_inst_list2)
    alloca_inst_list.append(alloca_inst_list3)
    alloca_inst_list.append(alloca_inst_list4)
    return '\n'.join(alloca_inst_list)

def makeStoreInstList(imm0, assignedreg0):
    store_inst_list0 = 'iAddi ASM ZERO ' + hex(int(imm0))
    store_inst_list1 = 'sw ASM ' + assignedreg0 + ' 0x00'
    store_inst_list = []
    store_inst_list.append(store_inst_list0)
    store_inst_list.append(store_inst_list1)
    return '\n'.join(store_inst_list)

def makeRetInstList(imm0, funcname):
    if (funcname == '@main()'):
        ret_inst_list0  = 'iAddi R0 ZERO ' + hex(int(imm0))
        ret_inst_list1  = 'j 0x00'
        ret_inst_list = []
        ret_inst_list.append(ret_inst_list0)
        ret_inst_list.append(ret_inst_list1)
    else:
        ret_inst_list0  = 'iAddi R0 ZERO ' + hex(int(imm0))
        ret_inst_list1  = 'return'
        ret_inst_list = []
        ret_inst_list.append(ret_inst_list0)
        ret_inst_list.append(ret_inst_list1)
    return '\n'.join(ret_inst_list)

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
    return None
