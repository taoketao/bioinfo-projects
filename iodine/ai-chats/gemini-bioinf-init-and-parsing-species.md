2/22/2026



<prompt>
Please point me to public internet resources, or downloadable datasets that can be scripted over and filtered, that provide:
a json-document-like table of species whose genes and genomes have been sequenced -> for each gene or genone sequenced, lists the discovered purpose and results of sequencing.

Next: I'm probably unclear at what exactly I'm looking for. Provide follow-up directions so I can direct you better .
</prompt>
<response>

</response>
Finding a single "json-document-like table" that combines every sequenced species with the specific "purpose and results" of its sequencing is a bit like looking for a library catalog that also contains a summary of every experiment ever done on every book.

However, you can get very close by using **NCBI Datasets** and **UniProt**, which provide the programmatic (JSON) access you need to script and filter this data.

### 1. The "List of Everything" (NCBI Datasets)

The **NCBI (National Center for Biotechnology Information)** is the primary global repository. Their "Datasets" tool provides metadata for genomes and genes in **JSON Lines (jsonl)** format, which is perfect for scripting.

* **What it gives you:** A list of all sequenced organisms (Taxonomy), their genome assemblies, and the associated gene metadata.
* **The "Results":** Look at the `assembly_stats` and `checkm_results` within the JSON to see the quality/completeness (the technical "result" of sequencing).
* **How to get it:** Use the [NCBI Datasets Command Line Tool](https://www.ncbi.nlm.nih.gov/datasets/docs/v2/download-and-install/).
```bash
# Example: Get a JSON summary of all primate genomes
datasets summary genome taxon primates --format jsonl > primates.json

```



### 2. The "Purpose and Function" (UniProt KB)

While NCBI tells you *what* was sequenced, **UniProt** tells you *why it matters* (functional annotation). It translates the genetic code into "Discovered Purpose" (Function, Pathways, and Subcellular Location).

* **What it gives you:** Detailed functional summaries for genes/proteins across thousands of species.
* **How to get it:** Use the [UniProt REST API](https://www.uniprot.org/help/api_queries). You can request specific fields like `comment(FUNCTION)` or `go` (Gene Ontology) in JSON format.
```text
https://rest.uniprot.org/uniprotkb/search?query=organism_id:9606&format=json&fields=accession,gene_names,comment(FUNCTION)

```



### 3. Comprehensive Multi-Species Data (Ensembl BioMart)

If you want to build a custom table across many species at once, **Ensembl BioMart** is the standard researcher tool.

* **Link:** [Ensembl BioMart](https://www.ensembl.org/biomart/)
* **Method:** You can select a "Dataset" (e.g., *Ensembl Genes*), then use "Attributes" to select the gene name, the description (the purpose), and "Study" or "Sequence" information.
* **Export:** It allows for CSV/TSV, which can be easily converted to JSON for your scripts.

---

### How to direct me better:

To narrow this down, I need to know which "layer" of biology you are actually interested in:

1. **The Metadata Layer:** Are you looking for the *scientific justification* for the sequencing? (e.g., "This genome was sequenced to study drought resistance in rice.")
* *Direction:* Ask for **SRA (Sequence Read Archive) study metadata** or **BioProject summaries**.


2. **The Functional Layer:** Are you looking for what the *genes actually do*? (e.g., "Gene X controls insulin production.")
* *Direction:* Ask for **Gene Ontology (GO) mappings** or **Functional Annotations**.


3. **The Taxonomic Breadth:** Do you want *every* bacteria and virus (millions), or just high-quality reference genomes (thousands)?
* *Direction:* Specify if you want **RefSeq** (curated) or **GenBank** (everything).



**Would you like me to write a Python script that pulls a sample of this data from the NCBI or UniProt API for a specific group of species?**
<prompt>
Good. I'm looking at higher-level right now. I don't need extensive information on each sequenced gene/genome (eg. why it was sequenced) as much as I need a thorough list. It doesn't need to be complete, and NCBI works well enough. 
For NCBI, how would I go about getting a list of sequenced genes/genomes, and what kinds of filters and args can i provide over api? Python 3 preferred.
</prompt>
<response>
To get a thorough, scriptable list of sequenced genomes/genes from NCBI, the modern standard is the **NCBI Datasets API (v2)**.

While there was a dedicated `ncbi-datasets-pylib` library, it is currently being deprecated in favor of direct REST API calls or their CLI tool. For a Python 3 project, using the `requests` library to hit their REST endpoints is the most stable and flexible method.

### 1. Key API Endpoints

You will primarily use the **Genome** and **Gene** summary endpoints. These return **JSON Lines (.jsonl)**, which is the "document-like" format you requested.

| Feature | Endpoint (Base: `https://api.ncbi.nlm.nih.gov/datasets/v2`) |
| --- | --- |
| **Genome List** | `/genome/taxon/{taxon}/dataset_report` |
| **Gene List** | `/gene/taxon/{taxon}/dataset_report` |
| **By Accession** | `/genome/accession/{accessions}/dataset_report` |

### 2. Useful Filters and Arguments

When querying these endpoints, you can pass several parameters to narrow your "thorough list":

* **`filters.assembly_source`**: Use `refseq` for curated, high-quality data, or `genbank` for everything.
* **`filters.assembly_level`**: Filter by completeness (`complete_genome`, `chromosome`, `scaffold`, `contig`).
* **`filters.reference_only`**: (Boolean) If true, returns only the single "best" reference genome for a species.
* **`filters.has_annotation`**: (Boolean) Ensures the genome actually has identified genes attached to it.
* **`page_size`**: Limit the number of records per request (default is often 20, max is usually 1000).

---

### 3. Python 3 Implementation

Here is a robust way to fetch a list of sequenced genomes for a specific group (e.g., "mammals" or a specific genus) and filter the results.

```python
import requests
import json

def get_ncbi_genomes(taxon="mammals", limit=10):
    # API URL for genome summaries by taxon
    url = f"https://api.ncbi.nlm.nih.gov/datasets/v2/genome/taxon/{taxon}/dataset_report"
    
    # Query parameters (filters)
    params = {
        "filters.assembly_source": "refseq",        # Only curated NCBI data
        "filters.assembly_level": "complete_genome", # Only high-quality full sequences
        "page_size": limit
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        # The API returns 'JSON Lines' - one JSON object per line
        results = []
        for line in response.text.strip().split('\n'):
            results.append(json.loads(line))
        return results
    else:
        print(f"Error: {response.status_code}")
        return None

# Example: Get 5 high-quality mammal genomes
mammals = get_ncbi_genomes("mammals", 5)

for record in mammals:
    # Digging into the JSON structure
    assembly = record.get('assembly', {})
    organism = record.get('organism', {})
    
    print(f"Species: {organism.get('sci_name')}")
    print(f"Accession: {assembly.get('assembly_accession')}")
    print(f"Release Date: {assembly.get('submission_date')}")
    print("-" * 30)

```

### 4. Directing Your Next Steps

To give you the exact script or dataset link you need, could you clarify:

* **Scope:** Do you want a list of *all* sequenced species (which is massive), or are you targeting a specific kingdom (e.g., Viruses, Bacteria, Fungi)?
* **Depth:** For the "results" part of your request—are you looking for the **physical properties** (genome size, GC content) or the **publication links** (the paper that explains why they did it)?
* **Format Preference:** Would you prefer a pre-generated CSV/TSV table from NCBI's FTP servers, or do you definitely want to build a live-querying Python tool?

**Would you like me to adapt the script above to fetch the "Gene" level data instead, including the functional descriptions of what those genes do?**
</response>
<prompt>
Responding to point 4. Certainly, I have kingdom preferences. While I have preferences across kingdoms too, those can be combined/unioned by hand. Rather, I'm looking for what information has been gathered about a specific type of gene and finding species that have been sequenced for that gene or protein function -- the function, or keyword, is the unifying factor.
</prompt>
<response>
To search by **function** or **keyword** and generate a list of species, you are essentially performing a "reverse search": starting with a biological trait and finding all organisms that have a sequenced gene associated with it.

For this specific task, **UniProt** is actually more powerful than NCBI Datasets because it uses a controlled vocabulary (**Keywords** and **Gene Ontology**) to link functions directly to species.

### 1. UniProt Approach (Recommended)

UniProt's API allows you to query by a function keyword (e.g., "Apoptosis" or "DNA repair") and return a "document-like" JSON list of all matching proteins and their parent organisms.

* **API URL:** `https://rest.uniprot.org/uniprotkb/search`
* **Key Argument:** `query=keyword:"KW-####"` (or a simple string like `query=function:"insulin secretion"`)
* **Filter:** `format=json` and `fields=organism_name,organism_id,gene_names,comment(FUNCTION)`

**Python Script for Keyword Search:**

```python
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

```

---

### 2. NCBI Approach (Legacy E-utilities)

NCBI’s newer "Datasets" API is great for bulk data, but for keyword-based "discovery," you should use the older **Entrez E-utilities** (`esearch`). This allows you to search the `gene` database using functional tags.

* **Logic:** `esearch` to find Gene IDs matching a keyword  `esummary` to get the species names for those IDs.
* **API Filter Example:** `term=bioluminescence[gene/protein name] AND has_seq[prop]`

**Scripting Logic:**

1. **Search:** `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gene&term=apoptosis[go]&retmode=json`
2. **Summary:** Use the IDs from Step 1 to call `esummary` and get a JSON list of the organisms.

---

### 3. Comparison of Filters

If you want to script this effectively, here is how you should structure your queries based on what you are looking for:

| If you want... | Use this Filter (UniProt) | Use this Filter (NCBI Gene) |
| --- | --- | --- |
| **Broad Keyword** | `keyword:KW-0067` (Stress response) | `stress response[Text Word]` |
| **Exact Function** | `go:0006915` (Apoptosis) | `0006915[go]` |
| **Enzyme Class** | `ec:1.1.1.1` | `EC 1.1.1.1[Description]` |
| **High Quality** | `reviewed:true` (Swiss-Prot) | `srcdb_refseq[Properties]` |

### Next Step for me:

Would you like me to provide a **curated list of "Keyword IDs"** (like the `KW-####` codes for UniProt) for the specific biological functions you are interested in so your script hits the most accurate data?
</response>
<prompt>
Reverse search is the promising strategy. If uniprot works well for that, then let's go with that. Please report the API reference that is accessed by the script you provided "Python Script for Keyword Search:".

Also, please if possible, provide a reference to an interactable phylogenetic tree where "taxonomic sequencing density" is estimated: ie, "primate" group is closer to 100% than "SAR supergroup".
</prompt>
<response>
### 1. UniProt API Reference

The "Python Script for Keyword Search" provided in the previous turn utilizes the **UniProtKB Search Endpoint**.

* **Base URL:** `https://rest.uniprot.org/uniprotkb/search`
* **Documentation:** [UniProt API Documentation - Retrieving entries via queries](https://www.uniprot.org/help/api_queries)
* **Field References:** * **Query Fields:** See [UniProtKB Query Fields](https://www.uniprot.org/help/query-fields) for arguments like `keyword:`, `go:`, `taxonomy_name:`, and `function:`.
* **Return Fields:** See [UniProtKB Return Fields](https://www.uniprot.org/help/return_fields) for the `fields=` parameter (e.g., `accession`, `organism_name`, `comment(FUNCTION)`).



**Pro-Tip for Scripting:** The UniProt website has a "Generate URL for API" feature. If you use the [Advanced Search](https://www.google.com/search?q=https://www.uniprot.org/uniprotkb/advanced-search) on the web UI to build your perfect filter visually, you can click the **"Download"** button and select **"Generate URL for API"** to get the exact string for your Python `requests` call.

---

### 2. Taxonomic Sequencing Density

Finding a single "100%" number is tricky because the denominator (total existing species) is an estimate, while the numerator (sequenced species) is concrete. However, there are two excellent interactive resources that visualize this "gap":

#### A. The Earth BioGenome Project (EBP) - "The Moonshot"

The EBP is the global effort to sequence all eukaryotic life. Their tracking data is the gold standard for "sequencing density."

* **Resource:** [EBP Progress Tracker / Genomes on a Tree (GoaT)](https://goat.genomehubs.org/)
* **Why it works for you:** GoaT allows you to query specific clades (e.g., "Primate" vs. "SAR") and see the percentage of families or genera that have a "Reference Quality" genome.
* **Density Metric:** It often uses the "Goal" of sequencing one representative per Family, then Genus, then Species. You will see that **Mammals** (specifically Primates) have very high coverage at the Family level, while **SAR (Stramenopiles, Alveolates, and Rhizaria)** has massive "dark matter" (unsequenced clades).

#### B. OneZoom Tree of Life Explorer

This is the most "interactable" phylogenetic tree available. It maps the entire tree of life in a fractal, zoomable interface.

* **Resource:** [OneZoom.org](http://www.onezoom.org/)
* **How to see density:** Look for the **leaf colors**. OneZoom typically colors leaves based on their conservation status or the availability of genetic data.
* **The Visualization:** You can literally "zoom out" from Humans to see a lush, green, well-documented branch of Primates, then pan over to the massive, thin, grayed-out branches of the SAR supergroup where sequencing data is scarce.

### Summary Table: Sequencing Density Estimates

| Clade | Family-Level Coverage | Why? |
| --- | --- | --- |
| **Primates** | ~95%+ | High biomedical interest; small number of species (~500). |
| **Mammals** | ~85% | Flagship species for conservation and research. |
| **SAR Supergroup** | <5% | Massive microbial diversity; many "unculturable" species; less funding. |

**Would you like me to help you formulate a "GoaT" query (Genomes on a Tree) to get the specific "count of sequenced species vs. total species" for a list of clades?**
</response>
<prompt>
</prompt>
<response>
</response>
<prompt>
</prompt>
<response>
</response>
<prompt>
</prompt>
<response>
</response>
<prompt>
</prompt>
<response>
</response>
<prompt>
</prompt>
<response>
</response>
<prompt>
</prompt>
<response>
</response>
