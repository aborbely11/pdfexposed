import os
import re
import readline  # Para autocomplete no Linux
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFSyntaxError
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfpage import PDFPage

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
        print("File not Found!")
        return

    # Mostrar onde o arquivo está salvo
    print(f"File Location: {os.path.abspath(file_path)}\n")

    print(f"Analyzing the file: {file_path}\n")

    # Detalhes básicos do arquivo
    print("Path Details:")
    print(f"- Filename: {os.path.basename(file_path)}")
    print(f"- Size: {os.path.getsize(file_path)} bytes\n")

    os_detected = set()

    # Analisar metadados e número de páginas
    print("Metadata:")
    try:
        with open(file_path, 'rb') as f:
            parser = PDFParser(f)
            document = PDFDocument(parser)
            # Contar número de páginas
            num_pages = sum(1 for _ in PDFPage.create_pages(document))
            print(f"  Number of Pages: {num_pages}")
            
            if document.info:
                for metadata in document.info:
                    for key, value in metadata.items():
                        key_decoded = decode_with_fallback(key)
                        value_decoded = decode_with_fallback(value)
                        
                        if "author" in key_decoded.lower():
                            print(f"→ Author is: {value_decoded}")
                        elif "creator" in key_decoded.lower():
                            print(f"  Creator: {value_decoded}")
                        elif "producer" in key_decoded.lower():
                            print(f"  Producer: {value_decoded}")
                        else:
                            print(f"  {key_decoded}: {value_decoded}")

                        # Procurar por URLs nos metadados
                        urls = re.findall(r'https?://[^\s]+', value_decoded)
                        if urls:
                            print("  URLs Found in Metadata:")
                            for url in urls:
                                print(f"    - {url}")

                        # Procurar por sistemas operacionais nos metadados
                        match = re.search(r'\b(Windows|Linux|macOS|Ubuntu|Fedora|Android)\b', value_decoded, re.IGNORECASE)
                        if match:
                            os_detected.add(match.group())
            else:
                print("  Not Found.")
    except PDFSyntaxError as e:
        print(f"Error analyzing metadata: {e}\n")
    except Exception as e:
        print(f"General error analyzing metadata: {e}\n")

    # Extrair texto do PDF
    try:
        text = extract_text(file_path)
        if text.strip():
            # Procurar por e-mails no texto
            print("Searching for e-mails:")
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
            if emails:
                print(f"  E-mails Found: {', '.join(emails)}")
            else:
                print("  No emails found.")

            # Procurar por URLs no texto
            print("\nSearching for URLs:")
            urls = re.findall(r'https?://[^\s]+', text)
            if urls:
                print("  URLs Found:")
                for url in urls:
                    print(f"    - {url}")
            else:
                print("  No URLs found.")

            # Procurar sistemas operacionais no texto
            print("\nSearching for operating system information:")
            os_info = re.findall(r'\b(Windows|Linux|macOS|Ubuntu|Fedora|Android)\b', text, re.IGNORECASE)
            if os_info:
                os_detected.update(os_info)

            # Mostrar apenas os sistemas operacionais detectados
            if os_detected:
                print(f"\nOperating systems identified: {', '.join(set(os_detected))}")
            else:
                print("  No operating system information identified.")

        else:
            print("No text extracted.")
    except Exception as e:
        print(f"Error extracting text: {e}")

    print("\nAnalysis Completed!\n")


if __name__ == "__main__":
    # Configuração para autocomplete no terminal
    readline.set_completer(complete_path)
    readline.parse_and_bind("tab: complete")
    
    # Caminho para o arquivo PDF a ser analisado
    pdf_file_path = input("Enter the PDF file path: ").strip()
    analyze_pdf(pdf_file_path)
