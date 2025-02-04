from colorama import Fore
from pdfminer.high_level import extract_text
import re

def search_pdf(file_path, search_query, password=None):
    """
    Realiza busca no texto do PDF por texto ou regex, usando a senha se necessário.
    """
    case_sensitive = input("Do you want a case-sensitive search? (Y/N): ").strip().lower()
    is_case_sensitive = case_sensitive == 'y'
    
    print(Fore.CYAN + f"\nSearching for: {search_query} ({'Case Sensitive' if is_case_sensitive else 'Case Insensitive'})\n")
    
    try:
        # Extrai texto usando a senha, se fornecida
        text = extract_text(file_path, password=password)
        if not text:
            print(Fore.RED + "No text found in the PDF.")
            return

        # Define a flag de busca com base na escolha do usuário
        flags = 0 if is_case_sensitive else re.IGNORECASE
        
        # Procura a expressão no texto extraído
        lines = text.splitlines()
        found = False
        for i, line in enumerate(lines, start=1):
            if re.search(search_query, line, flags):
                print(Fore.GREEN + f"Line {i}: {line}")
                found = True

        if not found:
            print(Fore.RED + "No matches found for the query.")

    except Exception as e:
        print(Fore.RED + f"Error searching PDF: {e}")
