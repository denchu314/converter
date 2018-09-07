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
            
            tableIndex = variableTableList[listIndex].searchVariable(varName)
            
            # Var has not been contained in table
            if(tableIndex != -1):
                variableTableList[listIndex].table[tableIndex][END] = i
            # Var has already been contained in table
            else:
                variableTableList[listIndex].addRow(varName, ATTR_TEMP, i, i, '')

        if(bracket_deep == 1 and string[j] == '}'):
            listIndex += 1
                
# reg is assined to variable
assignRegister(variableTableList, ALG_NONE)
#print(variableTableList[0].table)
#replace const line var to reg
replaced_line = replaceVariable(const_line, variableTableList)
#print(replaced_line)
#print(replaced_line[0])
# replace insts
for i, line in enumerate(replaced_line):
#    print(replace)
    string = line.split()
    # alloca
    if (isAllocaInst(string)):
        wfile.writelines(makeAllocaInstList(string[0]))
        wfile.write('\n')
    # store
    elif (isStoreInst(string)):
        wfile.writelines(makeStoreInstList(string[2][0:-1], string[4][0:-1]))
        wfile.write('\n')
    #ret
    elif (isRetInst(string)):
        wfile.writelines(makeRetInstList(string[2], variableTableList[0].funcName))
        wfile.write('\n')

#print(variableTableList[0].table)
#print(variableTableList[0].table[VARNAME])
