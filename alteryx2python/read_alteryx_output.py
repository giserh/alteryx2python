#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author: jeff maxey
date: 2018.05.15
purpose: example demonstrating integration of python and alteryx
"""

# // import packages
import os
import subprocess

def install(name):
    subprocess.call(['pip', '--proxy=cr-proxy.us.aegon.com:9090', 'install', name])
install('pandas')

import pandas as pd

# // define a function that will list all file paths in specified root directory with specified file extension
def list_file_paths(root_path, ext):
    """
    Purpose: Search all folders in root_path for specific file type.
    :param root_path: The parent directory for traversal search
    :param ext: Specified file extension desired to be searched for.
    :return: A list of files located within root_path that possess specified file extension
    """
    # // create an empty list for storing all file paths
    all_files = []

    # // walk entire directory of root_path; all sub-folders and files will be checked.
    for root, dirs, files in os.walk(root_path):
        for filename in files:
            # // check if file name ends with specified extension
            if filename.lower().endswith(ext):
                # // if it does, generate the full path using os.path.join() and append it to all_files list
                all_files.append(os.path.join(root, filename))

    # // return the list of files
    return all_files


# // specify the directory containing output from alteryx workflow
dir_alteryx_output = r"C:\Temp\moses2axis\docs\csv\alteryx_output"

# // call the function you created above to collect a list of files in the folder; returns a list
# // returns: ['C:\\Temp\\moses2axis\\docs\\csv\\alteryx_output\\alteryx_output_file_path.csv']
file_list = list_file_paths(root_path=dir_alteryx_output, ext='.csv')

# // select the file from the list using indexing; returns a string
# // returns: 'C:\\Temp\\moses2axis\\docs\\csv\\alteryx_output\\alteryx_output_file_path.csv'
desired_file = file_list[0]

# // easiest way to read a file is using pandas; you can even do pd.read_excel, pd.read_sql and many more:
df = pd.read_csv(desired_file, sep=',', header=0)

# // just to show an example of python performing a procedure, lets create an additional column and add the basename
# // of the file path.
# // e.g. 'C:\\Temp\\moses2axis\\docs\\csv\\alteryx_output\\alteryx_output_file_path.csv' --> 'alteryx_output_file_path.csv'
df['base_table_name'] = df['file_path'].apply(lambda x: os.path.basename(x))


# // generate a csv file path and output data frame; e.g. 'C:\\Temp\\moses2axis\\moses2axis\\app\\project_directory\\docs\\csv\\xref.csv'
filepathCSV = os.path.join(dir_alteryx_output, "example.csv")
df.to_csv(filepathCSV, sep=",", header=True, index=False)

