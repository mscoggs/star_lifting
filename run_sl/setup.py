import subprocess as sp
import math
import re
import sys
import numpy as np

#masses = np.arange(0.2, 1.4, 0.05)
masses = np.arange(0.1, 0.21, 0.01)
dt = 0.01/masses
runtimes = 2.0*np.linspace(1,1,len(masses))


METHOD_VALS    =  [0,1,2] #0, isolum, 1 isoirr, 2 maxlift

Z_SUN = 0.0122
Z_INIT_LIST = [0.01*Z_SUN]
Z_INIT_LIST = [Z_SUN, 0.1*Z_SUN, 0.01*Z_SUN]
A_START = 2
MAX_AGE = 14 # -1 means let the stars max age be determined by the time of leaving MS, otherwise hardset in GYr

if(hasattr(dt, "__len__")  and (len(dt) != len(masses))): 
	print("DT NOT SAME SIZE AS MASS")
	exit(0)



def replace_value(fname, var_name, new_var):
	f = open(fname, "r+")
	text = f.read()
	text = re.sub(var_name, new_var, text)
	f.seek(0)
	f.write(text)
	f.truncate()

def run_command(com):
	process = sp.Popen(com.split(), stdout=sp.PIPE)
	output, error = process.communicate()
	return output, error

def main(argv):
	num = int(argv[0])
	f2 = open("submit_jobs0.sh", "w")
	f2.write("#!/bin/bash\n\n")
	run_str = "run"+str(num)
	output, error = run_command("mkdir "+run_str)
	job_count,sh_num = 0,0
	for Z_BASE in Z_INIT_LIST:
		for x in range(len(METHOD_VALS)):
			for i in range(len(masses)):

				job_count += 1

				if(not hasattr(dt, "__len__")): d = float(dt)
				else: d = float(dt[i])

				mass = round(masses[i], 3)
				dir_ = run_str+"/M"+str(mass)+"_method_"+str(METHOD_VALS[x])+"_zbase_"+str(Z_BASE)
				
				f2.write("cd "+dir_+"\nsbatch knl.openmp.slurm\ncd ../..\n\n")	
				output, error = run_command("cp -r sl_base "+dir_)
				#dm = 1
				for inlist_name in ["inlist_project_start", "inlist_project_base", "inlist_project_full"]:
					replace_value(dir_+"/"+inlist_name, "initial_mass = 1", "initial_mass ="+str(mass))
					replace_value(dir_+"/"+inlist_name, "initial_z = 0.0122", "initial_z ="+str(Z_BASE))
					#replace_value(dir_+"/"+inlist_name, "mass_change = -1d-11", "mass_change = -"+str(dm)+"d-11")
					replace_value(dir_+"/"+inlist_name, "Zbase = 0.02", "Zbase = "+str(Z_BASE))
					if("full" not in inlist_name): replace_value(dir_+"/"+inlist_name, "max_age = 2.0d9", "max_age = "+str(A_START)+"d9")
				


				replace_value(dir_+"/knl.openmp.slurm", "-t 10", "-t "+str(int(math.ceil(runtimes[i]))))
				replace_value(dir_+"/sl_mesa.py", "DT = 0.5", "DT = "+str(d))
				replace_value(dir_+"/sl_mesa.py", "INITIAL_MASS = 1.0", "INITIAL_MASS = "+str(mass))
				replace_value(dir_+"/sl_mesa.py", "METHOD = -1", "METHOD = "+str(METHOD_VALS[x]))
				replace_value(dir_+"/sl_mesa.py", "MAX_AGE = -1", "MAX_AGE = "+str(MAX_AGE))




	f2.close()
	for x in range(sh_num+1):
		output, error = run_command("chmod +x submit_jobs"+str(sh_num)+".sh")



if __name__ == "__main__":
	main(sys.argv[1:])
