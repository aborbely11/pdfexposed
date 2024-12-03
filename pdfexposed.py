import os
import re
import glob
import readline  # Para autocomplete no Linux
from colorama import Fore, Style, init
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFSyntaxError
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfpage import PDFPage

# Inicializa o colorama para suportar cores no terminal
init(autoreset=True)

ENCODINGS = ['utf-8', 'latin-1', 'utf-16', 'utf-16le', 'utf-16be', 'ascii', 'cp1252']


def decode_with_fallback(value):
    """
    Decodifica um valor de bytes usando uma lista de encodings comuns.
    """
    for encoding in ENCODINGS:
        try:
            return value.decode(encoding)
        except (UnicodeDecodeError, AttributeError):
            continue
    return value  # Retorna o valor original se nenhum encoding funcionar


def complete_path(text, state):
    """
    Função de autocomplete para caminhos de arquivos.
    """
    line = readline.get_line_buffer().split()
    if not line:
        return [os.path.join('.', f) for f in os.listdir('.')][state]
    path = os.path.expanduser(text)
    matches = []
    if os.path.isdir(path):
        matches = [os.path.join(path, f) for f in os.listdir(path)]
    else:
        matches = glob.glob(path + '*')
    try:
        return matches[state]
    except IndexError:
        return None


def search_pdf(file_path, search_query):
    """
    Realiza uma busca específica no PDF por texto ou regex, incluindo metadados e texto.
    """
    print(Fore.CYAN + f"\nPerforming search for: {search_query}\n")
    found_results = []

    try:
        with open(file_path, 'rb') as f:
            parser = PDFParser(f)
            document = PDFDocument(parser)
            if document.info:
                print(Fore.BLUE + "Searching in Metadata:")
                for metadata in document.info:
                    for key, value in metadata.items():
                        key_decoded = decode_with_fallback(key)
                        value_decoded = decode_with_fallback(value)
                        if re.search(search_query, value_decoded, re.IGNORECASE):
                            found_results.append({
                                "section": "Metadata",
                                "key": key_decoded,
                                "value": value_decoded
                            })
                            print(Fore.GREEN + f"  Found in {key_decoded}: {value_decoded}")

        # Buscar no texto
        print(Fore.BLUE + "\nSearching in Text:")
        text = extract_text(file_path)
        lines = text.splitlines()
        for line_no, line in enumerate(lines, start=1):
            if re.search(search_query, line, re.IGNORECASE):
                found_results.append({
                    "section": "Text",
                    "line_number": line_no,
                    "line_content": line
                })
                print(Fore.GREEN + f"  Line {line_no}: {line}")

        # Relatório final
        if not found_results:
            print(Fore.RED + "No matches found for the query.")

    except Exception as e:
        print(Fore.RED + f"Error during search: {e}")


def extract_selected_information(file_path):
    """
    Extrai apenas as informações específicas: e-mails, URLs, sistemas operacionais, paths e alterações no cabeçalho.
    """
    print(Fore.CYAN + "\nExtracting selected information...\n")
    os_detected = set()
    emails_found = set()
    urls_found = set()
    export_paths = []
    creation_date = None
    modification_date = None

    try:
        # Analisar metadados
        with open(file_path, 'rb') as f:
            parser = PDFParser(f)
            document = PDFDocument(parser)
            if document.info:
                for metadata in document.info:
                    for key, value in metadata.items():
                        key_decoded = decode_with_fallback(key)
                        value_decoded = decode_with_fallback(value)

                        # Extração de e-mails, URLs, paths e sistemas operacionais
                        emails_found.update(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', value_decoded))
                        urls_found.update(re.findall(r'https?://[^\s]+', value_decoded))
                        os_detected.update(re.findall(r'\((Windows|Linux|macOS|Ubuntu|Fedora|Android)\)', value_decoded, re.IGNORECASE))
                        if re.search(r'(C:\\|/home/|/Users/)', value_decoded, re.IGNORECASE):
                            export_paths.append(value_decoded)

                        # Identificar datas de criação e modificação
                        if "creationdate" in key_decoded.lower():
                            creation_date = value_decoded
                        if "moddate" in key_decoded.lower():
                            modification_date = value_decoded

        # Extrair texto do PDF
        print(Fore.BLUE + "\nAnalyzing Text for Emails and URLs...")
        try:
            text = extract_text(file_path)
            lines = text.splitlines()
            for line in lines:
                emails_found.update(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', line))
                urls_found.update(re.findall(r'https?://[^\s]+', line))
        except Exception as e:
            print(Fore.RED + f"Error extracting text: {e}")

        # Exibir sistemas operacionais
        if os_detected:
            print(Fore.CYAN + f"\nOperating Systems Detected: {', '.join(set(os_detected))}")

        # Exibir paths
        if export_paths:
            print(Fore.CYAN + "\nPossible Export Paths Found:")
            for path in export_paths:
                print(Fore.YELLOW + f"  {path}")

        # Exibir e-mails
        if emails_found:
            print(Fore.YELLOW + "\nE-mails Found:")
            for email in emails_found:
                print(Fore.GREEN + f"  {email}")

        # Exibir URLs
        if urls_found:
            print(Fore.YELLOW + "\nURLs Found:")
            for url in urls_found:
                print(Fore.GREEN + f"  {url}")

        # Exibir análise de cabeçalhos (datas)
        if creation_date and modification_date:
            print(Fore.BLUE + "\nDate Analysis:")
            print(Fore.YELLOW + f"  - Creation Date: {creation_date}")
            print(Fore.YELLOW + f"  - Modification Date: {modification_date}")
            if creation_date != modification_date:
                print(Fore.RED + "  ⚠️ The metadata indicates the file was modified.")
            else:
                print(Fore.GREEN + "  ✅ No modifications detected in the dates.")
        elif creation_date or modification_date:
            print(Fore.BLUE + "\nDate Analysis:")
            print(Fore.YELLOW + f"  - Creation Date: {creation_date or 'Not Found'}")
            print(Fore.YELLOW + f"  - Modification Date: {modification_date or 'Not Found'}")
        else:
            print(Fore.RED + "  Unable to determine creation or modification dates.")

    except Exception as e:
        print(Fore.RED + f"Error during extraction: {e}")


def analyze_pdf(file_path):
    file_path = file_path.strip("'\"")

    if not os.path.exists(file_path):
        print(Fore.RED + "File not Found!")
        return

    print(Fore.CYAN + f"File Location: {os.path.abspath(file_path)}\n")
    print(Fore.CYAN + f"Analyzing the file: {file_path}\n")

    try:
        print(Fore.BLUE + "Path Details:")
        print(Fore.YELLOW + f"  - Filename: {os.path.basename(file_path)}")
        print(Fore.YELLOW + f"  - Size: {os.path.getsize(file_path)} bytes\n")

        with open(file_path, 'rb') as f:
            parser = PDFParser(f)
            document = PDFDocument(parser)
            num_pages = sum(1 for _ in PDFPage.create_pages(document))
            print(Fore.YELLOW + f"  - Number of Pages: {num_pages}\n")

        perform_search = input(Fore.CYAN + "Do you want to perform a search? (Y for Yes, X for No): ").strip().upper()
        if perform_search == 'Y':
            search_query = input(Fore.CYAN + "Enter the text or regex to search: ").strip()
            search_pdf(file_path, search_query)
        elif perform_search == 'X':
            print(Fore.GREEN + "No specific search performed. Extracting selected information...")
            extract_selected_information(file_path)
        else:
            print(Fore.RED + "Invalid option. Extracting selected information by default...")
            extract_selected_information(file_path)

    except PDFSyntaxError as e:
        print(Fore.RED + f"Error analyzing metadata: {e}\n")
    except Exception as e:
        print(Fore.RED + f"General error analyzing metadata: {e}\n")

    print(Fore.CYAN + "\nAnalysis Completed!\n")


if __name__ == "__main__":
    readline.set_completer(complete_path)
    readline.parse_and_bind("tab: complete")

    pdf_file_path = input(Fore.CYAN + "Enter the PDF file path: ").strip()
    analyze_pdf(pdf_file_path)
