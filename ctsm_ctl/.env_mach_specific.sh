# This file is for user convenience only and is not used by the model
# Changes to this file will be ignored and overwritten
# Changes to the environment should be made in env_mach_specific.xml
# Run ./case.setup --reset to regenerate this file
source /cluster/software/lmod/lmod/init/sh
module purge --force
module load StdEnv iimpi/2019b netCDF-Fortran/4.5.2-iimpi-2019b CMake/3.15.3-GCCcore-8.3.0
export KMP_STACKSIZE=256M
export I_MPI_EXTRA_FILESYSTEM_LIST=lustre
export I_MPI_EXTRA_FILESYSTEM=on