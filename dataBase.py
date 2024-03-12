import sqlite3
import re
import os
import pandas as pd

"""
    Directories made:
        compounds.db file: contains database
        affinities.xlsx:   excel with compound names and best affinities
    Requirements:
    The folder structure must be the following:
    -Project's folder
        -dataBase.py
        -webinaTXTOutputs folder with the results of webina.py in .txt
"""

# Function to extract affinity of mode 1
def extract_mode_1_affinity(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Regular expression to find the affinity for mode 1
    # mode_1_match = re.search(r'\s+1\s+(-\d+\.\d+)', content)
    mode_1_match = re.search(r'\s+1\s+(-\d+(?:\.\d+)?)', content)
    if mode_1_match:
        return mode_1_match.group(1)
    else:
        print("Mode 1 affinity not found.")
        return None

# Function to insert data into the database
def insert_into_database(db_path, compound_name, affinity):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS affinities
                      (compound_name TEXT PRIMARY KEY, mode_1_affinity REAL)''')
    
    # Insert the data, ignore the query if data exist for that primary key
    cursor.execute("INSERT OR IGNORE INTO affinities (compound_name, mode_1_affinity) VALUES (?, ?)",
                   (compound_name, affinity))
    
    # Commit changes and close connection
    conn.commit()
    conn.close()

try:

    db_path = 'compounds.db'
    current_dir = os.getcwd()
    excel_path = 'affinities.xlsx'  
    if not os.path.exists(os.path.join(current_dir, db_path)): # create database
        compoundsPath = os.path.join(current_dir, 'webinaTXTOutputs')
        directory_contents = os.listdir(compoundsPath)
        compoundNames = sorted([os.path.splitext(entry)[0] for entry in directory_contents 
                                            if os.path.isfile(os.path.join(compoundsPath, entry)) and entry.endswith('.txt')])
        for compound in compoundNames:
            affinity = extract_mode_1_affinity(os.path.join(compoundsPath, compound+'.txt'))
            if affinity is not None and isinstance(float(affinity), float):
                insert_into_database(db_path, compound, float(affinity))
            else:
                print(f"Failed to extract or insert data for {compound}.")
    elif not os.path.exists(os.path.join(current_dir, excel_path)): # produce excel
        conn = sqlite3.connect(db_path)
        query = "SELECT compound_name, mode_1_affinity FROM affinities"  
        df = pd.read_sql_query(query, conn)
        conn.close()
        df.to_excel(excel_path, index=False, engine='openpyxl')
    else:
        print("executing queries")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        query = "SELECT compound_name, mode_1_affinity FROM affinities ORDER BY mode_1_affinity ASC LIMIT 1"  
        cursor.execute(query)
        greatest_compound = cursor.fetchone()
        if greatest_compound:
            print(f"Compound with greatest affinity: {greatest_compound[0]}, Affinity: {greatest_compound[1]}")
        else:
            print("No data found.")
        conn.close()
        

except Exception as e:
    print(f"{e}")

"""
Notes:

import sqlite3
allows you to work with SQLite databases from Python


conn = sqlite3.connect('example.db')

create a new database or connect to an existing one by 
specifying a file path. If the file doesn't exist, 
SQLite will create it.


cursor = conn.cursor()
A cursor allows you to execute SQL queries on a database.

cursor.execute('''CREATE TABLE users
               (id INTEGER PRIMARY KEY, name TEXT, email TEXT)''')
cursor.execute("INSERT INTO users (name, email) VALUES ('John Doe', 'john@example.com')")


cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.commit()
conn.close()

After you've made changes to the database (like inserting, 
updating, or deleting data), you need to commit those changes. 
Finally, close the connection to the database when you're done.
"""