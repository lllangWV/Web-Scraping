from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
import time

import numpy as np

service =Service(executable_path="Z:\side_projects\Web Scraping\chromedriver.exe")
driver = webdriver.Chrome(service=service)



driver.get("https://www.cryst.ehu.es/cryst/commonsuper.html")


# Fill in the text inputs

spg_1 = 213
z_1 = 2
spg_2 = 214
z_2 = 2
k_index=str(16)

driver.find_element(By.NAME, 'G1').send_keys(str(spg_1))  # Example value for G1
driver.find_element(By.NAME, 'ZG1').send_keys(str(z_1))   # Example value for Z1
driver.find_element(By.NAME, 'G2').send_keys(str(spg_2))  # Example value for G2
driver.find_element(By.NAME, 'ZG2').send_keys(str(z_2))  # Example value for Z2


# Select an option from the dropdown for maxik
select_maxik = Select(driver.find_element(By.NAME, 'maxik'))
select_maxik.select_by_value(str(k_index))  # Example value, choose as needed


# Submit the form
driver.find_element(By.NAME, 'submit').click()



#################################################################################################################################
# Select the specific table
table = driver.find_element(By.CSS_SELECTOR, 'table[border="0"][cellpadding="3"]')

# Initialize a list to store all rows' data
all_rows_data = []

# Extract the rows, skipping the header row
rows = table.find_elements(By.TAG_NAME, 'tr')[1:]  # Assuming first row is the header

for row in rows:
    cols = row.find_elements(By.TAG_NAME, 'td')
    if len(cols) > 12:  # Ensure there are enough columns in the row to avoid index errors
        row_data = {
            'N': cols[0].text,
            'HM Symbol': cols[1].text,
            'PG': cols[2].text,
            'ZG': cols[3].text,
            'ITA': cols[4].text,
            'i1': cols[5].text,
            'it1': cols[6].text,
            'ik1': cols[7].text,
            'i2': cols[8].text,
            'it2': cols[9].text,
            'ik2': cols[10].text,
            'G > H1': cols[11].find_element(By.TAG_NAME, 'a').get_attribute('href') if cols[11].find_elements(By.TAG_NAME, 'a') else '',
            'G > H2': cols[12].find_element(By.TAG_NAME, 'a').get_attribute('href') if cols[12].find_elements(By.TAG_NAME, 'a') else ''
        }
        all_rows_data.append(row_data)
        
# Optionally, print out or process the collected data
for data in all_rows_data:
    print(data)

#################################################################################################################################

def get_supergroup_info(webpage):
    # Load the webpage (assuming local HTML or reachable URL)
    driver.get(webpage)

    # # Use CSS selector to find the outer table with the specified attributes
    # outer_table = driver.find_element(By.CSS_SELECTOR, 'table[width="100%"][cellpadding="0"][cellspacing="6"]')

    # From the located outer table, find the nested table with border=""
    nested_table = driver.find_element(By.CSS_SELECTOR, 'table[border=""]')

    results = []
    for i_row,row in enumerate(nested_table.find_elements(By.TAG_NAME, "tr")[1:]):

        for i_col,column in enumerate(row.find_elements(By.XPATH, "td")):

            if i_col==0:
                supergroup_number = column.text.strip()
            elif i_col==1:
                transformation_matrix=np.zeros(shape=(3,3))
                initial_vector=np.zeros(shape=(3))
                raw_transformation_matrix_rows = column.text.strip().split("\n")
                for i_transform_row,transformation_row in enumerate(raw_transformation_matrix_rows):
                    raw_numbers=transformation_row.replace("[","").replace("]","").split()
                    raw_numbers=[float(number) for number in raw_numbers]
                    transformation_matrix[i_transform_row,:]=raw_numbers[:3]
                    initial_vector[i_transform_row]=raw_numbers[3]

            elif i_col==2:
                coset_representatives = column.text.strip().split('\n')
      
 
        row_dict = {
            "Supergroup number": supergroup_number,
            "Transformation matrix": transformation_matrix,
            "Initial vector": initial_vector,
            "Coset representatives": coset_representatives
        }
        results.append(row_dict)

        return results

# Iterate through each entry and navigate to the URLs stored in 'G > H1' and 'G > H2'
for entry in all_rows_data[:1]:
    if entry['G > H1']:

        supergroup_info=get_supergroup_info(webpage=entry['G > H1'])
        
        print(f"Visited {entry['G > H1']}")
        print(supergroup_info)
        # Optionally perform actions here
        time.sleep(2)  # Wait for 2 seconds
        
    # if entry['G > H2']:
    #     driver.get(entry['G > H2'])
    #     print(f"Visited {entry['G > H2']}")
    #     # Optionally perform actions here
    #     time.sleep(2)  # Wait for 2 seconds


# time.sleep(10)

driver.quit()

# link = driver.find_element_by_link_text("Python Programming")
# link.click()
