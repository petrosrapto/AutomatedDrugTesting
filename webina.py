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
        webinaTXTOuputs: contains the output files of the webina execution
                         with the same compound name and .txt extension
        webinaPDBQTOuputs: contains the output files of the webina execution
                           with the same compound name and .pdbqt extension
        Downloads:       temporary directory that holds the downloads
                         of the website
"""

"""
    Requirements:
    googlechrome driver installed at the path '/usr/local/bin/chromedriver'

    The folder structure must be the following:
    -Project's folder
        -webina.py
        -7RPZ_final.pdb
        -7RPZ_KRAS_ligand.pdb
        -Testing_Compounds_Specs_Natural_Products folder which include the compounds with ending .sdf
"""

def runWebina(threadID):
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
            print_progress_bar(len(os.listdir(webinaTXTOutputs_path))+len(os.listdir(webinaPDBQTOutputs_path)), 2*upperLimit, prefix = 'Progress:', suffix = 'Complete', length = 50)

            compoundName = compoundNames[i]
            # if the results already exist then continue
            if os.path.exists(os.path.join(webinaPDBQTOutputs_path, compoundName+'.pdbqt')) and \
            os.path.exists(os.path.join(webinaTXTOutputs_path, compoundName+'.txt')):
                continue

            driver = webdriver.Chrome(service=service, options=options)
            time.sleep(big_delay)
            # Open the website
            driver.get('https://durrantlab.pitt.edu/webina/')
            driver.implicitly_wait(3)
            time.sleep(big_delay)
            # wait until website resources are ready
            WebDriverWait(driver, 10).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
            )

        # -------------------------- LIGAND FIELD --------------------------
            ligandID = "__BVID__24"
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, ligandID))
            )
            driver.find_element(By.ID, ligandID).send_keys(os.path.join(current_dir, 'Testing_Compounds_Specs_Natural_Products/'+compoundName+'.sdf'))

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'ph-val'))
            )
            driver.find_element(By.ID, 'ph-val').clear()
            driver.find_element(By.ID, 'ph-val').send_keys('7.5')

            try:
                time.sleep(short_delay)
                button = driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div/div/footer/button[2]')
                button.send_keys("\n")
                time.sleep(short_delay)
            except Exception as e:
                exceptions.append((threadID, e))

        # -------------------------- RECEPTOR FIELD --------------------------
            receptorID = "__BVID__20"
            # Wait for the input fields to be loaded
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, receptorID))
            )
            driver.find_element(By.ID, receptorID).send_keys(os.path.join(current_dir, '7RPZ_final.pdb'))
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'ph-val'))
            )
            driver.find_element(By.ID, 'ph-val').clear()
            driver.find_element(By.ID, 'ph-val').send_keys('7.5')

            try:
                time.sleep(short_delay)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[1]/div/div/footer/button[2]')))
                button = driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div/div/footer/button[2]')
                button.send_keys("\n")
                time.sleep(short_delay)
                button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[1]/div/div/footer/button')))
                button.send_keys("\n")
                time.sleep(short_delay)
            except Exception as e:
                exceptions.append((threadID, e))

        # -------------------------- CORRECT POSE FIELD --------------------------
            correctPoseID = "__BVID__28"
            # Wait for the input fields to be loaded
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, correctPoseID))
            )
            driver.find_element(By.ID, correctPoseID).send_keys(os.path.join(current_dir, '7RPZ_KRAS_ligand.pdb'))
            time.sleep(short_delay)

            # fill box centers and box sizes
            driver.find_element(By.ID, 'center_x').clear()
            driver.find_element(By.ID, 'center_x').send_keys('1')
            driver.find_element(By.ID, 'center_y').clear()
            driver.find_element(By.ID, 'center_y').send_keys('6')
            driver.find_element(By.ID, 'center_z').clear()
            driver.find_element(By.ID, 'center_z').send_keys('-24') 
            driver.find_element(By.ID, 'size_x').clear()
            driver.find_element(By.ID, 'size_x').send_keys('16') 
            driver.find_element(By.ID, 'size_y').clear()
            driver.find_element(By.ID, 'size_y').send_keys('15') 
            driver.find_element(By.ID, 'size_z').clear()
            driver.find_element(By.ID, 'size_z').send_keys('11') 

            try:
                # click start webina
                button = driver.find_element(By.XPATH, '/html/body/div/div[3]/div/div[2]/div[1]/p/div/form/button')
                button.send_keys("\n")
                WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div/div[3]/div/div[2]/div[3]/p/div/span')))
                WebDriverWait(driver, 6000).until(EC.invisibility_of_element_located((By.XPATH, '/html/body/div/div[3]/div/div[2]/div[3]/p/div/span')))
            except Exception as e:
                exceptions.append((threadID, e))
            time.sleep(short_delay)
            before_files = set(os.listdir(my_download_path))
            # download affinities
            button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[3]/div/div[2]/div[4]/p/div/div[2]/div/p/span[1]/div/div/button')))
            button.send_keys("\n")
            time.sleep(short_delay)
            after_files = set(os.listdir(my_download_path))
            file_downloaded = (after_files - before_files).pop()
            # move the file into webinaTXTOutputs
            shutil.move(os.path.join(my_download_path, file_downloaded), os.path.join(webinaTXTOutputs_path, compoundName+'.txt'))
            """
                Note:
                If the destination path is a file that already exists, 
                the existing file at the destination will be overwritten 
                by the file being moved.
            """
            time.sleep(1)

            before_files = set(os.listdir(my_download_path))
            # download pdbqt
            button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[3]/div/div[2]/div[4]/p/div/div[2]/div/p/span[2]/div/div/button')))
            button.send_keys("\n")
            time.sleep(short_delay)
            after_files = set(os.listdir(my_download_path))
            file_downloaded = (after_files - before_files).pop()
            # move the file into webinaPDBQTOutputs
            shutil.move(os.path.join(my_download_path, file_downloaded), os.path.join(webinaPDBQTOutputs_path, compoundName+'.pdbqt'))
            time.sleep(short_delay)
        except Exception as e:
            exceptions.append((threadID, e))
        finally:
            if driver is not None:
                driver.quit()  # automatically close the browser
                time.sleep(short_delay)
                

def main():
    global current_dir
    current_dir = os.getcwd()
    # check if the desired directories exist, otherwise create them
    global webinaTXTOutputs_path
    webinaTXTOutputs_path = os.path.join(current_dir, 'webinaTXTOutputs')
    if not os.path.exists(webinaTXTOutputs_path):
        os.makedirs(webinaTXTOutputs_path)
    global webinaPDBQTOutputs_path
    webinaPDBQTOutputs_path = os.path.join(current_dir, 'webinaPDBQTOutputs')
    if not os.path.exists(webinaPDBQTOutputs_path):
        os.makedirs(webinaPDBQTOutputs_path)
    global download_path
    download_path = os.path.join(current_dir, 'Downloads')
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    # List all entries in the compound directory
    compoundsPath = os.path.join(current_dir, 'Testing_Compounds_Specs_Natural_Products/')
    directory_contents = os.listdir(compoundsPath)
    # Filter out directories, keep only files, remove the .sdf extension, and sort alphabetically
    global compoundNames
    compoundNames = sorted([os.path.splitext(entry)[0] for entry in directory_contents 
                                    if os.path.isfile(os.path.join(compoundsPath, entry)) and entry.endswith('.sdf')])
    
    # Create a thread for each compound
    threads = []
    global exceptions
    exceptions=[]
    global totalThreads
    totalThreads = 10
    global short_delay
    short_delay = 10
    global big_delay
    big_delay = 20
    # loop while exceptions occured, some files not processed
    # try again 
    tries = 0
    global upperLimit
    upperLimit = len(compoundNames) # process up to that limit the compounds
    # Initial call to print 0% progress
    print_progress_bar(0, 2*upperLimit, prefix = 'Progress:', suffix = 'Complete', length = 50)
    while(True): 
        print(f"------------- {tries}th try ----------------")
        for index in range(totalThreads): 
            t = threading.Thread(target=runWebina, args=(index,))
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
            print_progress_bar(2*upperLimit, 2*upperLimit, prefix = 'Progress:', suffix = 'Complete', length = 50)
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
