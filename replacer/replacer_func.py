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

registers = ['ZERO', 'K0', 'K1', 'R0', 'R1', 'A0', 'A1', 'A2', 'A3', 'S0', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'T0', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'ASM', 'GP', 'SP', 'FP', 'RA']
saveRegisters = registers[0x09:0x11]
tempRegisters = registers[0x12:0x1a]

#class FuncTable:
#    def __init__(self, funcName):
#    self.funcName = funcName
#    self.start = 0
#    self.end = 0



class Stack:
    def __init__(self):
        self.ptr = 0
        self.items = []
        self.items.append(0)
    def empty(self):
        return self.items == []
                                        
    def update(self, val):
        self.items[self.ptr] = val

    def peek(self):
        #print(self.ptr)
        return self.items[self.ptr]
                              
    def size(self):
        return len(self.items)
    
    def next(self):
        self.ptr = self.ptr + 1
        self.items.append(0)
    
    def before(self):
        self.items[self.ptr] = 0
        self.ptr = self.ptr - 1

class MachineStatus:
    def __init__(self):
        self.sp = INIT_SP_ADDR
        self.sp = INIT_SP_ADDR

class RegisterTable:
    def __init__(self, name):
        self.funcName = name
        self.A = [True, True, True, True]
        self.S = [True, True, True, True, True, True, True, True, True]
        self.T = [True, True, True, True, True, True, True, True, True]

    def setRegisterOccupy(self, regName):
        if regName == 'ME':
            return True
        
        ptn = re.match('A[0-3]|[TS][0-8]', regName)
        if ptn is None:
            print('Reg ' + regName + ' is not implemented.')
            return False
        else:
            if (regName[0] == 'S'):
                self.S[int(regName[1])] = False
            if (regName[0] == 'T'):
                self.T[int(regName[1])] = False
            if (regName[0] == 'A'):
                self.A[int(regName[1])] = False
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
    
    def searchForArgVariable(self):
        for i in range(len(self.A)):
            if (self.A[i] == True):
                return 'A' + str(i)
        print('Error! Argment need more than 4! Not impremented.')
        exit(1)

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
        
        elif(varTable.table[i][ATTR] == ATTR_ARG):
            regName = regTable.searchForArgVariable()
            varTable.table[i][ASSIGNEDREG] = regName
            regTable.setRegisterOccupy(regName)

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

def makeStoreInstList(string):
    src0 = string[2][0:-1]
    dst = string[4][0:-1]
    
    store_inst_list = []
    
    if(isRegisterName(src0) == True):
        store_inst_list = makeStoreListValRegAddrImm(src0, dst)
    else:
        store_inst_list = makeStoreListValImmAddrImm(src0, dst)
    return  store_inst_list

def makeStoreListValImmAddrImm(valImm, addrImm):
    store_inst_list = []
    store_inst_list0 = 'iAddi ASM ZERO ' + hex(int(valImm) >> 16)
    store_inst_list1 = 'Lsfti ASM ASM 0x10'
    store_inst_list2 = 'iAddi ASM ASM ' + hex(int(valImm) & 0xFFFF)
    if(isFPDiff(addrImm)):
        diffaddr = int(addrImm[3:])
        store_inst_list3 = 'iAddi R1 ZERO ' + hex(diffaddr >> 16)
        store_inst_list4 = 'Lsfti R1 R1 0x10'
        store_inst_list5 = 'iAddi R1 R1 ' + hex(diffaddr & 0xFFFF)
    elif(isHex(addrImm)):
        store_inst_list3 = 'iAddi R1 ZERO ' + hex(int(addrImm, 16) >> 16)
        store_inst_list4 = 'Lsfti R1 R1 0x10'
        store_inst_list5 = 'iAddi R1 R1 ' + hex(int(addrImm, 16) & 0xFFFF)
    else:
        store_inst_list3 = 'iAddi R1 ZERO ' + hex(int(addrImm) >> 16)
        store_inst_list4 = 'Lsfti R1 R1 0x10'
        store_inst_list5 = 'iAddi R1 R1 ' + hex(int(addrImm) & 0xFFFF)
    
    store_inst_list6 = 'iSub R1 FP R1'
    store_inst_list7 = 'sw ASM R1 0x00'

    store_inst_list.append(store_inst_list0)
    store_inst_list.append(store_inst_list1)
    store_inst_list.append(store_inst_list2)
    store_inst_list.append(store_inst_list3)
    store_inst_list.append(store_inst_list4)
    store_inst_list.append(store_inst_list5)
    store_inst_list.append(store_inst_list6)
    store_inst_list.append(store_inst_list7)
    return '\n'.join(store_inst_list)
    
def makeStoreListValRegAddrImm(valReg, addrImm):
    store_inst_list = []
    if(isFPDiff(addrImm)):
        diffaddr = int(addrImm[3:])
        store_inst_list0 = 'iAddi R1 ZERO ' + hex(diffaddr >> 16)
        store_inst_list1 = 'Lsfti R1 R1 0x10'
        store_inst_list2 = 'iAddi R1 R1 ' + hex(diffaddr & 0xFFFF)
        store_inst_list3 = 'iSub R1 FP R1'
    elif(isHex(addrImm)):
        store_inst_list0 = 'iAddi R1 ZERO ' + hex(int(addrImm, 16) >> 16)
        store_inst_list1 = 'Lsfti R1 R1 0x10'
        store_inst_list2 = 'iAddi R1 R1 ' + hex(int(addrImm, 16) & 0xFFFF)
    else:
        store_inst_list0 = 'iAddi R1 ZERO ' + hex(int(addrImm) >> 16)
        store_inst_list1 = 'Lsfti R1 R1 0x10'
        store_inst_list2 = 'iAddi R1 R1 ' + hex(int(addrImm) & 0xFFFF)
    store_inst_list4 = 'sw ' + valReg + ' R1 0x00'
    
    store_inst_list.append(store_inst_list0)
    store_inst_list.append(store_inst_list1)
    store_inst_list.append(store_inst_list2)
    if(isFPDiff(addrImm)):
        store_inst_list.append(store_inst_list3)
    store_inst_list.append(store_inst_list4)
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
    if(isFPDiff(src)):
        diffaddr = int(src[3:])
        load_inst_list0 = 'iAddi ASM ZERO ' + hex(diffaddr >> 16)
        load_inst_list1 = 'Lsfti ASM ASM 0x10'
        load_inst_list2 = 'iAddi ASM ASM ' + hex(diffaddr & 0xFFFF)
        load_inst_list3 = 'iSub ASM FP ASM'
    elif(src[0:2] == '0x'):
        load_inst_list0 = 'iAddi ASM ZERO ' + hex(int(src, 16) >> 16)
        load_inst_list1 = 'Lsfti ASM ASM 0x10'
        load_inst_list2 = 'iAddi ASM ASM ' + hex(int(src, 16) & 0xFFFF)
    else:
        load_inst_list0 = 'iAddi ASM ZERO ' + hex(int(src) >> 16)
        load_inst_list1 = 'Lsfti ASM ASM 0x10'
        load_inst_list2 = 'iAddi ASM ASM ' + hex(int(src) & 0xFFFF)
    load_inst_list4 = 'lw ' + dst + ' ASM 0x00'

    load_inst_list.append(load_inst_list0)
    load_inst_list.append(load_inst_list1)
    load_inst_list.append(load_inst_list2)
    if(isFPDiff(src)):
        load_inst_list.append(load_inst_list3)
    load_inst_list.append(load_inst_list4)
    return '\n'.join(load_inst_list)
    
def makeAddInstList(string):
    dst = string[0]
    nuw_flag = False
    nsw_flag = False
    operand = []
    add_inst_list = []
    for i in range(3, len(string)):
        #print(i)
        if(string[i] == 'nuw'):
            nuw_flag = True
        elif(string[i] == 'nsw'):
            nsw_flag = True
        elif(string[i] == 'i32'):
            continue
            #operand.append(string[i+1][:-1])
        else:
            if(string[i][-1:]==','):
                operand.append(string[i][:-1])
            else:
                operand.append(string[i])
    if(isHex(operand[0])):
        src0 = operand[1]
        src1 = operand[0]
        add_inst_list0 = 'iAddi ASM ZERO ' + hex(int(src1, 16) >> 16)
        add_inst_list1 = 'Lsfti ASM ASM 0x10'
        add_inst_list2 = 'iAddi ASM ASM ' + hex(int(src1, 16) & 0xFFFF)
        add_inst_list3 = 'iAdd ' + dst + ' ' + src0 + ' ASM' 
        add_inst_list.append(add_inst_list0)
        add_inst_list.append(add_inst_list1)
        add_inst_list.append(add_inst_list2)
        add_inst_list.append(add_inst_list3)
    elif(isDec(operand[0])):
        src0 = operand[1]
        src1 = hex(int(operand[0]))
        add_inst_list0 = 'iAddi ASM ZERO ' + hex(int(src1, 16) >> 16)
        add_inst_list1 = 'Lsfti ASM ASM 0x10'
        add_inst_list2 = 'iAddi ASM ASM ' + hex(int(src1, 16) & 0xFFFF)
        add_inst_list3 = 'iAdd ' + dst + ' ' + src0 + ' ASM' 
        add_inst_list.append(add_inst_list0)
        add_inst_list.append(add_inst_list1)
        add_inst_list.append(add_inst_list2)
        add_inst_list.append(add_inst_list3)
    elif(isHex(operand[1])):
        src0 = operand[0]
        src1 = operand[1]
        add_inst_list0 = 'iAddi ASM ZERO ' + hex(int(src1, 16) >> 16)
        add_inst_list1 = 'Lsfti ASM ASM 0x10'
        add_inst_list2 = 'iAddi ASM ASM ' + hex(int(src1, 16) & 0xFFFF)
        add_inst_list3 = 'iAdd ' + dst + ' ' + src0 + ' ASM' 
        add_inst_list.append(add_inst_list0)
        add_inst_list.append(add_inst_list1)
        add_inst_list.append(add_inst_list2)
        add_inst_list.append(add_inst_list3)
    elif(isDec(operand[1])):
        src0 = operand[0]
        src1 = hex(int(operand[1]))
        add_inst_list0 = 'iAddi ASM ZERO ' + hex(int(src1, 16) >> 16)
        add_inst_list1 = 'Lsfti ASM ASM 0x10'
        add_inst_list2 = 'iAddi ASM ASM ' + hex(int(src1, 16) & 0xFFFF)
        add_inst_list3 = 'iAdd ' + dst + ' ' + src0 + ' ASM' 
        add_inst_list.append(add_inst_list0)
        add_inst_list.append(add_inst_list1)
        add_inst_list.append(add_inst_list2)
        add_inst_list.append(add_inst_list3)
    else:
        src0 = operand[0]
        src1 = operand[1]
        add_inst_list0 = 'iAdd ' + dst + ' ' + src0 + ' ' + src1
        add_inst_list.append(add_inst_list0)
    
    #print(add_inst_list)
    return '\n'.join(add_inst_list)

def makeCallInstList(string):
    ret, funcName, arg = readCallInfo(string)
    call_inst_list = []
    if( len(arg) == 0 ):
        call_inst_list0 = 'call ' + funcName + ' ZERO ZERO ZERO ZERO'
    elif( len(arg) == 1 ):
        call_inst_list0 = 'call ' + funcName + ' ' + arg[0] + ' ZERO ZERO ZERO'
    elif( len(arg) == 2 ):
        call_inst_list0 = 'call ' + funcName + ' ' + arg[0] + ' ' + arg[1] + ' ZERO ZERO'
    elif( len(arg) == 3 ):
        call_inst_list0 = 'call ' + funcName + ' ' + arg[0] + ' ' + arg[1] + ' ' + arg[2] + ' ZERO'
    elif( len(arg) == 4 ):
        call_inst_list0 = 'call ' + funcName + ' ' + arg[0] + ' ' + arg[1] + ' ' + arg[2] + ' ' + arg[3]
    else:
        print('Error! call args must be less than 4 for now! Not implemented.')
        exit(1)
    
    call_inst_list1 = 'iAdd ' + ret + ' ZERO R0'
    call_inst_list.append(call_inst_list0)
    call_inst_list.append(call_inst_list1)
    #print(arg)
    return '\n'.join(call_inst_list)

def makeFuncInstList(string):
    #funcName = re.match('@[a-zA-Z_0-9]*', string[2]).group()
    arg = []
    funcName, arg = readFuncInfo(string)
    func_inst_list = []
    if(funcName == '@main'):
        func_inst_list.append(funcName + ':')
    else:
        func_inst_list.append(funcName + ':')
        func_inst_list.append('arrival')
    return '\n'.join(func_inst_list)

def isImm(string):
    if(isHex(string) or isDec(string)):
        return True
    else:
        return False

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

def isAddInst(string):
    if (len(string) > 3 and string[2] == 'add'):
        return True
    else:
        return False

def isPointerInst(string):
    if (isAllocaInst(string)):
        return True
    else:
        return False

def isCallInst(string):
    if (len(string) > 3 and string[2] == 'call'):
        return True
    else:
        return False

def isFuncInst(string):
    if (len(string) > 3 and string[0] == 'define' and string[2][0] == '@'):
        return True
    else:
        return False

def readCallInfo(string):
    funcName = re.match('@[a-zA-Z_0-9]*', string[4]).group()
    arg = []
    for i in range(5, len(string), 2):
        arg.append(re.match('[a-zA-Z_0-9]*', string[i]).group())
    retval = string[0]
    return retval, funcName, arg

def readFuncInfo(string):
    funcName = re.match('@[a-zA-Z_0-9]*', string[2]).group()
    arg = []
    for i in range(3, len(string), 2):
        #if(re.match('i32', string[i])):
        ptr_arg = re.match('[a-zA-Z_0-9%]+', string[i])
        if ptr_arg:
            arg.append(ptr_arg.group())
    return funcName, arg


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
                funcName = re.match('@[a-zA-Z_0-9]*', string[2])
            if(string[j] == '{'):
                bracket_deep+=1
            if(string[j] == '}'):
                bracket_deep-=1
                if(bracket_deep == 0):
                    listIndex += 1

            #if var:
            ptn_var = re.match('^%[a-zA-Z_0-9]*', string[j])
            if ptn_var:
                varName = ptn_var.group()
                # erase "," from string
                tableIndex = variableTableList[listIndex].searchVariable(varName)
                string[j] = string[j].replace(varName, variableTableList[listIndex].table[tableIndex][ASSIGNEDREG])

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

def isHex(val):
    try:
        int(val, 16)
        return True
    except:
        return False

def isDec(val):
    try:
        int(val)
        return True
    except:
        return False

def isFPDiff(val):
    if(val[0:2] == 'FP'):
        return True
    else:
        return False

def isRegisterName(string):
    #print(string)
    for i in range(len(registers)):
        if(registers[i] == string):
            return True

    return False

