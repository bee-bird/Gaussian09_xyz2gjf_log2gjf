#!/usr/bin/python
#python log2gjf.py

import glob


file_extension = '-BMK'
first_task = '''\
%nproc=16
%mem=16GB
#p BMK def2SVP int=ultrafine opt=modred

YYS

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

elements = {1: 'H', 2: 'He', 3: 'Li', 4: 'Be', 5: 'B', 6: 'C', 7: 'N', 8: 'O', 9: 'F', 10: 'Ne', 11: 'Na', 12: 'Mg', 13: 'Al', 14: 'Si', 15: 'P', 16: 'S', 17: 'Cl', 18: 'Ar', 19: 'K', 20: 'Ca', 21: 'Sc', 22: 'Ti', 23: 'V', 24: 'Cr', 25: 'Mn', 26: 'Fe', 27: 'Co', 28: 'Ni', 29: 'Cu', 30: 'Zn', 33: 'As', 35: 'Br', 44: 'Ru', 45: 'Rh', 46: 'Pd', 47: 'Ag', 49: 'In', 53: 'I', 55: 'Cs', 74: 'W', 75: 'Re', 77: 'Ir', 78: 'Pt', 79: 'Au', 82: 'Pb'}

def log2gjf(filename):
    open_old = open(filename, 'r')
    rline = open_old.readlines()
    for i in range(len(rline)):
        if 'Input orientation:' in rline[i]: # to deal with nosymm keywords
            start = i
        elif 'Standard orientation:' in rline[i]: # to find the last set of coordinates
            start = i
    for m in range(start + 5, len(rline)): # to extract the final coordinates
        if '---' in rline[m]:
            end = m
            break
    for j in range(len(rline)): # to extract charge and spin
        if 'Charge' in rline[j]:
            charge_spin = rline[j]            
            charge = charge_spin.split()[2]            
            spin = charge_spin.split()[5]
            break   
    xyz = []    
    for line in rline[start + 5 : end]:  
        element = elements[int(line.split()[1])] # to replace numbers to elements
        xyz.append(element + line[30:-1] + '\n') # to write in elements
    open_old.close()

    inp = filename.split('.')[0] + file_extension + '.gjf'
    f1 = open(inp, 'w')
    f1.write('%chk=' + filename.split('.')[0] + file_extension + '.chk\n')
    f1.write(first_task)
    f1.write(str(charge) + ' ' + str(spin) + '\n')
    f1.writelines(xyz)
    if transition_state: # to check the second task of transition_stat searching
        f1.write(fixed)
        f1.write('\n--link1--\n')
        f1.write('%chk=' + filename.split('.')[0] + file_extension + '.chk\n')
        f1.write(second_task)
    f1.write('\n\n')
    f1.close()
    job = filename.split('.')[0] + file_extension + '.job'
    f2 = open(job, 'w') # to write in the executive job file
    f2.write(executive_job.format(inp, inp))

log = glob.glob('*.log') 
for filename in log: # to run with all the log files in current directory
    log2gjf(filename)