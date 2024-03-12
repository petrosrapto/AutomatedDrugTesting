from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.alert import Alert
import os 
import time
import shutil
import threading
import traceback
import sqlite3
import pandas as pd

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
        compoundsWithFinal: contains the output files of the pyrx execution
                            with extension .pdb combined with the 7RPZ_final.pdb
        plipXMLOuputs:      contains the XML output files of the PLIP execution
        plipTXTOuputs:      contains the TXT output files of the PLIP execution
        Downloads:          temporary directory that holds the downloads
                            of the website
"""

"""
    Requirements:
    googlechrome driver installed at the path '/usr/local/bin/chromedriver'
    
    The folder structure must be the following:
    -Project's folder
        -compounds.db
        -plip.py
        -7RPZ_final.pdb
        -pyrxPDBOutputs folder which include the outputs of the pyrx execution with extension .pdb
"""

def insert_into_database(db_path, compound_name, URL):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS URLs
                      (compound_name TEXT PRIMARY KEY, URL TEXT)''')
    
    # Insert the data, replace the url if already one exists 
    cursor.execute("INSERT OR REPLACE INTO URLs (compound_name, URL) VALUES (?, ?)",
                   (compound_name, URL))
    
    # Commit changes and close connection
    conn.commit()
    conn.close()

def runPLIP(threadID):
    # in order to avoid conflicts between threads 
    # we must have seperate folders for each thread's Downloads
    my_download_path = os.path.join(download_path, 'thread'+str(threadID))
    if not os.path.exists(my_download_path):
        os.makedirs(my_download_path)

    # Specify the path to your WebDriver here
    driver = None # just init
    driver_path = '/usr/local/bin/chromedriver'
    service = Service(executable_path=driver_path)
    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": my_download_path,
            "download.prompt_for_download": False,  # To automatically download the file to the specified directory
            "download.directory_upgrade": True,  # To make Chrome aware of the download directory's existence
            "plugins.always_open_pdf_externally": True  # It will not show PDF directly in Chrome
            }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--no-sandbox")  # Bypass OS security model; caution: use only if you understand the security implications
    options.headless = True  # Run Chrome in headless mode

    for i in range(threadID, upperLimit, totalThreads):
        try:
            print_progress_bar(len(os.listdir(plipXMLOuputs_path)), upperLimit, prefix = 'Progress:', suffix = 'Complete', length = 50)
            compoundName = compoundNames[i]

            # if the results already exist then continue
            if os.path.exists(os.path.join(plipXMLOuputs_path, compoundName+'.xml')) and \
                os.path.exists(os.path.join(plipTXTOuputs_path, compoundName+'.txt')):
                continue

            # the following two compounds get the error "We could not find any binding sites within your structure"
            # from the PILP analysis
            if compoundName == 'ZINC000006731693' or compoundName == 'ZINC000006731959':
                continue

            if not os.path.exists(os.path.join(compoundsWithFinal_path, compoundName+'.pdb')):
                # Note that reading the same files from different threads in parallel does NOT
                # typically result into conflicts
                with open(os.path.join(current_dir, '7RPZ_final.pdb'), 'r') as file:
                    final_content = file.readlines()
    
                # Find the index of the line that contains 'END'
                end_index = None
                for i, line in enumerate(final_content):
                    if 'END' in line:
                        end_index = i
                        break
                
                # If 'END' was found, insert the content from the compound pdb file
                if end_index is not None:
                    # Read the content of the compound file
                    with open(os.path.join(compoundsPath, compoundName+'.pdb'), 'r') as file:
                        compound_content = file.read()
                    
                    # Insert the compound pdb file content into the final content before 'END'
                    final_content.insert(end_index, compound_content)
                    
                    # Write the modified content to the modified file
                    with open(os.path.join(compoundsWithFinal_path, compoundName+'.pdb'), 'w') as file:
                        file.writelines(final_content)

            driver = webdriver.Chrome(service=service, options=options)
            time.sleep(big_delay)
            # Open the website
            driver.get('https://plip-tool.biotec.tu-dresden.de/plip-web/plip/index')
            driver.implicitly_wait(3)
            time.sleep(big_delay)
            # wait until website resources are ready
            WebDriverWait(driver, 10).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            # upload file
            filenameID = 'file-upload'
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, filenameID))
            )
            driver.find_element(By.ID, filenameID).send_keys(os.path.join(compoundsWithFinal_path, compoundName+'.pdb'))
            time.sleep(short_delay)
            # click start analyze button
            button = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/form/div[4]/input')
            button.send_keys("\n")
            time.sleep(short_delay)
            WebDriverWait(driver, 100).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div/div[3]/div/div[1]/div[2]/a[1]')))
            time.sleep(short_delay)
            insert_into_database('compounds.db', compoundName, driver.current_url)
            # download xml
            before_files = set(os.listdir(my_download_path))
            button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[3]/div/div[1]/div[2]/a[1]')))
            button.send_keys("\n")
            time.sleep(short_delay)   
            after_files = set(os.listdir(my_download_path))
            file_downloaded = (after_files - before_files).pop()
            shutil.move(os.path.join(my_download_path, file_downloaded), os.path.join(plipXMLOuputs_path, compoundName+'.xml'))   
            time.sleep(short_delay)   
            # download txt
            before_files = set(os.listdir(my_download_path))
            button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[3]/div/div[1]/div[2]/a[2]')))
            button.send_keys("\n")
            time.sleep(short_delay)   
            after_files = set(os.listdir(my_download_path))
            file_downloaded = (after_files - before_files).pop()
            shutil.move(os.path.join(my_download_path, file_downloaded), os.path.join(plipTXTOuputs_path, compoundName+'.txt'))   
            time.sleep(short_delay)  
        except Exception as e:
            tb_str = traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
            exceptions.append((threadID, ''.join(tb_str)))
        finally:
            if driver is not None:
                driver.quit()  # automatically close the browser
                time.sleep(short_delay)
                

def main():
    global current_dir
    current_dir = os.getcwd()
    # check if the desired directories exist, otherwise create them
    global compoundsWithFinal_path
    compoundsWithFinal_path = os.path.join(current_dir, 'compoundsWithFinal')
    if not os.path.exists(compoundsWithFinal_path):
        os.makedirs(compoundsWithFinal_path)
    global plipXMLOuputs_path
    plipXMLOuputs_path = os.path.join(current_dir, 'plipXMLOuputs')
    if not os.path.exists(plipXMLOuputs_path):
        os.makedirs(plipXMLOuputs_path)
    global plipTXTOuputs_path
    plipTXTOuputs_path = os.path.join(current_dir, 'plipTXTOuputs')
    if not os.path.exists(plipTXTOuputs_path):
        os.makedirs(plipTXTOuputs_path)
    global download_path
    download_path = os.path.join(current_dir, 'Downloads')
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    # List all entries in the compound directory
    global compoundsPath
    compoundsPath = os.path.join(current_dir, 'pyrxPDBOuputs')
    directory_contents = os.listdir(compoundsPath)
    # Filter out directories, keep only files, remove the .sdf extension, and sort alphabetically
    global compoundNames
    compoundNames = sorted([os.path.splitext(entry)[0] for entry in directory_contents 
                                    if os.path.isfile(os.path.join(compoundsPath, entry)) and entry.endswith('.pdb')])
    
    # Create a thread for each compound
    threads = []
    global exceptions
    exceptions=[]
    global totalThreads
    totalThreads = 1
    global short_delay
    short_delay = 5
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
            t = threading.Thread(target=runPLIP, args=(index,))
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

            # produce excel
            conn = sqlite3.connect('compounds.db')
            query = "SELECT compound_name, URL FROM URLs"  
            df = pd.read_sql_query(query, conn)
            conn.close()
            df.to_excel('URLs.xlsx', index=False, engine='openpyxl')

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

    
"""
    Methology: How to work with selenium and web automation
    -> See the element of the webpage you want to interact with,
    right click on it and click "inspect"
    repeat: right click on it and click "inspect"
    the developer tools will appear and the HTML of the 
    element you want will be highlighted. Right click on it,
    select copy and full xPath. with that path you can identify 
    the element using selenium commands like:
    button = driver.find_element(By.XPATH, '/html/body/div/div[3]/div/div[2]/div[1]/p/div/form/button')

    -> in order to click the buttons dont call the .click() but the button.send_keys("\n") which is
    equivalent to say that we picked the button and pressed enter.

    -> apply enough time.sleep() as the WebDriverWait..until dont work as expected
"""
