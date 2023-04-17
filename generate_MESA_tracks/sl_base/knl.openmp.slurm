#!/bin/bash
#----------------------------------------------------
# Sample Slurm job script
#   for TACC Stampede2 KNL nodes
#
#   *** OpenMP Job on Normal Queue ***

#SBATCH -J star_lift           # Job name
#SBATCH -o myjob.o1       # Name of stdout output file
#SBATCH -e myjob.e1       # Name of stderr error file
#SBATCH -p normal          # Queue (partition) name
#SBATCH -N 1               # Total # of nodes
#SBATCH -n 1               # Total # of mpi tasks
#SBATCH -t 10:00:00        # Run time (hh:mm:ss)
#SBATCH --mail-user=mts2188@columbia.edu
#SBATCH --mail-type=NONE    # Send email at begin and end of job

# Other commands must follow all #SBATCH directives...

module list
pwd
date

#Set thread count (default value is 1)...

export OMP_NUM_THREADS=48


# Launch OpenMP code...
rm output?.txt
rm output_best.txt
rm step_*
cp inlist_project_full inlist_project
./rn >> output_full.txt
python sl_mesa.py 0 0
./rn >> output_best.txt
cp output_best.txt output_start.txt
t=1
while [ $t -le 5000 ]
do
	for i in 1 2 3 4 5
	do
		python sl_mesa.py $i $t
		./rn >> output"$i".txt
	done
	cont=$(python sl_mesa.py 6 $t)
	if [[ *"$cont"* == *"False"* ]]; then
		break	
	fi
	./rn >> output_best.txt
	t=$(( $t + 1 ))
done
