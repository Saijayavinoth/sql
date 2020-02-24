from subprocess import *

ans_file = open("ans.txt", 'w')
ans_json = []
import json
ans_csv=open("ans.csv","w")
ans_csv.write('python,eng_text,query\n')
with open("run.txt") as f:
    commands = f.readlines()
    for command in commands:
        commands = command.split('-i')
        print(commands)
        command = commands[0].split() + ['-i'] + [commands[1]]
        print("command", command, "**************")
        p = Popen(command, stdin=PIPE, stderr=PIPE, stdout=PIPE)
        output, error = p.communicate(input="")
        ans = str(output.decode('utf-8')) + str(open("output.json").read())
        print(command)
        print(ans)
        ans_file.write(' '.join(command) + '\n')
        ans_file.write(ans + '\n')
        ans_file.write("***************\n")
        print("******************")
        out_csv=[' '.join(command).replace('\n',''),commands[1].replace('\n',''),str(output,'utf-8').replace('\n','')]
        ans_csv.write(','.join(out_csv))
        ans_csv.write('\n')
