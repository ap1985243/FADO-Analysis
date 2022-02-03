import os
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import os
import re
from os import listdir
from os.path import isfile, join, isdir

#cmd1 = "./FADO -i input/2022/5.txt -o output/2022/co2_01.K.3284.ell.1d -b SSPs/Base.BC03.L -s 5700 7300 5.5 -r 13 -u 1.0e-17 -v10"
#cmd2 = "./FADO -i input/2022/7.txt -o output/2022/co2_07.K.6743.ell.1d -b SSPs/Base.BC03.L -s 5500 6900 5 -r 12 -u 1.0e-17 -v10"
#os.system(cmd1)
#os.system(cmd2)

# generate_input_filename will tell FADO which file(full path!) will be the input spectra
# function takes the path of a folder as input and then works on each file to generate the input command
def generate_input_filename(filename):
    snippet = filename[82:]
    return "input/nrmalerror/"+snippet

# similar to the generate_input_filename function and provides the path of the output file for FADO
def generate_output_filename(filename):
    snippet = filename[82:]
    output = "output/error-spectra-included-fado-output/"+snippet
    return output

# get_fwhm is at the heart of the FADO command
# it looks up the name of the given file in the MOSDEF linemas file and returns the FWHM of the H-alpha line
def get_fwhm(filename):
    fits_filename = 'linemeas_cor.fits'
    snippet = filename
    count = 0
    spectral_fwhm = 2350
    for i in snippet:
        if (i == "."):
            count +=1
    if (count == 5):
        #print("Object observed as intended")
        #id = snippet[91:-11] (previously used let to errors sometimes due to varibale file names)
        #print(id)
        split1 = snippet.split(".")
        id = split1[2]
        hdul = fits.open('linemeas_cor.fits')
        flux = hdul[1].data
        #print(len(flux))
        for i in range(1824):
            if (flux[i][2] == int(id)  and flux[i][4] == 1):
                print("FOUND!!")
                spectral_fwhm = flux[i]['Ha6565_FWHM']
                hdul.close()

    if (count == 6):
        #print("Object detected serendipitously!")
        split1 = snippet.split(".")
        slit_name = split1[2]
        apperture = split1[3]
        #new_snip = snippet[91:-11]
        #slit_name = new_snip[0:-2]
        #apperture = new_snip[-1:]
        hdul = fits.open(fits_filename)
        flux = hdul[1].data
        for i in range(1824):
            if (flux[i][3] == int(slit_name) and flux[i][4] == int(apperture) ):
                print("FOUND!!")
                spectral_fwhm = flux[i]['Ha6565_FWHM']
                hdul.close()


    return spectral_fwhm

# generate_spectral_limit will open a given file and check its upper and lower wavelength bounds
# it will tell FADO the spectral range for the synthetic SED curve
# finally, it divides spectral_fwhm by 2.35 to give the resolution of the synthetic SED
def generate_spectral_limit (filename, spectral_fwhm):
    absolute_path = "/home/user/PycharmProjects/pythonProject/TASK /command-generator/7.txt"
    array = np.loadtxt(absolute_path)
    len_arr = len(array)
    start = array[0][0]
    end = array[len_arr - 1][0]
    start_rounded = int(round(start))
    end_rounded = int (round(end))
    synthetic_sed_fwhm = spectral_fwhm/(2.35)
    return_query = str(start_rounded)+" "+str(end_rounded)+" "+str(synthetic_sed_fwhm)+" "
    return return_query


# generate_command is responsible for assembling all the information from the above functions
# and generate a valid FADO command, the function returns the FADO command
# example of a FADO command:
# ./FADO -i input/2022/5.txt -o output/2022/co2_01.K.3284.ell.1d -b SSPs/Base.BC03.L -s 5700 7300 5.5 -r 13 -u 1.0e-17 -v10
def generate_command (filename):
    input_fwhm = get_fwhm(filename)
    input_file = generate_input_filename(filename)
    initial_bit = "./FADO -i "
    output_bit = " -o "
    output_file = generate_output_filename(filename)
    library_bit = " -b SSPs/Base.BC03.L -s "
    spectral_bit = generate_spectral_limit(filename, input_fwhm)
    input_res = " -r "
    final_bit = " -u 1.0e-17 -v10"
    full_command = initial_bit+input_file+output_bit+output_file+library_bit+spectral_bit+input_res+str(input_fwhm)+final_bit
    return full_command


# execute_command executes the command returned by generate_command with the help of os module
def execute_command (command_for_terminal):
    os.system(command_for_terminal)
    return 0


# getAllFilesRecursive takes a directory and lists every file that is in it
# this function was sourced from the internet!
# Credit-- Stack overflow user Matheus Araujo (link: https://stackoverflow.com/users/1362866/matheus-araujo)
# Link to answer-- https://stackoverflow.com/questions/4918458/how-to-traverse-through-the-files-in-a-directory
def getAllFilesRecursive(root):
    files = [ join(root,f) for f in listdir(root) if isfile(join(root,f))]
    dirs = [ d for d in listdir(root) if isdir(join(root,d))]
    for d in dirs:
        files_in_d = getAllFilesRecursive(join(root,d))
        if files_in_d:
            for f in files_in_d:
                files.append(join(root,f))
    return files



if __name__ == '__main__':
    files_present = getAllFilesRecursive("/home/user/PycharmProjects/pythonProject/TASK /command-generator/input/nrmalerror/")
    #command = generate_command("/home/user/PycharmProjects/pythonProject/TASK /command-generator/input/54321error/co2_07.K.6743.ell.1d.txt")
    #print(command)
    #cmd1 = "./FADO -i input/2022/5.txt -o output/2022/co2_01.K.3284.ell.1d.txt -b SSPs/Base.BC03.L -s 5700 7300 5.5 -r 13 -u 1.0e-17 -v10"
    #os.system(cmd1)
    #print(command)
    #execute_command(command)
    for i in files_present:
        #print(i)
        command = generate_command(i)
        print(command)
        execute_command(command)

    print(len(files_present))
