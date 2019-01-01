import sys
import re
from replacer_func import *
#import subprocess




args = sys.argv

OUTPUT_FILENAME = args[1][:-1] + '1'


if (len(args) < 2):
    print("usage: " + args[0] + " [replace_file_path] [-o output]")
    exit()

for i in range(len(args)):
    if (args[i] == "-o"):
        OUTPUT_FILENAME = args[i+1]

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
#print(const_line)
for i, line in enumerate(const_line):
     
    string = line.split()
    # new func detected
    if (isFuncInst(string)):
        funcName, varName = readFuncInfo(string)
        registerTableList.append(RegisterTable(funcName))
        variableTableList.append(VariableTable(funcName))
        for k in range(len(varName)):
            variableTableList[listIndex].addRow(varName[k], ATTR_ARG, i, i, '')
    #label preprocess
    if (isBrLongInst(string)):
            string[4] = 'L' + string[4][1:]
            string[6] = 'L' + string[6][1:]
    if (isBrShortInst(string)):
            string[2] = 'L' + string[2][1:]
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
        
        if(re.match(';', string[j])):#comment out
            break
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
                    #print(varName + ' ' + str(diff_from_fp.peek()))
                    variableTableList[listIndex].addRow(varName, ATTR_PTR_STATIC_LOCAL, i, i, 'FP-' + str(diff_from_fp.peek()))
                    diff_from_fp.update(diff_from_fp.peek() + ADDR_PER_WORD)
                else:
                    variableTableList[listIndex].addRow(varName, ATTR_TEMP, i, i, '')
            
# reg is assined to variable
#print(string + ':' + len(string) + ':' + string[-1])
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

#FP = 0x1FFFC
wfile.write('iAddi FP ZERO ' + hex(higher16bit(FP_INIT)))
wfile.write('\n')
wfile.write('Lsfti FP FP 0x10')
wfile.write('\n')
wfile.write('iAddi FP FP ' + hex(lower16bit(FP_INIT)))
wfile.write('\n')

#FP = 0x1FFF8
wfile.write('iAddi SP ZERO ' + hex(higher16bit(SP_INIT)))
wfile.write('\n')
wfile.write('Lsfti SP SP 0x10')
wfile.write('\n')
wfile.write('iAddi SP SP ' + hex(lower16bit(SP_INIT)))
wfile.write('\n')

#GP = 0x18000
wfile.write('iAddi GP ZERO ' + hex(higher16bit(GP_INIT)))
wfile.write('\n')
wfile.write('Lsfti GP GP 0x10')
wfile.write('\n')
wfile.write('iAddi GP GP ' + hex(lower16bit(GP_INIT)))
wfile.write('\n')

#RA = 0x14000
wfile.write('iAddi RA ZERO ' + hex(higher16bit(RA_INIT)))
wfile.write('\n')
wfile.write('Lsfti RA RA 0x10')
wfile.write('\n')
wfile.write('iAddi RA RA ' + hex(lower16bit(RA_INIT)))
wfile.write('\n')


wfile.write('j 0x4000')
wfile.write('\n')
wfile.write('ori 0x4000')
wfile.write('\n')
wfile.write('j @main')
wfile.write('\n')
#wfile.write('ori 0x10')
#wfile.write('\n')
funcName = ''
varName = ''
for i, line in enumerate(replaced_line):
#    print(replace)
    string = line.split()
    #funcDefinition
    if (isFuncInst(string)):
        funcName, varName = readFuncInfo(string)
        print(funcName)
        wfile.writelines(makeFuncInstList(string))
        wfile.write('\n')
    # alloca
    elif (isAllocaInst(string)):
        wfile.writelines(makeAllocaInstList())
        wfile.write('\n')
    # store
    elif (isStoreInst(string)):
        wfile.writelines(makeStoreInstList(string))
        wfile.write('\n')
    #ret
    elif (isRetInst(string)):
        print(funcName)
        wfile.writelines(makeRetInstList(string, funcName))
        wfile.write('\n')
    #load 
    elif (isLoadInst(string)):
        wfile.writelines(makeLoadInstList(string))
        wfile.write('\n')
    #add
    elif (isAddInst(string)):
        wfile.writelines(makeAddInstList(string))
        wfile.write('\n')
    #sub
    elif (isSubInst(string)):
        wfile.writelines(makeSubInstList(string))
        wfile.write('\n')
    #call
    elif (isCallInst(string)):
        wfile.writelines(makeCallInstList(string))
        wfile.write('\n')
    #icmp
    elif (isIcmpInst(string)):
        wfile.writelines(makeIcmpInstList(string))
        wfile.write('\n')
    #br long
    elif (isBrLongInst(string)):
        wfile.writelines(makeBrLongInst(string))
        wfile.write('\n')
    #br short
    elif (isBrShortInst(string)):
        wfile.writelines(makeBrShortInst(string))
        wfile.write('\n')
    #replaced label
    elif (isReplacedLabel(string)):
        wfile.writelines(string)
        wfile.write('\n')
    
    
#print(variableTableList[0].table)
#print(variableTableList[0].table[VARNAME])
