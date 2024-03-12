import pyautogui
import time
import subprocess
import os 
import threading
import traceback

def print_progress_bar(iteration, total, prefix='', suffix='', length=50, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

"""
    Directories made:
        pyrxPDBOuputs:  contains the output files of the PyRx execution
                        with the same compound name and .pdb extension
        PDBQTmodel1:     contains the output files of the webina execution
                         but only the first model
"""

"""
    Requirements:
    PyRx app installed as 'cscript' at path 'C:\Program Files (x86)\PyRx\PyRx.vbs' (windows)

    The folder structure must be the following:
    -Project's folder
        -pyrx.py
        -webinaPDBQTOutputs
"""

def runPyRx(threadID):
    for i in range(threadID, upperLimit, totalThreads):
        try:
            print_progress_bar(len(os.listdir(pyrxPDBOuputs_path)), upperLimit, prefix = 'Progress:', suffix = 'Complete', length = 50)

            compoundName = compoundNames[i]
            # if the results already exist then continue
            if os.path.exists(os.path.join(pyrxPDBOuputs_path, compoundName+'.pdb')):
                continue

            # if the file only with the first model doesnt exist create it 
            if not os.path.exists(os.path.join(PDBQTmodel1_path, compoundName+'.pdbqt')):
                with open(os.path.join(compoundsPath, compoundName+'.pdbqt'), 'r') as file:
                    lines = file.readlines()
                # Boolean to keep track of whether we're at the first model
                at_first_model = False
                # List to hold the lines of the first model
                first_model_lines = []
                # Go through each line in the file
                for line in lines:
                    if line.startswith('MODEL 1'):
                        at_first_model = True
                    if at_first_model:
                        first_model_lines.append(line)
                        if line.startswith('ENDMDL'):
                            break  # Stop after the first model is completely read
                # Write the first model to the output file
                with open(os.path.join(PDBQTmodel1_path, compoundName+'.pdbqt'), 'w') as file:
                    file.writelines(first_model_lines)
            # start the pyrx
            subprocess.Popen(['cscript', 'C:\Program Files (x86)\PyRx\PyRx.vbs'])
            time.sleep(big_delay) 
            pyautogui.hotkey('win', 'up')
            time.sleep(2*short_delay)
            pyautogui.click((18, 46)) # File
            time.sleep(short_delay) 
            pyautogui.click((55, 78)) # Load Molecule
            time.sleep(short_delay) 
            #pyautogui.click((457, 585)) # File Name
            pyautogui.write(os.path.join(PDBQTmodel1_path, compoundName+'.pdbqt'))
            time.sleep(short_delay) 
            pyautogui.press('Enter')
            time.sleep(2*short_delay) 
            pyautogui.rightClick((164, 168)) # right click on the first model
            time.sleep(short_delay) 
            pyautogui.click((254, 247)) # Save as PDB
            time.sleep(short_delay) 
            pyautogui.write(os.path.join(pyrxPDBOuputs_path, compoundName))
            time.sleep(short_delay) 
            pyautogui.press('Enter')
            time.sleep(short_delay)
            pyautogui.hotkey('alt', 'f4')
            time.sleep(2*short_delay)
        except Exception as e:
            tb_str = traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
            exceptions.append((threadID, ''.join(tb_str)))
            

def main():
    global current_dir
    current_dir = os.getcwd()
    # check if the desired directories exist, otherwise create them
    global pyrxPDBOuputs_path
    pyrxPDBOuputs_path = os.path.join(current_dir, 'pyrxPDBOuputs')
    if not os.path.exists(pyrxPDBOuputs_path):
        os.makedirs(pyrxPDBOuputs_path)
    global PDBQTmodel1_path
    PDBQTmodel1_path = os.path.join(current_dir, 'PDBQTmodel1')
    if not os.path.exists(PDBQTmodel1_path):
        os.makedirs(PDBQTmodel1_path)

    # List all entries in the compound directory
    global compoundsPath
    compoundsPath = os.path.join(current_dir, 'webinaPDBQTOutputs')
    directory_contents = os.listdir(compoundsPath)
    # Filter out directories, keep only files, remove the .pdbqt extension, and sort alphabetically
    global compoundNames
    compoundNames = sorted([os.path.splitext(entry)[0] for entry in directory_contents 
                                    if os.path.isfile(os.path.join(compoundsPath, entry)) and entry.endswith('.pdbqt')])
    print("length of compound names: ", len(compoundNames))
    print("compoundsPath: ", compoundsPath)
    # Create a thread for each compound
    threads = []
    global exceptions
    exceptions=[]
    global totalThreads
    totalThreads = 1
    global short_delay
    short_delay = 0.5
    global big_delay
    big_delay = 10
    # loop while exceptions occured, some files not processed
    # try again 
    tries = 0
    global upperLimit
    upperLimit = len(compoundNames) # process up to that limit the compounds
    # Initial call to print 0% progress
    print_progress_bar(0, upperLimit, prefix = 'Progress:', suffix = 'Complete', length = 50)
    while(True): 
        print(f"------------- {tries}th try ----------------")
        for index in range(totalThreads): 
            t = threading.Thread(target=runPyRx, args=(index,))
            threads.append(t)
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        # Check for exceptions
        if exceptions:
            for threadID, exception in exceptions:
                print(f"Exception in thread {threadID}: {exception}")
            print(f"-----------------------------------------")
            tries += 1
            exceptions=[]
            threads = []
        else:
            print("No exceptions occurred.")
            # Initial call to print 0% progress
            print_progress_bar(upperLimit, upperLimit, prefix = 'Progress:', suffix = 'Complete', length = 50)
            break

if __name__ == "__main__":
    start_time = time.perf_counter()
    main()
    # Record the end time with higher precision
    end_time = time.perf_counter()
    # Calculate the total execution time
    execution_time = end_time - start_time
    hours, remainder = divmod(execution_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    print(f"The script executed in {int(hours)} hours, {int(minutes)} minutes, and {seconds} seconds.")
    print(f"{upperLimit} compounds processed")