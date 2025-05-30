import pybliometrics
import pandas as pd
import itertools
from pybliometrics.scopus import ScopusSearch
from pybliometrics.scopus import exception
from combinations import unique_combinations
from datetime import datetime, timedelta
import os


pybliometrics.scopus.init()
pd.reset_option('display.max_columns', None)

scopus_string = f'TITLE-ABS-KEY( "energy project" ) AND '
fields_of_int = 'eid,doi,title,publicationyear,abstract'
tuple_operator = "OR"
word_operator = "AND"
combination_number = 1
min_results = 800
max_results = 1000

key_list = [
     "economic analysis",
     "energy policy",
     "techno-economic assessment",
     "cost-benefit analysis",
     "investment",
     "wind power",
     "economic assessment",
     "biogas",
     "methane",
     "tidal power",
     "gas emissions",
     "renewable energy sources"
]

####################################################################################################


# Function to process the tuples and return concatenated strings with a boolean operator
def process_tuples_with_operator(keywords, tuple_oper="OR", word_oper="AND", combination_num=2):
    result_list = []
    unique_combs = list(unique_combinations(keywords, combination_num))

    # Loop through each tuple in the list
    for tuple_pair in unique_combs:
        # Initialize a local string for each tuple
        local_string = ""

        # Loop through each element in the tuple and concatenate them with the tuple operator
        for index, element in enumerate(tuple_pair):
            # Split the element into words and rejoin with the word operator
            words = element.split()
            processed_element = f" {word_oper} ".join(words)

            if index > 0:
                local_string += f" {tuple_oper} "
            local_string += processed_element

        # Append the local string to the result list
        result_list.append(local_string)

    return result_list

##########################################################################################################


def fetch_scopus_results(base_string, strings, min_res, max_res, fields):
    dataframes_list = []

    for i, result in enumerate(strings):
        search_string = f"{base_string} TITLE-ABS-KEY( {result} )"
        print(f"Generated Search String: {search_string}")

        try:
            s = ScopusSearch(search_string, field=fields, verbose=True, download=False)
            result_size = s.get_results_size()
            print(f"The number of results for search string '{search_string}' is: * {result_size} *")

            if min_res <= result_size <= max_res:
                # Download results and store them in a dataframe
                s = ScopusSearch(search_string, field=fields, verbose=True, download=True)
                df = pd.DataFrame(s.results)
                dataframes_list.append(df)
        except exception.Scopus401Error as e:
            print(f"Scopus401Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    return dataframes_list
############################################################################


def find_intersection(n_dataframes):
    if len(n_dataframes) < 2:
        print("Not enough dataframes to find intersections.")
        return None

    # Assuming we are interested in intersection based on document identifiers like 'eid'
    intersection = n_dataframes[0]['eid']
    print(f"***** CONTROL *****{n_dataframes[0]['eid']}")
    for df in dataframes[1:]:
        intersection_2 = pd.merge(intersection, df[['eid']], on='eid', suffixes=('_x', '_y'))

    return intersection_2
##############################################################################


# todo: Call the functions
search_strings = process_tuples_with_operator(key_list, tuple_operator, word_operator, combination_number)

dataframes = fetch_scopus_results(scopus_string, search_strings, min_results, max_results, fields=fields_of_int)
print(f"THE TYPE OF THE VARIABLE dataframes IS: {type(dataframes)}")
print(len(dataframes))
print(range(len(dataframes)-1))

concat_dataframes = pd.concat(dataframes)
print(concat_dataframes.head())
print(concat_dataframes.info())

duplicated_rows = concat_dataframes[concat_dataframes.duplicated()]
print("Duplicated Rows:")
print(duplicated_rows)
not_duplicated = duplicated_rows.drop_duplicates()

condition_1= not_duplicated['subtype'] != 'ar'
df_filtered = not_duplicated[~condition_1]

df_filtered.loc[:, 'coverDate'] = pd.to_datetime(df_filtered['coverDate'])
print(df_filtered['coverDate'])

five_years_ago = datetime.now() - timedelta(days=365 * 5)
condition_2 = df_filtered['coverDate'] < five_years_ago
df_filtered_2 = df_filtered[~condition_2]


print(df_filtered.info())

df_filtered_2.to_csv("[exPEDite]_lit_review3.csv")
