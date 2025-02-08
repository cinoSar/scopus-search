import itertools
import pybliometrics
from pybliometrics.scopus import ScopusSearch

pybliometrics.scopus.init()
def unique_combinations(keywords, combination_number):
    # Generates unique combinations of the specified size
    return itertools.combinations(keywords, combination_number)


def process_tuples_with_operator(keywords, tuple_operator="AND", word_operator="AND", combination_number=2):
    result_list = []
    unique_combs = list(unique_combinations(keywords, combination_number))

    # Loop through each tuple in the list
    for tuple_pair in unique_combs:
        # Initialize a local string for each tuple
        local_string = ""

        # Loop through each element in the tuple and concatenate them with the tuple operator
        for index, element in enumerate(tuple_pair):
            # Split the element into words and rejoin with the word operator
            words = element.split()
            processed_element = f" {word_operator} ".join(words)

            if index > 0:
                local_string += f" {tuple_operator} "
            local_string += processed_element

        # Append the local string to the result list
        result_list.append(local_string)

    return result_list


# Example usage
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
tuple_operator = "AND"
word_operator = "AND"
combination_number = 1

result_list = process_tuples_with_operator(key_list, tuple_operator, word_operator, combination_number)

print("Generated Search Strings:")
print(result_list)
print(list(enumerate(result_list)))

# Print the resulting concatenated strings
for i, result in enumerate(result_list):
    print(result)
    search_string = f"TITLE-ABS-KEY( {result} )"
    print(f"Generated Search String: {search_string}")
    print(type(search_string))

    s = ScopusSearch(search_string, verbose=True, download=False)
    print(f"The number of results for search string '{search_string}' is: * {s.get_results_size()} *")

# Manually constructed string
b = 'TITLE-ABS-KEY( "energy project" ) AND TITLE-ABS-KEY( economic AND analysis )'
s = ScopusSearch(b, verbose=True, download=False)
print(f"TEST NUMBER IS {s.get_results_size()}")
