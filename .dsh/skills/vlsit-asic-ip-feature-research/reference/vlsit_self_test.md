# Evidence-gate self-test cases

Use these cases when changing the manifest checker. The script checks record structure, qualifying counts, unique keys, file existence and SHA-256 integrity. It does not judge a paper's scientific quality, legal access rights, source relevance or report truth.

| Case | Fixture | Expected result |
|---|---|---|
| Empty bundle | No source records | `INCOMPLETE`, exit 4 |
| Nine product families | Nine valid datasheet/databook records | `INCOMPLETE`, product shortfall shown |
| Nine peer-reviewed full texts | Nine valid paper records | `INCOMPLETE`, paper shortfall shown |
| Ten papers, one abstract only | One paper has no full text or local file | Excluded from qualifying count; `INCOMPLETE` if fewer than ten remain |
| Duplicate product family | Two product documents use the same family key | Count one product family; duplicate is reported |
| Duplicate paper | Same digital object identifier or normalized title | Count one paper; duplicate is reported |
| Identical source file | Two records in one category have the same file hash | Count the content once; duplicate is reported |
| Missing local file | Manifest points to a nonexistent source | Error, exit 1 |
| Changed local file | Recorded checksum differs from file bytes | Error, exit 1 |
| Restricted or unknown basis | Access basis is not one of the accepted values | Error, exit 1 |
| Ten plus ten valid records | All thresholds, unique keys, files and hashes valid | `READY`, exit 0 |
| Shortfall report | Seven families and four papers registered | `INCOMPLETE` with `missing_datasheets=3 missing_papers=6`, exit 4 |
| Inventory of user documents | Folder with a PDF, a text file, an image and a registered duplicate | Lists the PDF and the text file, flags the registered one, skips the image, writes nothing |

An implementation change must preserve these outcomes. Temporary fixtures must be created in a fresh temporary directory and removed after the check. Never test against or modify a user's research bundle.
