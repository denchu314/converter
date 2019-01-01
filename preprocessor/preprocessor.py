import sys

args = sys.argv

OUTPUT_FILENAME = args[1] + '0'

isFunc = False



bracket_deep = 0

if (len(args) < 2):
    print("usage: " + args[0] + " [preprocess_file_path] [-o output]")
    exit()

for i in range(len(args)):
    if (args[i] == "-o"):
        OUTPUT_FILENAME = args[i+1]

rfile = open(args[1], 'r')
wfile = open(OUTPUT_FILENAME, 'w')
line = rfile.readlines()

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


