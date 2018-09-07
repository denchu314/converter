import sys

args = sys.argv

OUTPUT_FILENAME = args[1] + '0'

isFunc = False

rfile = open(args[1], 'r')
wfile = open(OUTPUT_FILENAME, 'w')

line = rfile.readlines()

bracket_deep = 0

###################
# PRIPROCESS
###################
for i, line in enumerate(line):
    
    string = line.split()
    
    for j in range(len(string)):
        if (string[j] == 'define'):
            isFunc = True
        if(string[j] == '{'):
            bracket_deep+=1
        if(string[j] == '}'):
            bracket_deep-=1

    if(isFunc):
        wfile.write(line)
    
    if(bracket_deep == 0 and isFunc == True):
        isFunc = False
