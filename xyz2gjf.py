#!/usr/bin/python
#python xyz2gjf.py xyzfile.xyz

import sys
import glob


first_task = '''\
%nproc=16
%mem=16GB
#p BMK def2SVP int=ultrafine opt=modred

YYS

0 1
'''
transition_state = True # True or False
second_task = '''\
%nproc=16
%mem=16GB
#p BMK def2SVP int=ultrafine opt(ts,calcfc,nofreeze,noeigen) freq geom=allcheck guess=tcheck
'''
fixed = '''
B 1 30 F
B 1 6 F
B 6 30 F
''' 
executive_job = '''\
#!/bin/sh -f
#BSUB -q normal
#BSUB -o outfile
#BSUB -J {0}
export OMP_NUM_THREADS=16
g09 {1}
'''

if len(sys.argv) != 2:
    raise AssertionError('python xyz2gjf.py xyzfile.xyz')
    
global atoms_num
atoms_num = 0
global line_num
line_num = 0
global file_num
file_num = 0
global temp_file_name
global temp_chk_name

def process(temp_line):
    global atoms_num
    global line_num
    global file_num
    global temp_file_name
    global temp_chk_name
    line_num += 1
    if line_num == 1:
        atoms_num = int(temp_line.strip()) # to get the atom numbers
    if (line_num % (atoms_num + 2)) == 1:
        if atoms_num != int(temp_line):
            raise ValueError("Wrong total number of atoms!!!")
        file_num += 1
        temp_file_name = ''.join([str(sys.argv[1]).split('.')[0], '-', str(file_num).zfill(3), '.gjf']) # to generate files like filename-001.gjf
        temp_chk_name = ''.join([str(sys.argv[1]).split('.')[0], '-', str(file_num).zfill(3), '.chk'])
        temp_gjf = open(temp_file_name, 'w')
        temp_gjf.write("%chk=" + temp_chk_name + '\n') # to write in chk files
        temp_gjf.write(first_task)
        temp_gjf.close()
    elif (line_num % (atoms_num + 2)) == 2: # to pass the second line 
        pass
    else: 
        temp_line_list = temp_line[:].split()
        new_line_list = temp_line_list[0:4]
        new_line='    '.join(new_line_list) # 4 blanks
        temp_gjf = open(temp_file_name, 'a')
        temp_gjf.write(new_line + '\n') # to write in coordinates
        temp_gjf.close()

traj = open(str(sys.argv[1]), 'r')
while True:
    line = traj.readline()
    if not line:
        break
    process(line)
traj.close()

gjf = glob.glob('*.gjf') 
for filename in gjf: # to run with all the gjf files in current directory
    f1 = open(filename, 'a')
    if transition_state: # to check the second task of transition_stat searching
        f1.write(fixed)
        f1.write('\n--link1--\n')
        f1.write("%chk=" + filename.split('.')[0] + '.chk\n')
        f1.write(second_task)
    f1.write('\n\n')
    f1.close()    
    job = filename.split('.')[0] + '.job'
    f2 = open(job, 'w') # to write in the executive job file
    f2.write(executive_job.format(filename, filename))
    f2.close()