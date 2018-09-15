import sys
import re
from replacer_func import *
#import subprocess


args = sys.argv

OUTPUT_FILENAME = args[1][:-1] + '1'

rfile = open(args[1], 'r')
wfile = open(OUTPUT_FILENAME, 'w')

const_line = rfile.readlines()
#print(const_line)
registerTableList = []
variableTableList = []
machine = MachineStatus();
###################
# REPLACER
###################
# all read
for i, line in enumerate(const_line):
     
    string = line.split()
    bracket_deep = 0
    listIndex = 0
    for j in range(len(string)):
        if (string[j] == 'define'):
            funcName = string[2]
            registerTableList.append(RegisterTable(funcName))
            variableTableList.append(VariableTable(funcName))
        if(string[j] == '{'):
            bracket_deep+=1
        if(string[j] == '}'):
            bracket_deep-=1
        
        ptn_var = re.match('^%.*', string[j])
        # Variable is detected
        if ptn_var:
            varName = ptn_var.group()
            # erase "," from string
            if(varName[-1:]==','):
                varName = varName[0:-1]
            
            #first time? 
            tableIndex = variableTableList[listIndex].searchVariable(varName)
            
            # already conteined 
            if(tableIndex is not FIRST_TIME):
                variableTableList[listIndex].table[tableIndex][END] = i
            # first time in table
            else:
                if(isPointerInst(string)):
                    variableTableList[listIndex].addRow(varName, ATTR_PTR_STATIC_LOCAL, i, i, '')
                else:
                    variableTableList[listIndex].addRow(varName, ATTR_TEMP, i, i, '')

        if(bracket_deep == 1 and string[j] == '}'):
            listIndex += 1
                
# reg is assined to variable
assignRegister(variableTableList, machine, ALG_NONE)
print(variableTableList[0].table)
#replace const line var to reg
replaced_line = replaceVariable(const_line, variableTableList)
# replace insts
for i, line in enumerate(replaced_line):
#    print(replace)
    string = line.split()
    # alloca
    #if (isAllocaInst(string)):
        #wfile.writelines(makeAllocaInstList(string[0]))
        #wfile.write('\n')
        
    # store
    if (isStoreInst(string)):
        wfile.writelines(makeStoreInstList(string))
        wfile.write('\n')
    #ret
    elif (isRetInst(string)):
        wfile.writelines(makeRetInstList(string, variableTableList[0].funcName))
        wfile.write('\n')
    
    elif (isLoadInst(string)):
        wfile.writelines(makeLoadInstList(string))
        wfile.write('\n')

#print(variableTableList[0].table)
#print(variableTableList[0].table[VARNAME])
