import os
from colorama import Fore, init
from pdf_utils import is_pdf_encrypted, open_pdf_with_password
from search_utils import search_pdf
from extract_utils import extract_selected_information

# Inicializa o Colorama
init(autoreset=True)

def analyze_pdf(file_path):
    """
    Função principal para análise de PDF.
    """
    file_path = file_path.strip("'\"")  # Remove aspas no caminho

    if not os.path.exists(file_path):
        print(Fore.RED + "File not found!")
        return

    print(Fore.CYAN + f"Analyzing: {file_path}\n")

    password = None  # Variável para armazenar a senha, se necessário

    # Verificar criptografia
    if is_pdf_encrypted(file_path):
        print(Fore.YELLOW + "The PDF is encrypted.")
        password = open_pdf_with_password(file_path)
        if not password:
            print(Fore.RED + "Unable to unlock PDF. Exiting.")
            return
    else:
        print(Fore.GREEN + "The PDF is not encrypted.")

    # Escolha entre busca e extração
    print(Fore.CYAN + "\nChoose an option:")
    print("[1] Search in PDF")
    print("[2] Extract Emails/URLs and Metadata")
    choice = input(Fore.CYAN + "Enter your choice: ").strip()

    if choice == '1':
        search_query = input(Fore.CYAN + "Enter text/regex to search: ").strip()
        search_pdf(file_path, search_query, password=password)
    elif choice == '2':
        extract_selected_information(file_path, password=password)
    else:
        print(Fore.RED + "Invalid choice. Exiting.")

if __name__ == "__main__":
    print(Fore.CYAN + "\nPDF Analysis Tool\n")
    pdf_file_path = input(Fore.CYAN + "Enter the PDF file path: ").strip()
    analyze_pdf(pdf_file_path)
