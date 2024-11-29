import os
import re
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFSyntaxError
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfpage import PDFPage


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
                        key_decoded = key.decode("utf-8", errors="ignore")
                        value_decoded = value.decode("utf-8", errors="ignore")
                        print(f"  {key_decoded}: {value_decoded}")
                        
                        # Verificar informações adicionais nos metadados
                        if "creator" in key_decoded.lower():
                            print(f"    → Programa usado para criar: {value_decoded}")
                        if "producer" in key_decoded.lower():
                            print(f"    → Versão do programa: {value_decoded}")
                        if "os" in key_decoded.lower():
                            print(f"    → Sistema operacional identificado: {value_decoded}")
                        if "location" in key_decoded.lower() or "path" in key_decoded.lower():
                            print(f"    → Caminho ou localização antes de ser salvo: {value_decoded}")
            else:
                print("  Nenhum metadado encontrado.")
    except PDFSyntaxError as e:
        print(f"Erro ao analisar metadados: {e}\n")
    except Exception as e:
        print(f"Erro geral ao analisar metadados: {e}\n")

    # Verificar a presença de elementos suspeitos
    print("\nAnálise de Elementos Suspeitos:")
    try:
        with open(file_path, 'rb') as f:
            parser = PDFParser(f)
            document = PDFDocument(parser)

            suspicious_elements = {
                "/JavaScript": 0,
                "/JS": 0,
                "/AA": 0,
                "/OpenAction": 0,
                "/EmbeddedFile": 0,
                "/RichMedia": 0,
                "/Launch": 0
            }

            for page in PDFPage.create_pages(document):
                if page.annots:
                    annotations = page.annots.resolve()
                    for key in suspicious_elements.keys():
                        if key in annotations:
                            suspicious_elements[key] += 1

            for key, count in suspicious_elements.items():
                if count > 0:
                    print(f"  {key}: {count} ocorrência(s) encontrada(s)")
    except Exception as e:
        print(f"Erro ao verificar elementos suspeitos: {e}\n")

    # Extrair texto (limitado a 500 caracteres)
    print("\nExtração de Texto do PDF:")
    try:
        text = extract_text(file_path)
        if text.strip():
            print(f"Texto extraído (primeiros 500 caracteres):\n{text[:500]}...\n")
            
            # Procurar por e-mails no texto
            print("Procurando por e-mails no conteúdo do PDF:")
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
            if emails:
                print(f"  E-mails encontrados: {', '.join(emails)}")
            else:
                print("  Nenhum e-mail encontrado.")

            # Procurar por versões de sistemas operacionais ou softwares
            print("\nProcurando por informações de sistema operacional ou software:")
            os_info = re.findall(r'(Windows|Linux|macOS|Ubuntu|Fedora|Android|iOS)[\s\w\d.]*', text, re.IGNORECASE)
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
