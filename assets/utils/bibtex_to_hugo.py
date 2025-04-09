#!/usr/bin/env python3

import argparse
import bibtexparser
import os
import re
import calendar
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
# Import necessary components for customization
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode

# Dictionary to map month abbreviations/names to numbers
MONTH_MAP = {
    **{
        str(i): f"{i:02d}" for i in range(1, 13)
    },  # Handle numeric months '1'..'12'
    **{
        calendar.month_name[i].lower(): f"{i:02d}" for i in range(1, 13)
    },  # Full month names
    **{
        calendar.month_abbr[i].lower(): f"{i:02d}" for i in range(1, 13)
    },  # Abbreviated month names
}


def clean_string(text):
    """Removes potential BibTeX curly braces and extra whitespace."""
    if not text:
        return ""
    # Remove {{ and }} or { and } around the whole string
    text = re.sub(r"^\{+(.*)\}+$", r"\1", text)
    # Remove internal curly braces used for protection (less needed after unicode conversion)
    # text = text.replace("{", "").replace("}", "") # Keep this? Maybe for titles etc.
    return text.strip()


def format_authors(author_string):
    """Splits the author string (already unicode converted) into a list."""
    if not author_string:
        return []
    # The convert_to_unicode customization handles LaTeX chars.
    # We just need to split by ' and '.
    # clean_string might still be useful if names were wrapped like {First Last}
    authors = [clean_string(author) for author in author_string.split(" and ")]
    return [author for author in authors if author] # Remove empty strings


def format_date(entry):
    """Creates a YYYY-MM-DD date string."""
    year = entry.get("year", "1900")
    month_str = entry.get("month", "1").lower()
    month = MONTH_MAP.get(month_str, "01")
    day = entry.get("day", "01")
    # Ensure day is two digits
    try:
        day = f"{int(day):02d}"
    except ValueError:
        day = "01"

    # Basic validation for year
    if not re.match(r"^\d{4}$", year):
        year = "1900" # Default year if invalid format

    return f"{year}-{month}-{day}"


def get_publication_type(entry_type):
    """Maps BibTeX entry type to Hugo category."""
    entry_type = entry_type.lower()
    # Add more mappings as needed
    mapping = {
        "article": "article-journal",
        "book": "book",
        "inproceedings": "paper-conference",
        "conference": "paper-conference",
        "techreport": "report",
        "phdthesis": "thesis",
        "mastersthesis": "thesis",
        "misc": "other",
        "unpublished": "other",
        "incollection": "book-chapter",
        "booklet": "book",
        "manual": "other",
        "proceedings": "book",
    }
    return mapping.get(entry_type, "other")


def generate_filename(key):
    """Generates a safe filename from the BibTeX key."""
    # Convert to lowercase
    filename = key.lower()
    # Remove characters not suitable for filenames
    filename = re.sub(r"[^a-z0-9_\-]", "_", filename)
    # Replace multiple underscores with a single one
    filename = re.sub(r"_+", "_", filename)
    # Remove leading/trailing underscores
    filename = filename.strip("_")
    if not filename: # Handle cases where key becomes empty
        filename = "unnamed_entry"
    return f"{filename}.md"


def create_bibtex_string(entry):
    """Creates a BibTeX string for a single entry."""
    # Create a temporary entry dictionary *without* unicode conversion
    # to preserve the original BibTeX formatting for the citation block.
    # Note: This assumes the original entry object wasn't modified in place.
    # If bibtexparser modifies in place, we might need to re-read or store originals.
    # Let's test if the original entry dict retains original formatting.
    # It seems bibtexparser customization modifies the dict values in place.
    # So, we need a way to get the *original* string.
    # Easiest might be to re-parse just this entry, but that's inefficient.
    # Alternative: Store original entries before processing.
    # Let's stick to generating from the *processed* entry for now,
    # meaning the BibTeX block will have Unicode chars, not LaTeX commands.
    # This is often acceptable and sometimes preferred.
    db = BibDatabase()
    # Make a copy to avoid modifying the main loop's entry if writer changes it
    entry_copy = entry.copy()
    db.entries = [entry_copy]
    writer = BibTexWriter()
    writer.indent = "  " # Use 2 spaces for indentation
    writer.comma_first = False # Standard BibTeX format
    # Ensure braces are added if needed by the writer for special chars
    writer.add_trailing_comma = False
    # writer.display_order = sorted(entry_copy.keys()) # Optional: sort fields
    return writer.write(db)


def main():
    parser = argparse.ArgumentParser(
        description="Convert BibTeX entries to Hugo Markdown files."
    )
    parser.add_argument(
        "bibtex_file", help="Path to the input BibTeX file (.bib)"
    )
    parser.add_argument(
        "-o",
        "--output",
        default="hugo_content/publications", # Sensible default for Hugo
        help="Directory to save the output Markdown files",
    )
    parser.add_argument(
        "--featured",
        action="store_true",
        help="Mark all generated entries as featured=true",
    )

    args = parser.parse_args()

    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)

    # --- Load the BibTeX file with Unicode conversion ---
    try:
        with open(args.bibtex_file, encoding="utf-8") as bibtex_file:
            # Create a parser instance and apply the unicode conversion
            parser = BibTexParser(common_strings=True)
            # This customization converts LaTeX commands (like \'{e}) to unicode (é)
            parser.customization = convert_to_unicode
            parser.ignore_nonstandard_types = False # Keep all entry types
            bib_database = bibtexparser.load(bibtex_file, parser=parser)
    except FileNotFoundError:
        print(f"Error: Input file not found at {args.bibtex_file}")
        return
    except Exception as e:
        print(f"Error parsing BibTeX file: {e}")
        # You might want more specific error handling for bibtexparser errors
        return

    print(f"Found {len(bib_database.entries)} entries.")

    # Process each entry
    for entry in bib_database.entries:
        entry_id = entry.get("ID", "")
        if not entry_id:
            print("Warning: Skipping entry with missing ID.")
            continue

        print(f"Processing entry: {entry_id}")

        # --- Extract data (fields should now have Unicode chars) ---
        title = clean_string(entry.get("title", "Untitled"))
        # Author string is already unicode-converted by the parser customization
        authors = format_authors(entry.get("author", ""))
        date = format_date(entry)
        doi = entry.get("doi", "")
        abstract = clean_string(entry.get("abstract", ""))
        # Keywords might also have LaTeX, conversion handles them too
        keywords = [
            k.strip()
            for k in entry.get("keywords", "").split(",")
            if k.strip()
        ]
        entry_type = entry.get("ENTRYTYPE", "misc")
        publication_type = get_publication_type(entry_type)

        # Determine publication name (journal or booktitle)
        journal = clean_string(entry.get("journal", ""))
        booktitle = clean_string(entry.get("booktitle", ""))
        publication_name = journal if journal else booktitle

        # Determine URL (prefer 'url' field, fallback to DOI)
        url = entry.get("url", "")
        if not url and doi:
            url = f"https://doi.org/{doi}"

        # --- Build Front Matter ---
        front_matter = ["---"]
        front_matter.append(f'title: "{title}"')
        front_matter.append("draft: false")
        if authors:
            front_matter.append("authors:")
            for author in authors:
                # Ensure quotes within author names are escaped for YAML
                escaped_author = author.replace('"', '\\"')
                front_matter.append(f'- "{escaped_author}"')
        front_matter.append(f'date: "{date}"')
        if doi:
            front_matter.append(f'doi: "{doi}"')
        front_matter.append(f"category: [\"{publication_type}\"]")
        if publication_name:
            front_matter.append(f'journal: "{publication_name}"')
        if abstract:
            # Escape quotes within the summary for YAML compatibility
            escaped_abstract = abstract.replace('"', '\\"')
            front_matter.append(f'summary: "{escaped_abstract}"')
        if keywords:
            front_matter.append("tags:")
            for keyword in keywords:
                 # Ensure quotes within keywords are escaped for YAML
                escaped_keyword = keyword.replace('"', '\\"')
                front_matter.append(f'- "{escaped_keyword}"')
        if url:
            front_matter.append("links:")
            front_matter.append(f'- name: "URL"')
            front_matter.append(f'  url: "{url}"')

        # Add other optional fields if present
        pdf_url = entry.get("file", "") # Basic check, might need refinement
        if pdf_url and "pdf" in pdf_url.lower():
             # Attempt to extract a URL if it looks like one
             pdf_match = re.search(r'(https?://[^\s;]+)', pdf_url)
             if pdf_match:
                 front_matter.append(f'url_pdf: {pdf_match.group(1)}')
             # Note: Handling local file paths like C:\... is complex
             # and usually not desired directly in Hugo front matter.

        front_matter.append(f"featured: {'true' if args.featured else 'false'}")
        front_matter.append("---")
        front_matter.append("") # Blank line after front matter

        # --- Build Body ---
        body = []
        if abstract:
            body.append("## Abstract")
            body.append("")
            body.append(abstract) # Abstract already cleaned/unicoded
            body.append("")

        # Add BibTeX entry
        # Note: This will now contain Unicode characters instead of LaTeX commands
        # because the customization modified the entry dictionary.
        bibtex_string_for_block = create_bibtex_string(entry)
        body.append("> To cite this publication, please use the following BibTeX entry:")
        body.append("```bibtex")
        body.append(bibtex_string_for_block.strip())
        body.append("```")

        # --- Combine and Write File ---
        markdown_content = "\n".join(front_matter) + "\n".join(body)
        filename = generate_filename(entry_id)
        filepath = os.path.join(args.output, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            print(f"  -> Saved to {filepath}")
        except Exception as e:
            print(f"  -> Error writing file {filepath}: {e}")

    print("Processing complete.")


if __name__ == "__main__":
    main()
