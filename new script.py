from pybliometrics.scopus import ScopusSearch, exception
from itertools import combinations
from pybliometrics.scopus import ScopusSearch
from pybliometrics.scopus import exception
from pybliometrics.scopus import init
from combinations import unique_combinations
import pandas as pd

# Function to process the tuples and return concatenated strings with a boolean operator
def process_tuples_with_operator(keywords, tuple_oper="OR", word_oper="AND", combination_num=2):
    result_list = []
    unique_combs = list(combinations(keywords, combination_num))

    # Loop through each tuple in the list
    for tuple_pair in unique_combs:
        local_string = " {} ".format(tuple_oper).join(
            " {} ".format(word_oper).join(word.split()) for word in tuple_pair
        )
        result_list.append(local_string)

    return result_list

# Fetch Scopus results based on search strings
def fetch_scopus_results(base_string, strings, min_res, max_res):
    dataframes_list = []
    for result in strings:
        search_string = f"{base_string} TITLE-ABS-KEY( {result} )"
        print(f"Generated Search String: {search_string}")

        try:
            s = ScopusSearch(search_string, verbose=True, download=False)
            result_size = s.get_results_size()
            print(f"The number of results for search string '{search_string}' is: {result_size}")

            if min_res <= result_size <= max_res:
                # Download results and store them in a dataframe
                s = ScopusSearch(search_string, verbose=True, download=True)
                df = pd.DataFrame(s.results)
                dataframes_list.append(df)
        except exception.Scopus401Error as e:
            print(f"Scopus401Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    return dataframes_list

# Find intersection of EIDs
def find_intersection(dataframes):
    if len(dataframes) < 2:
        print("Not enough dataframes to find intersections.")
        return None

    intersection = dataframes[0][['eid']]
    for df in dataframes[1:]:
        intersection = pd.merge(intersection, df[['eid']], on='eid', suffixes=('_x', '_y'))

    return intersection

# Main execution
scopus_string = 'TITLE-ABS-KEY( "energy project" ) AND '
tuple_operator = "OR"
word_operator = "AND"
combination_number = 2
min_results = 200
max_results = 1000

key_list = [
    "economic analysis", "energy policy", "techno-economic assessment", "cost-benefit analysis",
    "investment", "wind power", "economic assessment", "biogas", "methane", "tidal power",
    "gas emissions", "renewable energy sources"
]

search_strings = process_tuples_with_operator(key_list, tuple_operator, word_operator, combination_number)
dataframes = fetch_scopus_results(scopus_string, search_strings, min_results, max_results)

init()
if dataframes:
    intersection_df = find_intersection(dataframes)
    if intersection_df is not None and not intersection_df.empty:
        print(f"Found intersection: {len(intersection_df)} records")
        print(intersection_df.describe())
    else:
        print("No intersection found.")
else:
    print("No dataframes were created.")
