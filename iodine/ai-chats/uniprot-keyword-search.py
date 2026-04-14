import requests

def find_species_by_function(keyword="Apoptosis", limit=10):
    url = "https://rest.uniprot.org/uniprotkb/search"
    params = {
        "query": f"keyword:{keyword}", # You can also use 'function:xxx' or 'go:0006915'
        "format": "json",
        "fields": "accession,gene_names,organism_name,organism_id,comment(FUNCTION)",
        "size": limit
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        results = []
        for entry in data.get('results', []):
            results.append({
                "species": entry['organism']['scientificName'],
                "gene": entry.get('genes', [{}])[0].get('geneName', {}).get('value', 'N/A'),
                "function": entry.get('comments', [{}])[0].get('texts', [{}])[0].get('value', 'No description')
            })
        return results
    return f"Error: {response.status_code}"

# Example: Find 5 species sequenced with genes related to "Bioluminescence"
matches = find_species_by_function("Bioluminescence", 5)
for m in matches:
    print(f"[{m['species']}] Gene: {m['gene']} | Function: {m['function'][:100]}...")
