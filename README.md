# alteryx2python
Send data from Alteryx to Python, execute script and send Python output back to Alteryx workflow.

## Step 1: Source of data from Alteryx.
For this example, I’ve just used a simple text input with some file paths, but this can be anything generated from Alteryx.

<p align="center"><img src="https://github.com/jeffmaxey/alteryx2python/blob/master/alteryx2python/pictures/step1.jpg"></p>


## Step 2: Connect to Run Command Tool. 
<p align="center"><img src="https://github.com/jeffmaxey/alteryx2python/blob/master/alteryx2python/pictures/Capture.JPG"></p>

As for the options:
1.	Write source will take whatever data is coming IN to the tool, that is the data stream that is attached to the input of the Run Command, and write it to the file or connection specified.
  a.	The point of this is to dump the data that is currently in Alteryx to a file so that your script can then read the file.
2.	Under 'Run External Program Command:' for a Python script, your command should be Python.exe. If the directory where Python exists is in your system path variable, you can simply type Python.exe, otherwise you will have to give it the full path keeping in mind to quote the string if there are spaces (e.g. "Program Files"). I however believe it is best practice to always include the entire file paths.

3.	In command argument, you will type the location of your Python script your_python_script.py (Alteryx's default working directory is the directory of the running module so if is easiest to keep your script nearby and simply type "your_python_script.py" instead of the full path) and any - or -- options necessary. Remember to quote this string.

4.	The default working directory for Alteryx is the directory of the running module unless set otherwise.
  a.	It is possible to find the working directory of your python script by running the following in python:
    ```python
    import os
    os.getcwd()
    # 'C:\\temp\\moses2axis'
    ```
    
5.	Your Python script should then write to a file at the end of its processing.
6.	The Read Results option should point to the file written by your Python script. This way, Alteryx can read back in the data that was processed by the external command.

## Step 3: Write Python Script That Reads Alteryx Output
```python
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
import errno 

# // install packages dynamically, adjusting to corporate proxy
def install(name):
    subprocess.call(['pip', '--proxy=cr-proxy.us.aegon.com:9090', 'install', name])

# // install packages from internet as needed
install('pandas')
install('xlrd')
install('openpyxl')

# // then you can import the packages
import pandas as pd
import xlrd
from openpyxl.workbook import Workbook

# // PYTHON SCRIPT MUST BE LOCATED IN SAME DIECTORY AT THE SAME DIRECTORY LEVEL AS ALTERYX WORKFLOW.
# // specify the directory containing output from alteryx workflow
dir_path = os.path.dirname(os.path.realpath(__file__))


# // user-defined function that creates python output directory if it does not already exist
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

# /// establish an output path for python files
dir_python_output = os.path.join(dir_path, 'python_output')

# // create python output folder using user-defined mkdir_p(path) function from above.
mkdir_p(dir_python_output)

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


# // call the function you created above to collect a list of files in the folder; returns a list
# // returns: ['C:\\Temp\\moses2axis\\docs\\csv\\alteryx_output\\alteryx_output_file_path.csv']
file_list = list_file_paths(root_path=dir_path, ext='.csv')

# // select the file from the list using indexing; returns a string
# // returns: 'C:\\Temp\\moses2axis\\docs\\csv\\alteryx_output\\alteryx_output_file_path.csv'
desired_file = file_list[0]

# // easiest way to read a file is using pandas; you can even do pd.read_excel, pd.read_sql and many more:
df = pd.read_csv(desired_file, sep=',', header=0)

# // remove "?" character that may arise from text encoding
df.columns = [col.replace("?", "") for col in df.columns.tolist()]

# // create a function to transfer data from xls file to xlsx file.
def convert_xls_to_xlsx(src_file_path, dst_file_path):
    """
    Purpose: Convert xls file to xlsx. Assumes simple files, no graphics or advanced formatting
    :param src_file_path: 
    :param dst_file_path: 
    :return: 
    """
    book_xls = xlrd.open_workbook(src_file_path)
    book_xlsx = Workbook()

    sheet_names = book_xls.sheet_names()
    for sheet_index in range(0, len(sheet_names)):
        sheet_xls = book_xls.sheet_by_name(sheet_names[sheet_index])
        if sheet_index == 0:
            sheet_xlsx = book_xlsx.active
            sheet_xlsx.title = sheet_names[sheet_index]
        else:
            sheet_xlsx = book_xlsx.create_sheet(title=sheet_names[sheet_index])

        for row in range(0, sheet_xls.nrows):
            for col in range(0, sheet_xls.ncols):
                sheet_xlsx.cell(row=row+1, column=col+1).value = sheet_xls.cell_value(row, col)
    book_xlsx.save(dst_file_path)


# // just to show an example of python performing a procedure, lets create an additional column and add the basename
# // of the file path.
# // e.g. 'C:\\Temp\\moses2axis\\docs\\csv\\alteryx_output\\alteryx_output_file_path.csv' --> 'alteryx_output_file_path.csv'
df['file_path_xlsx'] = df['file_path'].apply(lambda x: x.replace('.xls', '.xlsx'))


# // generate a csv file path and output data frame; e.g. 'C:\\Temp\\moses2axis\\moses2axis\\app\\project_directory\\docs\\csv\\xref.csv'
filepathCSV = os.path.join(dir_python_output, "example.csv")
df.to_csv(filepathCSV, sep=",", header=True, index=False)


# // list of xls files
file_list = list_file_paths(dir_path, ext='.xls')


# // for each file in the list of .xls files; call the convert_xls_to_xlsx function.
# // the second parameter creates the desired output file path by replacing ".xls" by ".xlsx"
for file in file_list:
    convert_xls_to_xlsx(file, file.replace(".xls", ".xlsx"))


```

## Step 4: Stream Python Output Back Into Alteryx Workflow
The Read Result Option path specified in the Run Command Tool in Alteryx matches the output file path generated from the python script, and the result will be read back into Alteryx after the python script has been completed (e.g. base_table_name column has been added).

<p align="center"><img src="https://github.com/jeffmaxey/alteryx2python/blob/master/alteryx2python/pictures/step3.jpg"></p>

