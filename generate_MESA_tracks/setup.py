import subprocess as sp
import math
import re
import sys
import numpy as np

masses = np.arange(1.02, 1.205, 0.01)
dt = 0.1
runtimes = 4*np.linspace(1,1,len(masses))#4.0/masses
ISO_LUM_LIST = [True]
Z_SUN = 0.0122
Z_INIT_LIST = [0.1*Z_SUN]
A_START = 2

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
		for ISO_LUM in ISO_LUM_LIST:
			for i in range(len(masses)):

				job_count += 1

				if(not hasattr(dt, "__len__")): d = float(dt)
				else: d = float(dt[i])

				mass = round(masses[i], 3)
				dir_ = run_str+"/M"+str(mass)+"_Isolum_"+str(ISO_LUM)+"_zbase_"+str(Z_BASE)
				
				f2.write("cd "+dir_+"\nsbatch knl.openmp.slurm\ncd ../..\n\n")	
				output, error = run_command("cp -r sl_base_test "+dir_)
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
				replace_value(dir_+"/sl_mesa.py", "ISO_LUM = True", "ISO_LUM = "+str(ISO_LUM))

	f2.close()
	for x in range(sh_num+1):
		output, error = run_command("chmod +x submit_jobs"+str(sh_num)+".sh")



if __name__ == "__main__":
	main(sys.argv[1:])
