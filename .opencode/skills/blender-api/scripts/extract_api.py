#!/usr/bin/env python3
"""
Extract API content from Blender 5.0 Python reference HTML files.

Strips the ~300KB sidebar/navigation boilerplate from each HTML file,
extracting only the <article role="main"> content and converting it
to clean markdown-like text.

Usage:
    python extract_api.py <input_dir> <output_dir> [--files FILE1 FILE2 ...]
    python extract_api.py <input_dir> <output_dir> --pattern "bpy.ops.object*"

If --files is omitted and --pattern is omitted, processes ALL .html files.
"""

import argparse
import fnmatch
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


class BlenderAPIExtractor(HTMLParser):
    """
    Parses Blender Sphinx-generated HTML and extracts content from
    <article role="main" id="furo-main-content">.
    Converts to clean text with markdown-style formatting.
    """

    def __init__(self):
        super().__init__()
        self.in_article = False
        self.article_depth = 0
        self.tag_stack: list[str] = []
        self.output_parts: list[str] = []
        self.current_text = ""
        self.skip_tags = {"script", "style", "nav"}
        self.skip_depth = 0
        self.in_code_block = False
        self.code_block_content = ""
        self.in_pre = False
        self.in_dt = False
        self.in_dd = False
        self.dd_depth = 0
        self.list_depth = 0
        self.in_headerlink = False

    def _flush_text(self):
        """Flush accumulated text to output."""
        if self.current_text.strip():
            self.output_parts.append(self.current_text)
        self.current_text = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        attrs_dict = dict(attrs)

        # Detect the main content article
        if (tag == "article" and attrs_dict.get("role") == "main"):
            self.in_article = True
            self.article_depth = 0
            return

        if not self.in_article:
            return

        # Track nesting depth within article
        if tag in ("div", "section", "article", "aside", "details"):
            self.article_depth += 1

        # Skip script/style/nav
        if tag in self.skip_tags:
            self.skip_depth += 1
            return

        if self.skip_depth > 0:
            return

        # Skip headerlink anchors (the ¶ symbols)
        if tag == "a" and "headerlink" in (attrs_dict.get("class") or ""):
            self.in_headerlink = True
            return

        # Skip toctree-wrapper divs (internal nav within articles)
        if tag == "div" and "toctree-wrapper" in (attrs_dict.get("class") or ""):
            self.skip_depth += 1
            return

        # Handle headings
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._flush_text()
            level = int(tag[1])
            self.output_parts.append("\n" + "#" * level + " ")
            return

        # Handle code blocks
        if tag == "pre":
            self.in_pre = True
            self._flush_text()
            self.output_parts.append("\n```python\n")
            return

        if tag == "code" and not self.in_pre:
            self.current_text += "`"
            return

        # Handle definition lists (used for API signatures)
        if tag == "dt":
            self._flush_text()
            self.in_dt = True
            self.output_parts.append("\n**")
            return

        if tag == "dd":
            self.in_dd = True
            self.dd_depth += 1
            return

        # Handle lists
        if tag in ("ul", "ol"):
            self.list_depth += 1
            self._flush_text()
            return

        if tag == "li":
            self._flush_text()
            indent = "  " * max(0, self.list_depth - 1)
            self.output_parts.append(f"\n{indent}- ")
            return

        # Handle paragraphs
        if tag == "p":
            self._flush_text()
            self.output_parts.append("\n\n")
            return

        # Handle line breaks
        if tag == "br":
            self.current_text += "\n"
            return

        # Handle emphasis
        if tag in ("em", "i"):
            self.current_text += "*"
            return

        if tag in ("strong", "b"):
            self.current_text += "**"
            return

        # Handle tables
        if tag == "table":
            self._flush_text()
            self.output_parts.append("\n")
            return

        if tag == "tr":
            self._flush_text()
            self.output_parts.append("\n| ")
            return

        if tag in ("td", "th"):
            self.current_text += " "
            return

    def handle_endtag(self, tag: str):
        if not self.in_article:
            return

        # End of article
        if tag == "article":
            self._flush_text()
            self.in_article = False
            return

        # Track nesting
        if tag in ("div", "section", "article", "aside", "details"):
            self.article_depth = max(0, self.article_depth - 1)

        # End skip
        if tag in self.skip_tags:
            self.skip_depth = max(0, self.skip_depth - 1)
            return

        if self.skip_depth > 0:
            # Check if this is ending a toctree-wrapper
            if tag == "div":
                self.skip_depth = max(0, self.skip_depth - 1)
            return

        if self.in_headerlink and tag == "a":
            self.in_headerlink = False
            return

        # Headings
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._flush_text()
            self.output_parts.append("\n\n")
            return

        # Code blocks
        if tag == "pre":
            self.in_pre = False
            self._flush_text()
            self.output_parts.append("\n```\n")
            return

        if tag == "code" and not self.in_pre:
            self.current_text += "`"
            return

        # Definition lists
        if tag == "dt":
            self.in_dt = False
            self._flush_text()
            self.output_parts.append("**\n")
            return

        if tag == "dd":
            self.dd_depth = max(0, self.dd_depth - 1)
            if self.dd_depth == 0:
                self.in_dd = False
            return

        # Lists
        if tag in ("ul", "ol"):
            self.list_depth = max(0, self.list_depth - 1)
            return

        # Emphasis
        if tag in ("em", "i"):
            self.current_text += "*"
            return

        if tag in ("strong", "b"):
            self.current_text += "**"
            return

        # Table cells
        if tag in ("td", "th"):
            self.current_text += " | "
            return

    def handle_data(self, data: str):
        if not self.in_article or self.skip_depth > 0 or self.in_headerlink:
            return

        if self.in_pre:
            # Preserve whitespace in code blocks
            self.current_text += data
        else:
            # Collapse whitespace in regular text
            self.current_text += data

    def get_output(self) -> str:
        """Return the extracted content as clean text."""
        self._flush_text()
        text = "".join(self.output_parts)

        # Clean up excessive whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+\n", "\n", text)
        # Collapse runs of spaces (but not leading indentation in code)
        lines = text.split("\n")
        cleaned = []
        in_code = False
        for line in lines:
            if line.strip().startswith("```"):
                in_code = not in_code
                cleaned.append(line)
            elif in_code:
                cleaned.append(line)
            else:
                cleaned.append(re.sub(r"  +", " ", line))
        text = "\n".join(cleaned)
        return text.strip() + "\n"


def extract_file(input_path: Path) -> str:
    """Extract API content from a single HTML file."""
    with open(input_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    parser = BlenderAPIExtractor()
    parser.feed(html_content)
    return parser.get_output()


def main():
    ap = argparse.ArgumentParser(description="Extract Blender API content from HTML docs")
    ap.add_argument("input_dir", help="Directory containing HTML files")
    ap.add_argument("output_dir", help="Directory for extracted .md files")
    ap.add_argument("--files", nargs="+", help="Specific filenames to process (without path)")
    ap.add_argument("--pattern", help="Glob pattern for filenames (e.g. 'bpy.ops.*')")
    ap.add_argument("--min-lines", type=int, default=3,
                     help="Skip files with fewer content lines (default: 3)")
    args = ap.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_dir.is_dir():
        print(f"Error: {input_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    # Determine which files to process
    if args.files:
        html_files = [input_dir / f for f in args.files if (input_dir / f).exists()]
    elif args.pattern:
        html_files = sorted(input_dir.glob(args.pattern))
    else:
        html_files = sorted(input_dir.glob("*.html"))

    if not html_files:
        print("No matching HTML files found.", file=sys.stderr)
        sys.exit(1)

    print(f"Processing {len(html_files)} files...")

    processed = 0
    skipped = 0
    for html_path in html_files:
        try:
            content = extract_file(html_path)
            line_count = len(content.strip().split("\n"))

            if line_count < args.min_lines:
                skipped += 1
                continue

            out_name = html_path.stem + ".md"
            out_path = output_dir / out_name
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(content)
            processed += 1
        except Exception as e:
            print(f"  Error processing {html_path.name}: {e}", file=sys.stderr)

    print(f"Done. Processed: {processed}, Skipped (too short): {skipped}")


if __name__ == "__main__":
    main()
