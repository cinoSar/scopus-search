import itertools
import pandas as pd
import pybliometrics
from pybliometrics.scopus import ScopusSearch

pybliometrics.init()

def build_queries(concepts, mode="structured", filters=None):
    """
    Build queries from a concepts dictionary.

    mode = "structured"   -> one query with OR inside groups, AND between groups
    mode = "combinations" -> list of queries, one for each Cartesian combination

    filters = list of additional constraints, e.g.
              ['PUBYEAR > 2015', '(LIMIT-TO(DOCTYPE, "ar"))', '(LIMIT-TO(LANGUAGE, "English"))']
    """
    if mode == "structured":
        groups = []
        for terms in concepts.values():
            group = " OR ".join([f'TITLE-ABS-KEY("{term}")' for term in terms])
            groups.append(f"({group})")
        query = " AND ".join(groups)
    elif mode == "combinations":
        combos = itertools.product(*concepts.values())
        queries = []
        for combo in combos:
            group = " AND ".join([f'TITLE-ABS-KEY("{term}")' for term in combo])
            queries.append(group)
        return [f"{q} AND {' AND '.join(filters)}" for q in queries] if filters else queries
    else:
        raise ValueError("mode must be 'structured' or 'combinations'")

    # Add filters if structured
    if filters:
        query = f"{query} AND {' AND '.join(filters)}"
    return [query]


def fetch_results(queries, max_results=None):
    """
    Run queries with pybliometrics ScopusSearch and collect results.

    - queries: list of complete queries (with TITLE-ABS-KEY + filters)
    - max_results: stop after this many records per query
    """
    all_results = []

    for q in queries:
        print(f"Running query:\n{q}\n")

        search = ScopusSearch(q, subscriber=True)

        for i, item in enumerate(search.results or []):
            if max_results and i >= max_results:
                break
            all_results.append({
                "eid": item.eid,
                "title": item.title,
                "authors": item.author_names,
                "year": item.coverDate.split("-")[0] if item.coverDate else None,
                "doi": item.doi,
                "source": item.publicationName,
                "query": q
            })

    return pd.DataFrame(all_results)



# --- Example Usage ---
if __name__ == "__main__":
    concepts = {
        "hubs": [
            "logistic hub",
            "logistics centre",
            "logistics center",
            "integrated logistic centre",
            "integrated ",
            "logistic center"
        ],

        "analysis": [
            "impact",
             "CBA",
             "BCA",
             "cost-benefit",
             "benefit-cost",
             "spatial",
             "socio-economic"
        ],

        "spatial": [
            "urban economics",
            "spatial economics",
            "GIS",
            "NEG",
            "New Economic Geography",
            "agglomeration"
        ],

        "econometrics": [
            "spatial models",
            "difference-in-differences",
            "DiD",
            "DID"
        ],

        "ESG": [
            "indicators",
            "environmental",
            "social",
            "governance"
        ]
    }

    filters = [
        "PUBYEAR > 2013",
        "PUBYEAR < 2026",
        '(LIMIT-TO(PUBSTAGE, "final"))',
        '(LIMIT-TO(DOCTYPE, "ar"))',
        '(LIMIT-TO(LANGUAGE, "English"))',
        '(EXCLUDE(SUBJAREA, "IMMU") OR EXCLUDE(SUBJAREA, "BIOC") OR EXCLUDE(SUBJAREA, "MULT") '
        'OR EXCLUDE(SUBJAREA, "MEDI") OR EXCLUDE(SUBJAREA, "CHEM") OR EXCLUDE(SUBJAREA, "CENG") '
        'OR EXCLUDE(SUBJAREA, "MATE") OR EXCLUDE(SUBJAREA, "AGRI") OR EXCLUDE(SUBJAREA, "PHYS") '
        'OR EXCLUDE(SUBJAREA, "MATH") OR EXCLUDE(SUBJAREA, "EART") OR EXCLUDE(SUBJAREA, "COMP"))'
    ]

    queries = build_queries(concepts, mode="structured", filters=filters)

    # df = fetch_results(queries, max_results=50) # Limited to 50 results for testing
    df= fetch_results(queries)
    df.to_csv("scopus_filtered_results.csv", index=False)
    print(f"\nCollected {len(df)} records")
