import sys
import re
from replacer_func import *
#import subprocess


args = sys.argv

OUTPUT_FILENAME = args[1] + '1'

rfile = open(args[1], 'r')
wfile = open(OUTPUT_FILENAME, 'w')

const_line = rfile.readlines()
print(const_line)
registerTableList = []
variableTableList = []
thisfuncname = ''

###################
# REPLACER
###################
# all read
for i, line in enumerate(const_line):
     
    string = line.split()

    for j in range(len(string)):
        ptn_func = re.match('^@.*(\(\))$', string[j])
        # Function is detected
        if ptn_func:
            thisfuncname = ptn_func.group()
            registerTableList.append(RegisterTable(thisfuncname))
            variableTableList.append(VariableTable(thisfuncname))
#            funcTableList.append(FuncTable(thisfuncname))
 #           funcTableList[len(funcTableList)].start = i
        
        ptn_var = re.match('^%.*', string[j])
        # Variable is detected
        if ptn_var:
            varName = ptn_var.group()
            # erase "," from string
            if(varName[-1:]==','):
                varName = varName[0:-1]
            # Var is first time
            if(variableTableList[0].hasContainedVarName(varName)==False):
                variableTableList[0].addRow(varName, ATTR_TEMP, i, i, '')
                
# reg is assined to variable
assignRegister(variableTableList[0], ALG_NONE)
#print(variableTableList[0].table)
#replace const line var to reg
replaced_line = replaceVariable(const_line, variableTableList)
print(replaced_line)
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
