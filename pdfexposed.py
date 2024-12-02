import os
import re
import readline  # Para autocomplete no Linux
from colorama import Fore, Style, init
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFSyntaxError
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfpage import PDFPage

# Inicializa o colorama para suportar cores no terminal
init(autoreset=True)

# Lista de encodings comuns para tentar
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
    return value  # Retorna o original caso todos os encodings falhem


def complete_path(text, state):
    """
    Função de autocomplete para caminhos de arquivos.
    """
    line = readline.get_line_buffer().split()
    if not line:
        return [os.path.join('.', f) for f in os.listdir('.')][state]
    path = os.path.expanduser(text)
    if os.path.isdir(path):
        return [os.path.join(path, f) for f in os.listdir(path)][state]
    else:
        return [f for f in glob.glob(path + '*')][state]


def analyze_pdf(file_path):
    # Remover aspas do caminho, se existirem
    file_path = file_path.strip("'\"")

    # Verificar se o arquivo existe
    if not os.path.exists(file_path):
        print(Fore.RED + "File not Found!")
        return

    # Mostrar onde o arquivo está salvo
    print(Fore.CYAN + f"File Location: {os.path.abspath(file_path)}\n")

    print(Fore.CYAN + f"Analyzing the file: {file_path}\n")

    # Detalhes básicos do arquivo
    print(Fore.BLUE + "Path Details:")
    print(Fore.YELLOW + f"  - Filename: {os.path.basename(file_path)}")
    print(Fore.YELLOW + f"  - Size: {os.path.getsize(file_path)} bytes\n")

    os_detected = set()
    author_detected = None
    creation_date = None
    modification_date = None
    producer = None
    creator = None
    export_path = None  # Para armazenar o possível path de exportação

    try:
        with open(file_path, 'rb') as f:
            parser = PDFParser(f)
            document = PDFDocument(parser)
            # Contar número de páginas
            num_pages = sum(1 for _ in PDFPage.create_pages(document))
            print(Fore.YELLOW + f"  - Number of Pages: {num_pages}")
            
            if document.info:
                for metadata in document.info:
                    for key, value in metadata.items():
                        key_decoded = decode_with_fallback(key)
                        value_decoded = decode_with_fallback(value)

                        # Verificar o autor
                        if "author" in key_decoded.lower():
                            author_detected = value_decoded
                            print(Fore.GREEN + f"  - Author: {value_decoded}")

                        # Identificar datas de criação e modificação
                        if "creationdate" in key_decoded.lower():
                            creation_date = value_decoded
                        elif "moddate" in key_decoded.lower():
                            modification_date = value_decoded

                        # Produtor e Criador
                        if "producer" in key_decoded.lower():
                            producer = value_decoded
                        elif "creator" in key_decoded.lower():
                            creator = value_decoded

                        # Procurar sistemas operacionais nos metadados
                        os_in_metadata = re.findall(r'\((Windows|Linux|macOS|Ubuntu|Fedora|Android)\)', value_decoded, re.IGNORECASE)
                        if os_in_metadata:
                            print(Fore.GREEN + f"    → Operating System(s) found in metadata ({key_decoded}): {', '.join(os_in_metadata)}")
                            os_detected.update(os_in_metadata)

                        # Verificar se há um caminho no metadado
                        if re.search(r'(C:\\|/home/|/Users/)', value_decoded, re.IGNORECASE):
                            export_path = value_decoded
                            print(Fore.GREEN + f"  Possible Export Path Detected in {key_decoded}: {value_decoded}")

                        # Exibir os demais metadados
                        print(Fore.GREEN + f"    {key_decoded}: {value_decoded}")

            # Analisar possíveis modificações no campo "Author"
            print(Fore.BLUE + "\nAuthor Analysis:")
            if author_detected:
                if creation_date and modification_date:
                    print(Fore.YELLOW + f"  - Creation Date: {creation_date}")
                    print(Fore.YELLOW + f"  - Modification Date: {modification_date}")
                    if creation_date != modification_date:
                        print(Fore.RED + "  ⚠️ The metadata indicates the file was modified.")
                        print(Fore.RED + "    Note: This may suggest the 'Author' field was changed.")
                    else:
                        print(Fore.GREEN + "  ✅ No modifications detected in the dates.")
                else:
                    print(Fore.RED + "  Unable to determine modification status (dates missing).")
            else:
                print(Fore.RED + "  No 'Author' field detected in metadata.")

            # Verificar inconsistências no produtor ou criador
            if producer and creator:
                print(Fore.YELLOW + f"  - Producer: {producer}")
                print(Fore.YELLOW + f"  - Creator: {creator}")
                if producer != creator:
                    print(Fore.RED + "  ⚠️ Producer and Creator fields do not match, suggesting possible edits.")
            elif producer or creator:
                print(Fore.YELLOW + f"  - Producer: {producer or 'Not found'}")
                print(Fore.YELLOW + f"  - Creator: {creator or 'Not found'}")

            # Imprimir sistemas operacionais encontrados
            if os_detected:
                print(Fore.GREEN + f"\nOperating Systems identified in metadata: {', '.join(set(os_detected))}")

            # Resultado final para o caminho de exportação
            if export_path:
                print(Fore.CYAN + f"\nDetected Export Path: {export_path}")
            else:
                print(Fore.RED + "No export path could be identified.")

    except PDFSyntaxError as e:
        print(Fore.RED + f"Error analyzing metadata: {e}\n")
    except Exception as e:
        print(Fore.RED + f"General error analyzing metadata: {e}\n")

    # Extrair texto do PDF
    try:
        text = extract_text(file_path)
        if text.strip():
            # Procurar por e-mails no texto
            print(Fore.BLUE + "Searching for e-mails:")
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
            if emails:
                print(Fore.YELLOW + "  - E-mails Found:")
                for email in emails:
                    print(Fore.GREEN + f"    {email}")
            else:
                print(Fore.RED + "  No emails found.")

            # Procurar por URLs no texto
            print(Fore.BLUE + "\nSearching for URLs:")
            urls = re.findall(r'https?://[^\s]+', text)
            if urls:
                print(Fore.YELLOW + "  - URLs Found:")
                for url in urls:
                    print(Fore.GREEN + f"    {url}")
            else:
                print(Fore.RED + "  No URLs found.")
        else:
            print(Fore.RED + "No text extracted.")
    except Exception as e:
        print(Fore.RED + f"Error extracting text: {e}")

    print(Fore.CYAN + "\nAnalysis Completed!\n")


if __name__ == "__main__":
    # Configuração para autocomplete no terminal
    readline.set_completer(complete_path)
    readline.parse_and_bind("tab: complete")
    
    # Caminho para o arquivo PDF a ser analisado
    pdf_file_path = input(Fore.CYAN + "Enter the PDF file path: ").strip()
    analyze_pdf(pdf_file_path)
