import mimetypes
import json
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any
import fitz  # PyMuPDF for handling PDF files
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Retrieve OpenAI API key from environment
# api_key = os.getenv("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")
# api_key=os.environ.get("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")
# if not api_key:
#     logging.error("API key not set. Please add OPENAI_API_KEY to your environment.")
# else:
client = OpenAI(api_key= "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")    


def is_text_file(file_path: Path) -> bool:
    """Check if a file is likely to be text-based."""
    mime_type, _ = mimetypes.guess_type(str(file_path))
    logging.debug(f"Checking file type for {file_path}: mime_type = {mime_type}")
    return mime_type and mime_type.startswith('text')


def extract_text_from_pdf(file_path: Path) -> str:
    """Extract text from a PDF file."""
    try:
        doc = fitz.open(file_path)
        text = "".join(page.get_text() for page in doc)
        logging.info(f"Successfully extracted text from PDF: {file_path}")
        return text
    except Exception as e:
        logging.error(f"Error extracting text from PDF {file_path}: {str(e)}")
        return ""


def get_file_content(file_path: Path, max_size: int = 1024 * 1024) -> Optional[str]:
    """Read file content if it's a text file or extract from a PDF."""
    logging.info(f"Attempting to read: {file_path}")
    
    if not is_text_file(file_path):
        if file_path.suffix.lower() == '.pdf':
            return extract_text_from_pdf(file_path)
        logging.warning(f"Not a text file: {file_path}")
        return None

    if file_path.stat().st_size > max_size:
        logging.warning(f"File too large: {file_path}")
        return f"File too large (>{max_size / 1024 / 1024:.1f}MB)"
        
    try:
        content = file_path.read_text(errors='ignore')
        logging.info(f"Successfully read file: {file_path} (length: {len(content)})")
        return content
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {str(e)}")
        return f"Error reading file: {str(e)}"


def summarize_content(content: str) -> str:
    """Summarize the provided text content using the OpenAI API."""
    if not content:
        return "Empty or binary file"
    
    try:
        truncated_content = content[:2000] + ("..." if len(content) > 2000 else "")
        
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes text."},
                {"role": "user", "content": f"Summarize the following content in 2-3 sentences:\n\n{truncated_content}"}
            ],
            model="gpt-4",
        )

        summary = response.choices[0].message.content.strip()
        return summary if summary else "No summary generated"
    
    except Exception as e:
        logging.error(f"Error generating summary: {e}")
        return f"Error generating summary: {e}"


def build_directory_tree(directory: Path) -> Dict[str, Any]:
    """Builds a directory tree structure with summaries for text files."""
    tree = {"name": directory.name, "type": "directory", "children": []}
    
    for item in directory.iterdir():
        if item.is_dir():
            tree["children"].append(build_directory_tree(item))
        else:
            content = get_file_content(item)
            summary = summarize_content(content) if content else "Non-text or unreadable file"
            tree["children"].append({"name": item.name, "type": "file", "summary": summary})
            
    return tree


def save_tree(tree: Dict[str, Any], output_file: Path) -> None:
    """Save the directory tree structure to a JSON file."""
    with open(output_file, 'w') as f:
        json.dump(tree, f, indent=4)
    logging.info(f"Saved directory tree to {output_file}")


def print_tree(tree: Dict[str, Any], indent: str = "") -> None:
    """Pretty-print the directory tree structure with summaries."""
    print(indent + tree["name"] + (": Directory" if tree["type"] == "directory" else ""))
    
    if "children" in tree:
        for child in tree["children"]:
            print_tree(child, indent + "  ")
    elif "summary" in tree:
        print(indent + f"  Summary: {tree['summary']}")


# Register additional text file MIME types
mimetypes.add_type('text/plain', '.txt')
mimetypes.add_type('text/plain', '.md')
mimetypes.add_type('text/plain', '.py')
mimetypes.add_type('text/plain', '.json')
mimetypes.add_type('text/plain', '.csv')
mimetypes.add_type('text/plain', '.log')


if __name__ == "__main__":
    root_path = Path("/Users/jay/Desktop/College")
    logging.info(f"Starting analysis of {root_path}...")
    
    # Build the directory tree
    tree = build_directory_tree(root_path)
    
    # Save the results
    output_file = Path("directory_summary.json")
    save_tree(tree, output_file)
    logging.info(f"\nResults saved to {output_file}")
    
    # Print the tree
    logging.info("\nDirectory Structure and Summaries:")
    print_tree(tree)
