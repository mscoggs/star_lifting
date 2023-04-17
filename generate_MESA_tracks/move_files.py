import os
import subprocess as sp
import re
import sys
import numpy as np


def run_command(com):
	process = sp.Popen(com.split(), stdout=sp.PIPE)
	output, error = process.communicate()
	return output, error







def main(args):
	dir_num = int(args[0])
	dirs = [name for name in os.listdir(".") if (("run"+str(dir_num) in name))]

	for main_dir in dirs:
		subdirs = os.listdir(main_dir)
		for subdir_ in subdirs:
			dir_to = subdir_
			dir_from = main_dir +"/"+subdir_
			
			
			if not os.path.exists("output/"+dir_to): os.makedirs("output/"+dir_to)
			#output, error = run_command("cp "+dir_from+"/output_full.txt output/"+dir_to+"/output_full.txt")
			output, error = run_command("cp "+dir_from+"/output_best.txt output/"+dir_to+"/output_best.txt")
			#output, error = run_command("cp -r "+dir_+"/LOGS/ output/"+dir_+"/LOGS/")

if __name__ == "__main__":
	main(sys.argv[1:])

