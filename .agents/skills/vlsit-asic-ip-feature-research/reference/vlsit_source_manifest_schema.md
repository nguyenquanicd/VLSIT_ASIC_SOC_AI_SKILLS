# Source-bundle commands and manifest schema

Run the script with Python 3.8 or later. Examples use `<python>` for the full path printed by the locator. All downloads require `--approved` after the user has approved the candidate batch. The script does not verify legal rights; the researcher must qualify access basis and retain notices.

## Initialize

The parent research directory may already exist, but these bundle paths must be new. The command refuses to overwrite either the manifest or the source folder.

```powershell
<python> "<skill folder>\scripts\vlsit_asic_ip_feature_research.py" init "<research directory>"
```

## Download one direct document

Example for a paper; use `--category datasheet` and `--family-key vendor_product_family` for a product document. The source must be accessible without credentials, and the user must have approved the proposed batch. A Uniform Resource Locator (URL) must use Hypertext Transfer Protocol (HTTP) or Hypertext Transfer Protocol Secure (HTTPS). The maximum-file-size option `--max-mb` defaults to 250.

```powershell
<python> "<skill folder>\scripts\vlsit_asic_ip_feature_research.py" download "<research directory>" --category paper --title "Example paper title" --authors "Author A; Author B" --year 2025 --publisher "Publisher" --venue "Peer-reviewed conference" --doi "10.xxxx/example" --url "https://example.org/paper.pdf" --access-basis open-access --license-notice "CC BY 4.0" --peer-reviewed yes --full-text yes --approved
```

For a datasheet, provide `--family-key` and `--publisher`; peer-review status is not applicable (`na`). For a user-provided authorized document, use `--access-basis user-authorized` with `register` instead of attempting a credentialed download.

## List the documents the user supplied

Read-only: lists every `.pdf`, `.docx`, `.doc`, `.html`, `.htm`, `.md`, `.txt` and `.epub` file below the folder with its size and SHA-256, and with `--bundle` whether a file with the same hash is already registered. It copies nothing and writes nothing.

```powershell
<python> "<skill folder>\scripts\vlsit_asic_ip_feature_research.py" inventory "<folder of user documents>" --bundle "<research directory>"
```

## Register a user-provided document

```powershell
<python> "<skill folder>\scripts\vlsit_asic_ip_feature_research.py" register "<research directory>" --category datasheet --title "Example device datasheet" --publisher "Manufacturer" --year 2025 --family-key "manufacturer_device_family" --file "<authorized local file>" --access-basis user-authorized --peer-reviewed na --full-text yes --approved
```

The user-approved file is copied into `vlsit_sources/`; the input file is left untouched. Existing destination names are never replaced.

## Check the bundle

```powershell
<python> "<skill folder>\scripts\vlsit_asic_ip_feature_research.py" check "<research directory>"
```

The command exits `0` and prints `READY` when there are at least ten unique datasheet family keys and ten unique peer-reviewed paper keys with full-text local files whose hashes match. It exits `4` and prints `INCOMPLETE` when thresholds are short. It exits `1` for missing, invalid or changed files. The result does not validate source quality, legal access, relevance or report claims.

## Manifest columns

`vlsit_source_manifest.csv` is UTF-8 comma-separated text with these columns:

| Column | Use |
|---|---|
| `category` | `datasheet` or `paper` |
| `source_id` | Stable local record identifier |
| `work_key` | Work key used for paper deduplication |
| `family_key` | Distinct product-family key used for datasheets |
| `title`, `authors`, `year` | Citation details |
| `publisher`, `venue`, `doi` | Publisher and digital object identifier (DOI) evidence |
| `url` | Canonical source URL or user-provided-file note |
| `access_basis` | `open-access` or `user-authorized`; this is a recorded assertion, not legal validation |
| `license_notice` | Exact reuse/access notice or `Not stated; review source notice` |
| `peer_reviewed`, `full_text` | Manually qualified `yes`, `no` or `na` status |
| `local_file` | Relative path inside the research directory |
| `sha256` | File-integrity digest |
| `acquired_utc` | Acquisition/registration time in Coordinated Universal Time (UTC) |
| `notes` | Revision, duplicate relation, cited pages or other qualification notes |

Keep a separate feature-evidence matrix in the report or in a user-requested companion file. The source manifest is not the feature-prevalence dataset by itself.
