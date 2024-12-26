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
            document = PDFDocument(parser)
            return document.encryption  # Verifica criptografia corretamente
    except Exception as e:
        print(Fore.RED + f"Error checking PDF encryption: {e}")
        return True  # Assume criptografado em caso de erro

def open_pdf_with_password(file_path):
    """
    Tenta abrir um PDF criptografado solicitando a senha e retorna a senha correta.
    """
    for attempt in range(3):
        password = input(Fore.CYAN + "Enter the PDF password: ").strip()
        try:
            with open(file_path, 'rb') as f:
                parser = PDFParser(f)
                PDFDocument(parser, password=password)  # Tenta desbloquear com a senha
                print(Fore.GREEN + "Password accepted!")
                return password  # Retorna a senha correta
        except PDFEncryptionError:
            print(Fore.RED + "Incorrect password. Try again.")
    print(Fore.RED + "Failed to unlock the PDF after 3 attempts.")
    return None
