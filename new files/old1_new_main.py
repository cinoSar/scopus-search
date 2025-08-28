import pybliometrics as pybl
from pybliometrics.scopus import ScopusSearch
import itertools
import pandas as pd

pybl.init()

# Note: These words must be updated
# Define concepts with synonyms
concepts = {
    "hubs": ["logistic hub", "logistics centre", "logistics center", "integrated logistic centre", "integrated ",
             "logistic center"],
    "analysis": ["impact", "CBA", "BCA", "cost-benefit", "benefit-cost", "spatial", "socio-economic"],
    "spatial": ["urban economics", "spatial economics", "GIS", "NEG", "New Economic Geography", "agglomeration"],
    "econometrics": ["spatial models", "difference-in-differences", "DiD", "DID"],
    "ESG": ["indicators", "environmental", "social", "governance"]
}

def build_queries(concepts):
    """
    Generate Cartesian product (one keyword from each concept group in the dictionary)

    :param concepts:
    :return queries combinations joined by the AND boolean:
    """
    combos = itertools.product(*concepts.values())

    queries = []
    for combo in combos:
        # Each concept has OR synonyms, but combo picks one per group
        query = " AND ".join([f'"{term}"' for term in combo])
        queries.append(query)
    return queries

queries = build_queries(concepts)
for q in queries[:5]:
    print(q)

results = []
for q in queries[:5]:
    s = ScopusSearch(q, subscriber=True)
    for item in s.results or []:
        results.append({
            "eid": item.eid,
            "title": item.title,
            "authors": item.author_names,
            "year": item.coverDate.split("-")[0],
            "doi": item.doi,
            "source": item.publicationName
        })

df = pd.DataFrame(results)
df.to_csv("identification_results.csv", index=False)
