from colorama import Fore
from pdfminer.high_level import extract_text
import re

def search_pdf(file_path, search_query):
    """
    Realiza busca no texto do PDF por texto ou regex.
    """
    print(Fore.CYAN + f"\nSearching for: {search_query}")
    try:
        text = extract_text(file_path)
        lines = text.splitlines()
        for i, line in enumerate(lines, start=1):
            if re.search(search_query, line, re.IGNORECASE):
                print(Fore.GREEN + f"Line {i}: {line}")
    except Exception as e:
        print(Fore.RED + f"Error searching PDF: {e}")
