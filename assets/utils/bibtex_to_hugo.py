#!/usr/bin/env python3
# Help in https://bibtexparser.readthedocs.io/en/main/

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import author, homogenize_latex_encoding
import argparse
import os
import re
from datetime import datetime

# Month mapping for date conversion
MONTH_MAP = {
    "jan": "01",
    "feb": "02",
    "mar": "03",
    "apr": "04",
    "may": "05",
    "jun": "06",
    "jul": "07",
    "aug": "08",
    "sep": "09",
    "oct": "10",
    "nov": "11",
    "dec": "12",
    "january": "01",
    "february": "02",
    "march": "03",
    "april": "04",
    # 'may': '05', # Already exists
    "june": "06",
    "july": "07",
    "august": "08",
    "september": "09",
    "october": "10",
    "november": "11",
    "december": "12",
}


def sanitize_filename(name):
    """Removes invalid characters for filenames."""
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', "", name)
    # Replace spaces with hyphens
    sanitized = sanitized.replace(" ", "-").lower()
    # Limit length if necessary (optional)
    # sanitized = sanitized[:100]
    return sanitized


def format_date(entry):
    """Formats year and month into YYYY-MM-DD."""
    year = entry.get("year")
    if not year:
        return datetime.now().strftime("%Y-%m-%d")  # Fallback to today

    month_str = entry.get("month", "01").lower()
    month = MONTH_MAP.get(month_str, "01")  # Default to January if unknown

    # Try to handle numeric months as well
    if month_str.isdigit() and 1 <= int(month_str) <= 12:
        month = f"{int(month_str):02d}"

    return f"{year}-{month}-01"  # Default to the 1st of the month


def get_publication_venue(entry):
    """Gets the journal, booktitle, or publisher."""
    if "journal" in entry:
        return entry["journal"]
    elif "booktitle" in entry:
        return entry["booktitle"]
    elif "publisher" in entry:
        return entry["publisher"]
    return ""


def get_category(entry_type):
    """Maps BibTeX entry type to Hugo category."""
    entry_type = entry_type.lower()
    if entry_type == "article":
        return "article-journal"
    elif entry_type in ["inproceedings", "conference"]:
        return "paper-conference"
    elif entry_type == "book":
        return "book"
    elif entry_type == "incollection":
        return "book-section"
    elif entry_type == "techreport":
        return "report"
    elif entry_type == "phdthesis":
        return "thesis"
    elif entry_type == "mastersthesis":
        return "thesis"
    else:
        return entry_type  # Use the type directly as fallback


def clean_text(text):
    """Basic cleaning of text fields."""
    if not text:
        return ""
    # Remove potential outer curly braces often found in BibTeX
    text = text.strip("{} ")
    # Replace common LaTeX-like escapes if needed (add more as required)
    text = text.replace("{", "").replace("}", "")
    text = text.replace("\\&", "&")
    text = text.replace("\\%", "%")
    # Add more replacements here if you find other common escapes
    return text


def create_hugo_content(entry_data):
    """Generates the Hugo Markdown content string."""
    content = "---\n"
    content += f'title: "{entry_data["title"]}"\n'
    content += "draft: false\n"
    content += "authors:\n"
    for auth in entry_data["authors"]:
        content += f'- "{auth}"\n'
    content += f'date: "{entry_data["date"]}"\n'
    if entry_data["doi"]:
        content += f'doi: "{entry_data["doi"]}"\n'
    content += f'category: ["{entry_data["category"]}"]\n'
    if entry_data["journal"]:
        content += f'journal: "{entry_data["journal"]}"\n'
    if entry_data["summary"]:
        # Basic YAML escaping for multi-line strings
        summary_escaped = entry_data["summary"].replace('"', '\\"')
        content += f'summary: "{summary_escaped}"\n'
    if entry_data["tags"]:
        content += "tags:\n"
        for tag in entry_data["tags"]:
            content += f'- "{tag}"\n'
    if entry_data["links"]:
        content += "links:\n"
        for link in entry_data["links"]:
            content += f'- name: "{link["name"]}"\n'
            content += f'  url: "{link["url"]}"\n'
    # Add other fields like 'featured' as needed
    content += f'featured: {str(entry_data.get("featured", False)).lower()}\n'
    content += "---\n\n"

    if entry_data["summary"]:
        content += "## Abstract\n\n"
        content += entry_data["summary"] + "\n"

    return content


def main():
    parser = argparse.ArgumentParser(
        description="Convert BibTeX entries to Hugo Markdown files."
    )
    parser.add_argument(
        "bibtex_file", help="Path to the input BibTeX file (.bib)"
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default="hugo_publications",
        help="Directory to save the generated Markdown files (default: hugo_publications)",
    )
    parser.add_argument(
        "--featured",
        action="store_true",
        help="Mark all generated entries as featured=true",
    )

    args = parser.parse_args()

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Configure bibtexparser
    bib_parser = BibTexParser(common_strings=True)
    bib_parser.customization = homogenize_latex_encoding
    bib_parser.customization = author

    try:
        with open(args.bibtex_file, "r", encoding="utf-8") as bibfile:
            bib_database = bibtexparser.load(bibfile, parser=bib_parser)
    except FileNotFoundError:
        print(f"Error: Input file not found at {args.bibtex_file}")
        return
    except Exception as e:
        print(f"Error parsing BibTeX file: {e}")
        return

    print(f"Found {len(bib_database.entries)} entries.")

    for entry in bib_database.entries:
        entry_id = entry.get("ID", "unknown_entry")
        print(f"Processing entry: {entry_id}")

        try:
            # Prepare data for Hugo template
            hugo_data = {}
            hugo_data["title"] = clean_text(entry.get("title", "Untitled"))
            hugo_data["authors"] = entry.get("author", [])  # Customization handles splitting
            hugo_data["date"] = format_date(entry)
            hugo_data["doi"] = entry.get("doi", "")
            hugo_data["category"] = get_category(entry.get("ENTRYTYPE", "misc"))
            hugo_data["journal"] = clean_text(get_publication_venue(entry))
            hugo_data["summary"] = clean_text(entry.get("abstract", ""))
            hugo_data["featured"] = args.featured

            # Handle keywords/tags
            tags_raw = entry.get("keywords", "") or entry.get("tags", "")
            if tags_raw:
                # Split by comma or semicolon, strip whitespace
                hugo_data["tags"] = [
                    tag.strip()
                    for tag in re.split(r"[,;]", tags_raw)
                    if tag.strip()
                ]
            else:
                hugo_data["tags"] = []

            # Handle links
            hugo_data["links"] = []
            if "url" in entry:
                hugo_data["links"].append({"name": "URL", "url": entry["url"]})
            elif hugo_data["doi"]:
                hugo_data["links"].append(
                    {"name": "DOI", "url": f"https://doi.org/{hugo_data['doi']}"}
                )
            # Add other link types if needed (e.g., url_pdf, url_code from your example)
            # if 'url_pdf' in entry:
            #     hugo_data['links'].append({'name': 'PDF', 'url': entry['url_pdf']})

            # Generate filename (using BibTeX key is usually best)
            filename_base = sanitize_filename(entry_id)
            output_filename = os.path.join(args.output_dir, f"{filename_base}.md")

            # Generate Markdown content
            markdown_content = create_hugo_content(hugo_data)

            # Write the file
            with open(output_filename, "w", encoding="utf-8") as outfile:
                outfile.write(markdown_content)
            print(f"  -> Saved {output_filename}")

        except Exception as e:
            print(f"  -> Error processing entry {entry_id}: {e}")

    print("Processing complete.")


if __name__ == "__main__":
    main()
