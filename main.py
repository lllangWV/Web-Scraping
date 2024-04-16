import time

import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service

VERBOSE=False

#################################################################################################################################


def get_supergroup_table(driver, verbose=VERBOSE):
    """
    Extracts data from a table on a webpage 
    (https://www.cryst.ehu.es/cgi-bin/cryst/programs/paths/nph-commonsuper) 
    using a Selenium WebDriver.

    Args:
        driver: The Selenium WebDriver instance.

    Returns:
        A list of dictionaries, where each dictionary represents a row in the table.
        The keys in the dictionary correspond to the column names, and the values
        represent the data in each cell of the row.
    """

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

    for i,entry in enumerate(all_rows_data[:]):
        if verbose:
            print("Processing common supergroups row",i)
            print("-"*200)

        if entry['G > H1']:
            webpage=entry['G > H1']
            entry_name='G > H1 Supergroup Info'  # Name for the entry in the dictionary
            supergroup_info=get_supergroup_info(webpage=webpage,driver=driver)  # Get the supergroup info
            entry[entry_name]=supergroup_info  # Add the supergroup info to the dictionary entry

        if entry['G > H2']:
            webpage=entry['G > H2']
            entry_name='G > H2 Supergroup Info'  # Name for the entry in the dictionary

            supergroup_info=get_supergroup_info(webpage=webpage,driver=driver)  # Get the supergroup info
            entry[entry_name]=supergroup_info  # Add the supergroup info to the dictionary entry
            

    return all_rows_data
        

#################################################################################################################################


def get_supergroup_info(webpage,driver, verbose=VERBOSE):
    """
    Retrieves information about supergroups from a this type of webpage:
    https://www.cryst.ehu.es/cgi-bin/cryst/programs/nph-show_all_super?super=230&sub=213&ind=4&super_nor=en&subgr_nor=en

    Args:
        webpage (str): The URL or local path of the webpage to scrape.
        driver: The webdriver object to use for scraping.

    Returns:
        list: A list of dictionaries, where each dictionary contains the following information for a supergroup:
            - "Supergroup number": The number of the supergroup.
            - "Transformation matrix": The transformation matrix associated with the supergroup.
            - "Initial vector": The initial vector associated with the supergroup.
            - "Coset representatives": The coset representatives associated with the supergroup.
            - "Wyckoff splitting info": The Wyckoff splitting information associated with the supergroup.
    """

    # Load the webpage (assuming local HTML or reachable URL)
    driver.get(webpage)

    # From the located outer table, find the nested table with border=""
    nested_table = driver.find_element(By.CSS_SELECTOR, 'table[border=""]').find_element(By.XPATH, "tbody")

    # Initialize an empty list to store the results
    results = []

    # Iterate through each row in the nested table, skipping the header row
    for i_row, row in enumerate(nested_table.find_elements(By.XPATH, "tr")[1:]): # This find the rows directly under table/tbody
        if verbose:
            print("Procesing row",i_row)
        # Initialize variables to store the data for each row
        supergroup_number = None
        transformation_matrix = np.zeros(shape=(3,3))
        initial_vector = np.zeros(shape=(3))
        coset_representatives = None
        wyckoff_splitting_url = None
        wyckoff_information = None

 
        # Iterate through each column in the row
        # for i_col, column in enumerate(row.find_elements(By.TAG_NAME, "td")):
        for i_col, column in enumerate(row.find_elements(By.XPATH, "td")):
            if verbose:
                print("Processing column",i_col)
            # Extract the supergroup number from the first column
            if i_col == 0:
                supergroup_number = column.text.strip()

            # Extract the transformation matrix and initial vector from the second column
            elif i_col == 1:
                raw_transformation_matrix_rows = column.text.strip().split("\n")
                for i_transform_row, transformation_row in enumerate(raw_transformation_matrix_rows):
                    raw_numbers = transformation_row.replace("[","").replace("]","").split()
                    tmp_list = []
                    for raw_number in raw_numbers:
                        # handles cases where the string is a fraction
                        if "/" in raw_number:
                            numerator, denominator = map(int, raw_number.split('/'))
                            result_number = numerator / denominator
                        else:
                            result_number=raw_number
                        tmp_list.append(float(result_number))

                    raw_numbers = tmp_list
                    transformation_matrix[i_transform_row,:] = raw_numbers[:3]
                    initial_vector[i_transform_row] = raw_numbers[3]

            # Extract the coset representatives from the third column
            elif i_col == 2:
                coset_representatives = column.text.strip().split('\n')

            # Extract the URL for the wyckoff splitting information from the fourth column
            elif i_col == 3:

                wyckoff_splitting_url = column.find_elements(By.TAG_NAME, "a")[0].get_attribute('href')

                # Retrieve the wyckoff splitting information using the provided function
                wyckoff_information = get_wyckoff_splitting_info(webpage=wyckoff_splitting_url,driver=driver)


        # Create a dictionary to store the data for the current row
        row_dict = {
            "Supergroup number": supergroup_number,
            "Transformation matrix": transformation_matrix,
            "Initial vector": initial_vector,
            "Coset representatives": coset_representatives,
            "Wyckoff splitting info": wyckoff_information
        }

        # Append the dictionary to the results list
        results.append(row_dict)

    return results

#################################################################################################################################

def get_wyckoff_splitting_info(webpage,driver, verbose=VERBOSE):
    """
    Retrieves Wyckoff splitting information from a this example webpage 
    https://www.cryst.ehu.es/cgi-bin/cryst/programs/nph-allwpsplit?super=230&sub=213&trmat=x%2Cy%2Cz.

    Args:
        webpage (str): The URL or local file path of the webpage to scrape.
        driver: The webdriver object to use for scraping.

    Returns:
        list: A list of dictionaries containing the Wyckoff splitting information.
              Each dictionary represents a row in the table and contains the following keys:
              - "Wyckoff number": The Wyckoff number.
              - "Wyckoff Group": The Wyckoff group.
              - "Wyckoff Subgroup": The Wyckoff subgroup.

    """

    # Load the webpage (assuming local HTML or reachable URL)
    driver.get(webpage)

    # From the located outer table, find the nested table with border=""
    nested_table = driver.find_element(By.CSS_SELECTOR, 'table[border="5"][width="60%"]').find_element(By.XPATH, "tbody")

    results=[]
    # Iterate through each row in the nested table
    for i_row, row in enumerate(nested_table.find_elements(By.XPATH, "tr")[2:]): # skip first two rows, they are headers

        # Initialize variables to store Wyckoff splitting information
        wyckoff_number = None
        wyckoff_group = None
        wyckoff_subgroup = None

        # Iterate through each column in the row
        for i_col, column in enumerate(row.find_elements(By.XPATH, "td")):
            # Extract Wyckoff number from the first column
            if i_col == 0:
                wyckoff_number = column.text.strip()
            # Extract Wyckoff group from the second column
            elif i_col == 1:
                wyckoff_group = column.text.strip()
            # Extract Wyckoff subgroup from the third column
            elif i_col == 2:
                wyckoff_subgroup = column.text.strip().split()

        # Create a dictionary to store the Wyckoff splitting information for the current row
        row_dict = {
            "Wyckoff number": wyckoff_number,
            "Wyckoff Group": wyckoff_group,
            "Wyckoff Subgroup": wyckoff_subgroup,
        }

        # Append the dictionary to the results list
        results.append(row_dict)

    # Go back to the previous page to continure the loop
    driver.back()

    # Return the list of Wyckoff splitting information
    return results
   
def get_common_supergroups_of_two_spacegroups(spg_1, z_1, spg_2, z_2, k_index, verbose=VERBOSE):
    """
    Retrieves the common supergroups of two spacegroups using web scraping.

    Parameters:
    spg_1 (int): The spacegroup number of the first spacegroup.
    z_1 (int): The Z number of the first spacegroup.
    spg_2 (int): The spacegroup number of the second spacegroup.
    z_2 (int): The Z number of the second spacegroup.
    k_index (int): The index of the maxik option to select.
    verbose (bool): Whether to print verbose output. Default is VERBOSE.

    Returns:
    list: A list of dictionaries containing the data of the common supergroups.

    """
    service = Service(executable_path="Z:\side_projects\Web Scraping\chromedriver.exe")
    driver = webdriver.Chrome(service=service)

    driver.get("https://www.cryst.ehu.es/cryst/commonsuper.html")

    # Fill in the text inputs
    spg_1 = spg_1
    z_1 = z_1
    spg_2 = spg_2
    z_2 = z_2
    k_index = str(k_index)

    driver.find_element(By.NAME, 'G1').send_keys(str(spg_1))  # Example value for G1
    driver.find_element(By.NAME, 'ZG1').send_keys(str(z_1))   # Example value for Z1
    driver.find_element(By.NAME, 'G2').send_keys(str(spg_2))  # Example value for G2
    driver.find_element(By.NAME, 'ZG2').send_keys(str(z_2))  # Example value for Z2

    # Select an option from the dropdown for maxik
    select_maxik = Select(driver.find_element(By.NAME, 'maxik'))
    select_maxik.select_by_value(str(k_index))  # Example value, choose as needed

    # Submit the form
    driver.find_element(By.NAME, 'submit').click()

    try:
        # Get the table data
        all_rows_data = get_supergroup_table(driver=driver, verbose=verbose)
    except Exception as e:
        print("Error:",e)
        # If the table is not found, return an empty list
        all_rows_data = []

    driver.quit()
    return all_rows_data


def main():
    """
    This is the main function that performs the web scraping process.

    It fills in the text inputs, retrieves common supergroups information,
    and prints the results.

    Parameters:
    None

    Returns:
    None
    """
    # Fill in the text inputs
    spg_1 = 213
    z_1 = 1
    spg_2 = 214
    z_2 = 1
    k_index = 1
    start_time = time.time()

    common_supergroups_info = get_common_supergroups_of_two_spacegroups(spg_1, z_1, spg_2, z_2, k_index, verbose=VERBOSE)

    end_time = time.time()
    execution_time = end_time - start_time
    print("-"*200)
    print("Execution time:", execution_time, "seconds")
    print("-"*200)
    for entry in common_supergroups_info:
        print(entry)
        print("-"*200)
        print("\n")
        

if __name__ == "__main__":

    main()
