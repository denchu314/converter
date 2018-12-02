import sys
import re
from replacer_func import *
#import subprocess


args = sys.argv

OUTPUT_FILENAME = args[1][:-1] + '1'

rfile = open(args[1], 'r')
wfile = open(OUTPUT_FILENAME, 'w')
wfile2 = open('rep.ll', 'w')

diff_from_fp = Stack()

const_line = rfile.readlines()
#print(const_line)
registerTableList = []
variableTableList = []
machine = MachineStatus();
###################
# REPLACER
###################
# all read
bracket_deep = 0
listIndex = 0
for i, line in enumerate(const_line):
     
    string = line.split()
    # new func detected
    if (isFuncInst(string)):
        funcName, varName = readFuncInfo(string)
        registerTableList.append(RegisterTable(funcName))
        variableTableList.append(VariableTable(funcName))
        for k in range(len(varName)):
            variableTableList[listIndex].addRow(varName[k], ATTR_ARG, i, i, '')
    
    for j in range(len(string)):
        #if (string[j] == 'define'):
        if(string[j] == '{'):
            bracket_deep+=1
        if(string[j] == '}'):
            bracket_deep-=1
            if(bracket_deep == 0):
                #function{} finish
                listIndex += 1
                diff_from_fp.next()
        
        ptn_var = re.match('^%[a-zA-Z_0-9]*', string[j]) #variable name
        # Variable is detected
        if ptn_var:
            varName = ptn_var.group()
            
            # special variable?
            # (argumemt?)
            #if(isFuncInst(string)):
                
            # first time? 
            tableIndex = variableTableList[listIndex].searchVariable(varName)

            # already conteined 
            if(tableIndex is not FIRST_TIME):
                variableTableList[listIndex].table[tableIndex][END] = i
            # first time in table
            else:
                if(isPointerInst(string)):
                    print(varName + ' ' + str(diff_from_fp.peek()))
                    variableTableList[listIndex].addRow(varName, ATTR_PTR_STATIC_LOCAL, i, i, 'FP-' + str(diff_from_fp.peek()))
                    diff_from_fp.update(diff_from_fp.peek() + ADDR_PER_WORD)
                else:
                    variableTableList[listIndex].addRow(varName, ATTR_TEMP, i, i, '')

                
# reg is assined to variable
#print(variableTableList[0].funcName)
#print(variableTableList[0].table)
#print(variableTableList[1].funcName)
#print(variableTableList[1].table)
assignRegister(variableTableList, machine, ALG_NONE)
#print(variableTableList[0].funcName)
#print(variableTableList[0].table)
#print(variableTableList[1].funcName)
#print(variableTableList[1].table)
#print(variableTableList[1].funcName)
#print(variableTableList[1].table)
#replace const line var to reg
replaced_line = replaceVariable(const_line, variableTableList)
wfile2.writelines(replaced_line)
# replace insts
# asm header
wfile.write('j @main')
wfile.write('\n')
wfile.write('ori 0x10')
wfile.write('\n')

for i, line in enumerate(replaced_line):
#    print(replace)
    string = line.split()
    # alloca
    if (isAllocaInst(string)):
        wfile.writelines(makeAllocaInstList())
        wfile.write('\n')
    # store
    elif (isStoreInst(string)):
        wfile.writelines(makeStoreInstList(string))
        wfile.write('\n')
    #ret
    elif (isRetInst(string)):
        wfile.writelines(makeRetInstList(string, variableTableList[0].funcName))
        wfile.write('\n')
    #load 
    elif (isLoadInst(string)):
        wfile.writelines(makeLoadInstList(string))
        wfile.write('\n')
    #add
    elif (isAddInst(string)):
        wfile.writelines(makeAddInstList(string))
        wfile.write('\n')
    #call
    elif (isCallInst(string)):
        wfile.writelines(makeCallInstList(string))
        wfile.write('\n')
    #funcDefinition
    elif (isFuncInst(string)):
        wfile.writelines(makeFuncInstList(string))
        wfile.write('\n')
#print(variableTableList[0].table)
#print(variableTableList[0].table[VARNAME])
