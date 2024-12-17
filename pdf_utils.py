import os
from colorama import Fore
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument, PDFEncryptionError

def is_pdf_encrypted(file_path):
    """
    Verifica se o PDF está criptografado.
    Retorna True se estiver criptografado, False caso contrário.
    """
    try:
        with open(file_path, 'rb') as f:
            parser = PDFParser(f)
            document = PDFDocument(parser)  # Tenta abrir o PDF sem senha
            if document.encryption:  # Corrigido para verificar 'encryption'
                print(Fore.YELLOW + "PDF is marked as encrypted, attempting to verify...")
                try:
                    # Testa se a senha em branco desbloqueia o PDF
                    PDFDocument(parser, password="")
                    print(Fore.GREEN + "PDF does not require a password.")
                    return False  # Não está realmente criptografado
                except PDFEncryptionError:
                    return True  # Requer senha
            return False  # Não criptografado
    except Exception as e:
        print(Fore.RED + f"Error checking PDF encryption: {e}")
        return True  # Assume criptografado em caso de erro

def open_pdf_with_password(file_path):
    """
    Tenta abrir um PDF criptografado solicitando a senha.
    """
    for attempt in range(3):
        password = input(Fore.CYAN + "Enter the PDF password: ").strip()
        try:
            with open(file_path, 'rb') as f:
                parser = PDFParser(f)
                document = PDFDocument(parser, password)
                if not document.encryption:  # Corrigido para 'encryption'
                    print(Fore.GREEN + "Password accepted!")
                    return document
        except PDFEncryptionError:
            print(Fore.RED + "Incorrect password. Try again.")
    print(Fore.RED + "Failed to unlock the PDF after 3 attempts.")
    return None
