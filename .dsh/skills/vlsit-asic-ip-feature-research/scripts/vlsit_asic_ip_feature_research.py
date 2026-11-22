#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_asic_ip_feature_research.py
# Function : register approved research documents and audit source thresholds and file integrity
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Create and audit a source bundle for application-specific integrated circuit
(ASIC) intellectual-property and system-on-chip (SoC) feature research.

Actions:
  init      create a manifest and source directory without replacing files
  download  download one user-approved, directly accessible document
  register  copy one user-approved local document into the source bundle
  inventory list the documents in a user folder (read-only) and whether they are registered
  check     audit qualifying counts, unique keys, file presence and hashes

Acquisition timestamps use Coordinated Universal Time (UTC).

Exit codes: 0 complete/mechanical check passed, 1 invalid input or integrity error,
4 source thresholds are not met. This script cannot judge source quality or legal rights.

Standard library only. Text files are read and written as UTF-8. Network access is
used only by the explicit download action; no credentials or cookies are sent.
"""
import argparse
import csv
import hashlib
import re
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

MANIFEST = "vlsit_source_manifest.csv"
SOURCE_DIR = "vlsit_sources"
FIELDS = [
    "category", "source_id", "work_key", "family_key", "title", "authors",
    "year", "publisher", "venue", "doi", "url", "access_basis",
    "license_notice", "peer_reviewed", "full_text", "local_file", "sha256",
    "acquired_utc", "notes",
]
MINIMUM = 10
MAX_BYTES_DEFAULT = 250 * 1024 * 1024


def say_error(message):
    print("ERROR: " + message)
    return 1


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path):
    digest = hashlib.sha256()
    with open(str(path), "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def slug(value, limit=48):
    value = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()
    return (value[:limit].strip("_") or "source")


def normalized(value):
    return re.sub(r"[^a-z0-9]+", " ", (value or "").casefold()).strip()


def manifest_path(directory):
    root = Path(directory).expanduser()
    return root, root / MANIFEST


def action_init(args):
    root, manifest = manifest_path(args.directory)
    if manifest.exists():
        return say_error("manifest already exists: %s" % manifest)
    source_dir = root / SOURCE_DIR
    if source_dir.exists():
        return say_error("source directory already exists: %s" % source_dir)
    try:
        root.mkdir(parents=True, exist_ok=True)
        source_dir.mkdir(parents=True, exist_ok=True)
        with open(str(manifest), "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writeheader()
    except OSError as exc:
        return say_error("cannot initialize evidence bundle: %s" % exc)
    print("OK: initialized %s" % manifest)
    return 0


def read_manifest(path):
    with open(str(path), "r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDS:
            raise ValueError("manifest columns do not match the required schema")
        return list(reader)


def write_manifest(path, rows):
    with open(str(path), "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def validate_common(args):
    if not getattr(args, "approved", False):
        raise ValueError("batch approval is required; pass --approved only after user approval")
    if args.access_basis not in ("open-access", "user-authorized"):
        raise ValueError("access basis must be open-access or user-authorized")
    if args.category == "paper" and args.peer_reviewed != "yes":
        raise ValueError("a paper must be manually qualified as peer-reviewed before registration")
    if args.category == "datasheet" and not args.family_key.strip():
        raise ValueError("datasheets require a distinct product-family key")
    if args.category == "paper" and not (args.doi.strip() or args.work_key.strip()):
        raise ValueError("papers require a DOI or a stable work key for deduplication")


def make_row(args, local_file, digest, original_url):
    category = args.category
    work_key = (args.work_key or args.doi or args.title).strip()
    return {
        "category": category,
        "source_id": "%s_%s_%s" % (category, slug(args.title, 28), digest[:10]),
        "work_key": work_key,
        "family_key": args.family_key.strip(),
        "title": args.title.strip(),
        "authors": args.authors.strip(),
        "year": str(args.year or ""),
        "publisher": args.publisher.strip(),
        "venue": args.venue.strip(),
        "doi": args.doi.strip(),
        "url": original_url.strip(),
        "access_basis": args.access_basis,
        "license_notice": args.license_notice.strip() or "Not stated; review source notice",
        "peer_reviewed": args.peer_reviewed,
        "full_text": args.full_text,
        "local_file": local_file,
        "sha256": digest,
        "acquired_utc": utc_now(),
        "notes": args.notes.strip(),
    }


def append_row(manifest, row):
    if not manifest.is_file():
        raise ValueError("manifest not found; run init first: %s" % manifest)
    rows = read_manifest(manifest)
    if any(item.get("source_id") == row["source_id"] for item in rows):
        raise ValueError("source identifier already exists: %s" % row["source_id"])
    rows.append(row)
    write_manifest(manifest, rows)


def safe_source_name(source_id, title, original_name):
    suffix = Path(original_name).suffix.lower()
    if not re.match(r"^\.[a-z0-9]{1,8}$", suffix):
        suffix = ".bin"
    return "%s_%s%s" % (slug(source_id, 36), slug(title, 36), suffix)


def action_register(args):
    root, manifest = manifest_path(args.directory)
    try:
        validate_common(args)
        source_dir = root / SOURCE_DIR
        if not manifest.is_file() or not source_dir.is_dir():
            raise ValueError("bundle is not initialized; run init first")
        source = Path(args.file).expanduser().resolve(strict=True)
        if not source.is_file():
            raise ValueError("input is not a file")
        digest = sha256_file(source)
        row = make_row(args, "", digest, args.url or "user-provided file")
        filename = safe_source_name(row["source_id"], row["title"], source.name)
        target = source_dir / filename
        if target.exists():
            raise ValueError("destination already exists: %s" % target)
        shutil.copy2(str(source), str(target))
        row["local_file"] = "%s/%s" % (SOURCE_DIR, filename)
        try:
            append_row(manifest, row)
        except Exception:
            target.unlink()
            raise
    except (OSError, ValueError, csv.Error) as exc:
        return say_error(str(exc))
    print("OK: registered %s" % row["source_id"])
    print("FILE: %s" % target)
    return 0


def action_download(args):
    root, manifest = manifest_path(args.directory)
    try:
        validate_common(args)
        parsed = urllib.parse.urlparse(args.url)
        if parsed.scheme not in ("https", "http") or not parsed.netloc:
            raise ValueError("URL must be a direct HTTP or HTTPS document URL")
        source_dir = root / SOURCE_DIR
        if not manifest.is_file() or not source_dir.is_dir():
            raise ValueError("bundle is not initialized; run init first")
        limit = int(args.max_mb * 1024 * 1024)
        if limit <= 0:
            raise ValueError("--max-mb must be greater than zero")
        request = urllib.request.Request(
            args.url,
            headers={"User-Agent": "VLSIT-Research-Bundle/1.0 (direct approved document retrieval)"},
        )
        with urllib.request.urlopen(request, timeout=45) as response:
            final_url = response.geturl()
            final = urllib.parse.urlparse(final_url)
            if final.scheme not in ("https", "http") or not final.netloc:
                raise ValueError("redirected to an unsupported URL")
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > limit:
                raise ValueError("file exceeds --max-mb limit")
            original_name = Path(urllib.parse.unquote(final.path)).name or "document.bin"
            temp = source_dir / (".download_" + str(datetime.now().timestamp()).replace(".", "") + ".tmp")
            digest = hashlib.sha256()
            total = 0
            try:
                with open(str(temp), "wb") as output:
                    while True:
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        total += len(chunk)
                        if total > limit:
                            raise ValueError("file exceeds --max-mb limit")
                        digest.update(chunk)
                        output.write(chunk)
                if total == 0:
                    raise ValueError("downloaded file is empty")
                hex_digest = digest.hexdigest()
                row = make_row(args, "", hex_digest, args.url)
                filename = safe_source_name(row["source_id"], row["title"], original_name)
                target = source_dir / filename
                if target.exists():
                    raise ValueError("destination already exists: %s" % target)
                temp.replace(target)
                row["local_file"] = "%s/%s" % (SOURCE_DIR, filename)
                try:
                    append_row(manifest, row)
                except Exception:
                    target.unlink()
                    raise
            finally:
                if temp.exists():
                    temp.unlink()
    except (OSError, ValueError, urllib.error.URLError, csv.Error) as exc:
        return say_error(str(exc))
    print("OK: downloaded and registered %s" % row["source_id"])
    print("FILE: %s" % target)
    return 0


def action_check(args):
    root, manifest = manifest_path(args.directory)
    if not manifest.is_file():
        return say_error("manifest not found: %s" % manifest)
    errors = []
    product_families = set()
    paper_keys = set()
    hashes = set()
    duplicate_hashes = 0
    try:
        rows = read_manifest(manifest)
    except (OSError, ValueError, csv.Error) as exc:
        return say_error(str(exc))
    for index, row in enumerate(rows, 2):
        label = "row %d" % index
        required = ("category", "source_id", "title", "access_basis", "full_text", "local_file", "sha256")
        missing = [key for key in required if not row.get(key, "").strip()]
        if missing:
            errors.append("%s missing %s" % (label, ", ".join(missing)))
            continue
        if row["category"] not in ("datasheet", "paper"):
            errors.append("%s has unsupported category" % label)
            continue
        if row["access_basis"] not in ("open-access", "user-authorized"):
            errors.append("%s has unsupported access basis" % label)
            continue
        relative = Path(row["local_file"])
        file_path = (root / relative).resolve()
        try:
            file_path.relative_to(root.resolve())
        except ValueError:
            errors.append("%s file path escapes research directory" % label)
            continue
        if not file_path.is_file():
            errors.append("%s local file is missing" % label)
            continue
        actual = sha256_file(file_path)
        if actual.lower() != row["sha256"].lower():
            errors.append("%s SHA-256 mismatch" % label)
            continue
        content_key = (row["category"], actual)
        if content_key in hashes:
            duplicate_hashes += 1
            continue
        hashes.add(content_key)
        if row["full_text"].casefold() != "yes":
            continue
        if row["category"] == "datasheet":
            key = normalized(row.get("family_key", ""))
            if not key:
                errors.append("%s datasheet lacks family_key" % label)
            else:
                product_families.add(key)
        else:
            if row.get("peer_reviewed", "").casefold() != "yes":
                continue
            key = normalized(row.get("doi", "")) or normalized(row.get("work_key", "")) or normalized(row.get("title", ""))
            if key:
                paper_keys.add(key)
            else:
                errors.append("%s peer-reviewed paper lacks DOI/work key" % label)
    if errors:
        print("ERROR: evidence bundle has %d problem(s)" % len(errors))
        for number, error in enumerate(errors[:20], 1):
            print("%d. %s" % (number, error))
        if len(errors) > 20:
            print("... %d additional problem(s)" % (len(errors) - 20))
        return 1
    products = len(product_families)
    papers = len(paper_keys)
    if products < MINIMUM or papers < MINIMUM:
        print("INCOMPLETE: datasheets=%d/%d papers=%d/%d duplicate_file_hashes=%d missing_datasheets=%d missing_papers=%d" %
              (products, MINIMUM, papers, MINIMUM, duplicate_hashes,
               max(0, MINIMUM - products), max(0, MINIMUM - papers)))
        return 4
    print("READY: datasheets=%d papers=%d duplicate_file_hashes=%d" %
          (products, papers, duplicate_hashes))
    print("LIMIT: source quality, relevance, legal rights and report claims require manual review")
    return 0


DOCUMENT_SUFFIXES = {".pdf", ".docx", ".doc", ".html", ".htm", ".md", ".txt", ".epub"}
INVENTORY_LIMIT = 500


def action_inventory(args):
    """Read-only list of the candidate documents of a user folder; copies and writes nothing."""
    folder = Path(args.folder)
    if not folder.is_dir():
        return say_error("folder not found: %s" % folder)
    registered = set()
    if args.bundle:
        _root, manifest = manifest_path(args.bundle)
        if manifest.is_file():
            try:
                registered = {row.get("sha256", "").lower() for row in read_manifest(manifest)}
            except (OSError, ValueError, csv.Error) as exc:
                return say_error(str(exc))
    files = sorted(p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in DOCUMENT_SUFFIXES)
    print("path | size_bytes | sha256 | registered")
    for path in files[:INVENTORY_LIMIT]:
        digest = sha256_file(path)
        print("%s | %d | %s | %s" % (path.relative_to(folder).as_posix(), path.stat().st_size, digest,
                                     "yes" if digest.lower() in registered else "no"))
    if len(files) > INVENTORY_LIMIT:
        print("... %d more file(s) not listed" % (len(files) - INVENTORY_LIMIT))
    pending = sum(1 for p in files[:INVENTORY_LIMIT] if sha256_file(p).lower() not in registered)
    print("INVENTORY: files=%d not_registered=%d (read-only; nothing was copied or written)" % (len(files), pending))
    return 0


def add_source_fields(parser):
    parser.add_argument("directory", help="user-supplied research output directory")
    parser.add_argument("--category", required=True, choices=("datasheet", "paper"))
    parser.add_argument("--title", required=True)
    parser.add_argument("--access-basis", required=True, choices=("open-access", "user-authorized"))
    parser.add_argument("--approved", action="store_true", help="record that the user approved this batch")
    parser.add_argument("--authors", default="")
    parser.add_argument("--year", default="")
    parser.add_argument("--publisher", default="")
    parser.add_argument("--venue", default="")
    parser.add_argument("--doi", default="")
    parser.add_argument("--work-key", default="", help="stable deduplication key when no DOI exists")
    parser.add_argument("--family-key", default="", help="distinct product-family key for a datasheet")
    parser.add_argument("--url", default="")
    parser.add_argument("--license-notice", default="")
    parser.add_argument("--peer-reviewed", default="na", choices=("yes", "no", "na"))
    parser.add_argument("--full-text", default="yes", choices=("yes", "no"))
    parser.add_argument("--notes", default="")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="action", required=True)
    init = sub.add_parser("init", help="create a new empty source bundle")
    init.add_argument("directory")
    download = sub.add_parser("download", help="download one approved direct document URL")
    add_source_fields(download)
    download.add_argument("--max-mb", type=int, default=250)
    register = sub.add_parser("register", help="copy one authorized local source file")
    add_source_fields(register)
    register.add_argument("--file", required=True)
    inventory = sub.add_parser("inventory", help="list the documents of a user folder (read-only)")
    inventory.add_argument("folder", help="folder with the documents the user supplied")
    inventory.add_argument("--bundle", help="research directory whose manifest marks the registered files")
    check = sub.add_parser("check", help="audit source thresholds and file integrity")
    check.add_argument("directory")
    args = parser.parse_args()
    return {"init": action_init, "download": action_download,
            "register": action_register, "inventory": action_inventory,
            "check": action_check}[args.action](args)


if __name__ == "__main__":
    sys.exit(main())
