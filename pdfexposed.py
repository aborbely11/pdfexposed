import os
from colorama import Fore, init
from pdf_utils import is_pdf_encrypted, open_pdf_with_password
from search_utils import search_pdf
from extract_utils import extract_selected_information
from integrity_utils import check_integrity
from compare_utils import compare_pdfs  # Importando o módulo de comparação

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

def clean_path(file_path):
    """
    Limpa o caminho do arquivo removendo aspas e espaços indesejados.
    """
    return file_path.strip().strip("'").strip('"')

def analyze_pdf(file_path):
    """
    Função principal para analisar um PDF.
    """
    file_path = clean_path(file_path)

    if not os.path.exists(file_path):
        print(Fore.RED + f"Error: File not found! ({file_path})")
        return

    password = None

    if is_pdf_encrypted(file_path):
        print(Fore.YELLOW + "The PDF is encrypted.")
        password = open_pdf_with_password(file_path)
        if not password:
            print(Fore.RED + "Unable to unlock the PDF. Exiting.")
            return
        print(Fore.GREEN + "The PDF was successfully unlocked!")
    else:
        print(Fore.GREEN + "The PDF is not encrypted.")

    # Pergunta se o usuário deseja comparar com outro PDF
    choice = input(Fore.CYAN + "Do you want to compare with another PDF? (Y/N): ").strip().lower()
    if choice == 'y':
        second_pdf = input(Fore.CYAN + "Enter the second PDF file path: ").strip()
        second_pdf = clean_path(second_pdf)
        if os.path.exists(second_pdf):
            second_password = None
            if is_pdf_encrypted(second_pdf):
                print(Fore.YELLOW + "The second PDF is encrypted.")
                second_password = open_pdf_with_password(second_pdf)
                if not second_password:
                    print(Fore.RED + "Unable to unlock the second PDF. Exiting comparison.")
                    return
                print(Fore.GREEN + "The second PDF was successfully unlocked!")
            
            print(Fore.CYAN + "\nComparing the files...")
            differences_found = compare_pdfs(file_path, second_pdf, password1=password, password2=second_password)
            
            if not differences_found:
                print(Fore.GREEN + "No differences found between the PDFs.")
            return  # Sai após a comparação
        else:
            print(Fore.RED + f"Error: Second file not found! ({second_pdf}) Exiting comparison.")
            return
    
    # Menu de opções
    while True:
        print(Fore.CYAN + "\nChoose an option:")
        print("[1] Search in PDF")
        print("[2] Extract Emails/URLs/CPF/CNPJ and Metadata")
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
            print(Fore.RED + "Invalid option. Please try again.")

if __name__ == "__main__":
    print_banner()
    pdf_file_path = input(Fore.CYAN + "Enter the PDF file path: ").strip()
    analyze_pdf(pdf_file_path)
