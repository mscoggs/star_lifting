import sys
import shutil
from decimal import Decimal
import re
import numpy as np
from scipy.interpolate import *

ITERATIONS = 6
A_START = 2
DT = 0.5
INITIAL_MASS = 1.0
ISO_LUM = True
ISO_IRR = not ISO_LUM


def replace_line(filename, line_id, newline):

	f = open(filename, "r+")
	text = f.readlines()
	for i in range(len(text)):
		if(line_id in text[i]): text[i] = newline+"\n"
	f.seek(0)
	f.writelines(text)
	f.truncate()
	f.close()



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

def update_base(t):

	replace_line("inlist_project_base", "max_age", "    max_age = "+str(A_START + (t)*DT)+"d9")
	replace_line("inlist_project_base", "load_model_filename", "  load_model_filename = 'step_"+str(t-1)+".mod'")
	replace_line("inlist_project_base", "save_model_filename", "  save_model_filename = 'step_"+str(t)+".mod'")


def get_text(filename):
	f = open(filename, "r+")
	text = f.read()
	f.close()
	return text

def get_lines(filename):
	f = open(filename, "r+")
	lines = f.readlines()
	f.close()
	return lines

def calc_dmdt(t, arg):

	text = get_text("inlist_project_base")
	shutil.copyfile("inlist_project_base", "inlist_project")
	dmdt_best_string = ""

	if(t >= 2): 
		text2 = get_lines("inlist_project_step")
		
		for i in range(len(text2)):
			if("mass_change" in text2[i]):
				mass_loss_str = text2[i].split("=")[-1]
				s_base = float(mass_loss_str.split("d-")[0])
				p = int(mass_loss_str.split("d-")[-1])

		if(arg == 1): 
			s = s_base

		elif(arg == 2):
			m_i, age_i, log_l_recent = get_vals_from_output("output1.txt")
			m_start, age_start, log_l_i = get_vals_from_output("output_start.txt")
			m_last, age_last, log_l_last = get_vals_from_output("output_best.txt")
			if(ISO_IRR):
				log_l_i = np.log10((10.0**log_l_i) * m_start**2.0)
				log_l_recent = np.log10((10.0**log_l_recent) * m_i **2.0)

			if(log_l_recent >= log_l_i): s = s_base*5
			else: s = s_base/5

		else:
			m_i_list, age_i_list, log_l_list = [],[],[]
			for x in range(1,arg):
				m_i, age_i, log_l_recent = get_vals_from_output("output"+str(x)+".txt")
				m_i_list.append(m_i), age_i_list.append(age_i), log_l_list.append(log_l_recent)
			m_start, age_start, log_l_i = get_vals_from_output("output_start.txt")
			m_last, age_last, log_l_last = get_vals_from_output("output_best.txt")
			dmdt = np.abs((np.array(m_i_list)-m_last)/(age_last-np.array(age_i_list)))
			if(ISO_IRR):
				log_l_i = np.log10((10.0**log_l_i) * m_start**2.0)
				log_l_list = np.log10(np.power(10.0,log_l_list) * np.power(m_i_list ,2.0))
			if(min(log_l_list) > log_l_i): s = s_base * 5
			elif(max(log_l_list) < log_l_i): s = s_base / 5
			else: 
				dmdt_best = -1*interp1d(np.power(10.0,log_l_list),dmdt, kind="linear")(10.0**log_l_i)
				dmdt_best_string = ("{:.2E}".format(Decimal(str(dmdt_best)))).replace("E", "d")
				replace_line("inlist_project", "mass_change","  mass_change = "+dmdt_best_string)

	else:
		a=1
		if(INITIAL_MASS >= 1): a=10
		s = -5*INITIAL_MASS*a
		p = int(10+(arg))
	
	if(dmdt_best_string == ""): replace_value("inlist_project", "-1d-11", str(s)+"d-"+str(p))



def check_stops():
	stop_strs = ["stop because have dropped below central lower limit for h1", "stop because star_mass <= star_mass_min_limit"]
	for stop_str in stop_strs:
		for line in open("output_best.txt").readlines():
			if(stop_str in line): 
				return False
	return True

def get_vals_from_output(filename):
	f = open(filename)
	lines = f.readlines()[-6:-3]
	f.close()
	mass = float((lines[-3].split())[5])
	age   = float((lines[-1].split())[0])
	log_l = float((lines[-1].split())[2])
	return mass,age,log_l

def read_output_trial_data():
	log_l_list, final_mass, final_t = [],[],[]
	for i in range(1,ITERATIONS):
		mass,age,log_l = get_vals_from_output("output"+str(i)+".txt")
		final_mass.append(mass),final_t.append(age), log_l_list.append(log_l)
	return log_l_list, final_mass, final_t

def best_run(t, arg):
	log_l_list, final_mass, final_t = read_output_trial_data()

	m_i, age_i, log_l_recenet = get_vals_from_output("output_best.txt")
	m_start, age_start, log_l_i = get_vals_from_output("output_start.txt")

	dmdt = np.abs((m_i - np.array(final_mass))/(np.array(final_t) - age_i))

	if(ISO_IRR):
		log_l_i = np.log10((10.0**log_l_i) * m_start**2.0)
		log_l_list = np.log10(np.power(10.0, np.array(log_l_list))*np.power(np.array(final_mass),2.0))
	f = open("lum.txt", "a")
	errorstr = str(t) + "    " + str(log_l_i)
	for l in log_l_list: errorstr += "   " + str(l)
	for d in dmdt: errorstr += "   " + str(d)
	errorstr += "\n"
	f.write(errorstr)
	f.close()
	if((log_l_i < max(log_l_list)) and (log_l_i > min(log_l_list))):
		dmdt_best = -1*interp1d(np.power(10.0,log_l_list),dmdt, kind="linear")(10.0**log_l_i)
	else:
		dmdt_best = -1*np.polyval(np.polyfit(np.power(10.0, log_l_list), dmdt, 3), 10.0**log_l_i)
	dmdt_best_string = ("{:.2E}".format(Decimal(str(dmdt_best)))).replace("E", "d")
	replace_line("inlist_project", "mass_change","  mass_change = "+dmdt_best_string)
	shutil.copyfile("inlist_project", "inlist_project_step")



def main(argv):
	arg = int(argv[0])
	t = int(argv[1])

	if(arg == 0): shutil.copyfile("inlist_project_start", "inlist_project")
	elif(0  < arg < ITERATIONS):
		if(arg == 1): update_base(t)
		calc_dmdt(t, arg)
		#try:calc_dmdt(t, arg)
		#except Exception as e: 
		#	print(e)
		#	return False
		shutil.copyfile("inlist_project", "inlist_copies/inlist_project_t_"+str(t)+"_i_"+str(arg))
		
	else:
		if not check_stops(): return False

		best_run(t,arg)


		
	return True
		

if __name__ == "__main__":
	dont_exit = main(sys.argv[1:])
	print(dont_exit)
