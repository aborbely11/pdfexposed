import os
from colorama import Fore, init
from pdf_utils import is_pdf_encrypted, open_pdf_with_password
from search_utils import search_pdf
from extract_utils import extract_selected_information
from integrity_utils import check_integrity

# Inicializa o Colorama
init(autoreset=True)

def print_banner():
    """
    Exibe um banner de boas-vindas com arte ASCII.
    """
    banner = """
            ::::::::::::        
            ::::::::::::;;      
            ::::::::::::;;;;    
            ::::::::::::::::    
            ::::::::::::::::    
          $$$$$:::::::::::::    
        $:;:;;;;;:::::::::::    
       $;:::;:;;;$::::::::::    
       $;;;:::;:;$;;;;;;;:::    
        $;;;;:::::::::::::::    
       +: $;;;$$::::::::::::    
     ++     ::::::::::::::::    
    ++                           
    PDFEXPOSED - Reveal the hidden!
### Made by Artur Borbely
    """
    print(Fore.GREEN + banner)

def analyze_pdf(file_path):
    """
    Função principal para análise de PDF.
    """
    file_path = file_path.strip("'")

    if not os.path.exists(file_path):
        print(Fore.RED + "File not found!")
        return

    password = None

    if is_pdf_encrypted(file_path):
        print(Fore.YELLOW + "The PDF is encrypted.")
        password = open_pdf_with_password(file_path)
        if not password:
            print(Fore.RED + "Unable to unlock PDF. Exiting.")
            return
        print(Fore.GREEN + "The PDF was successfully unlocked!")
    else:
        print(Fore.GREEN + "The PDF is not encrypted.")

    # Escolha de opções
    while True:
        print(Fore.CYAN + "\nChoose an option:")
        print("[1] Search in PDF")
        print("[2] Extract Emails/URLs and Metadata")
        print("[3] Check Document Integrity")
        print("[9] Exit")
        
        choice = input(Fore.CYAN + "Enter your choice: ").strip()

        if choice == '1':
            search_query = input(Fore.CYAN + "Enter text/regex to search: ").strip()
            search_pdf(file_path, search_query, password=password)
        elif choice == '2':
            extract_selected_information(file_path, password=password)
        elif choice == '3':
            check_integrity(file_path, password=password)
        elif choice == '9':
            print(Fore.GREEN + "Exiting the program. Goodbye!")
            break
        else:
            print(Fore.RED + "Invalid choice. Please try again.")

if __name__ == "__main__":
    print_banner()
    pdf_file_path = input(Fore.CYAN + "Enter the PDF file path: ").strip()
    analyze_pdf(pdf_file_path)
