import os
import re
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


def analyze_pdf(file_path):
    # Verificar se o arquivo existe
    if not os.path.exists(file_path):
        print("Arquivo não encontrado!")
        return

    print(f"Analisando o arquivo: {file_path}\n")

    # Detalhes básicos do arquivo
    print("Detalhes do Arquivo:")
    print(f"- Nome do arquivo: {os.path.basename(file_path)}")
    print(f"- Tamanho: {os.path.getsize(file_path)} bytes\n")

    # Analisar metadados
    print("Metadados do PDF:")
    try:
        with open(file_path, 'rb') as f:
            parser = PDFParser(f)
            document = PDFDocument(parser)
            if document.info:
                for metadata in document.info:
                    for key, value in metadata.items():
                        key_decoded = decode_with_fallback(key)
                        value_decoded = decode_with_fallback(value)
                        
                        # Printar apenas uma vez o campo Author
                        if "author" in key_decoded.lower():
                            print(f"→ Author encontrado nos metadados: {value_decoded}")
                        elif "creator" in key_decoded.lower():
                            print(f"  Creator: {value_decoded}")
                        elif "producer" in key_decoded.lower():
                            print(f"  Producer: {value_decoded}")
                        else:
                            print(f"  {key_decoded}: {value_decoded}")
            else:
                print("  Nenhum metadado encontrado.")
    except PDFSyntaxError as e:
        print(f"Erro ao analisar metadados: {e}\n")
    except Exception as e:
        print(f"Erro geral ao analisar metadados: {e}\n")

    # Extrair texto do PDF
    try:
        text = extract_text(file_path)
        if text.strip():
            # Procurar por e-mails no texto
            print("Procurando por e-mails no conteúdo do PDF:")
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
            if emails:
                print(f"  E-mails encontrados: {', '.join(emails)}")
            else:
                print("  Nenhum e-mail encontrado.")

            # Procurar por sistemas operacionais ou softwares
            print("\nProcurando por informações de sistema operacional ou software:")
            os_info = re.findall(r'(Windows|Linux|macOS|Ubuntu|Fedora|Android)[\s\w\d.]*', text, re.IGNORECASE)
            if os_info:
                print(f"  Sistemas operacionais mencionados: {', '.join(set(os_info))}")
            else:
                print("  Nenhuma informação de sistema operacional identificada.")
        else:
            print("Nenhum texto extraído.")
    except Exception as e:
        print(f"Erro ao extrair texto: {e}")

    print("\nAnálise Concluída!\n")


if __name__ == "__main__":
    # Caminho para o arquivo PDF a ser analisado
    pdf_file_path = input("Digite o caminho do arquivo PDF: ").strip()
    analyze_pdf(pdf_file_path)

