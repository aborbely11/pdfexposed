from colorama import Fore
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument, PDFEncryptionError
import re
import os
import hashlib
from datetime import datetime

def decode_with_fallback(value):
    """
    Decodifica um valor de bytes usando uma lista de encodings comuns.
    """
    ENCODINGS = ['utf-8', 'latin-1', 'utf-16', 'utf-16le', 'utf-16be', 'ascii', 'cp1252']
    for encoding in ENCODINGS:
        try:
            return value.decode(encoding)
        except (UnicodeDecodeError, AttributeError):
            continue
    return "Not Found"

def calculate_file_hashes(file_path):
    """
    Calcula os hashes MD5 e SHA256 de um arquivo.
    """
    md5_hash = hashlib.md5()
    sha256_hash = hashlib.sha256()

    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
                sha256_hash.update(chunk)
        return md5_hash.hexdigest(), sha256_hash.hexdigest()
    except Exception as e:
        return f"Error: {e}", f"Error: {e}"

def get_file_timestamps(file_path):
    """
    Retorna informações de data e hora do arquivo.
    """
    try:
        stats = os.stat(file_path)
        modification_time = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        access_time = datetime.fromtimestamp(stats.st_atime).strftime('%Y-%m-%d %H:%M:%S')
        inode_change_time = datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
        return modification_time, access_time, inode_change_time
    except Exception as e:
        return f"Error: {e}", None, None

def check_integrity(file_path, password=None):
    """
    Verifica possíveis adulterações no documento PDF.
    """
    print(Fore.CYAN + "\nChecking document integrity...\n")

    try:
        # Tamanho do arquivo
        file_size = os.path.getsize(file_path)
        print(Fore.YELLOW + f"\nFile Size: {file_size} bytes")

        # Hashes do arquivo
        md5_hash, sha256_hash = calculate_file_hashes(file_path)
        print(Fore.YELLOW + f"MD5: {md5_hash}")
        print(Fore.YELLOW + f"SHA256: {sha256_hash}")

        # Timestamps do arquivo
        modification_time, access_time, inode_change_time = get_file_timestamps(file_path)
        print(Fore.YELLOW + f"File Modification Date/Time: {modification_time}")
        print(Fore.YELLOW + f"File Access Date/Time: {access_time}")
        print(Fore.YELLOW + f"File Inode Change Date/Time: {inode_change_time}")

        with open(file_path, 'rb') as f:
            parser = PDFParser(f)
            document = PDFDocument(parser, password=password)

            # Inicializa as variáveis de metadados
            creation_date = "Not Found"
            modification_date = "Not Found"
            author = "Not Found"
            producer = "Not Found"
            title = "Not Found"
            last_modified_by = "Not Found"
            creator_tool = "Not Found"

            if document.info:
                for metadata in document.info:
                    for key, value in metadata.items():
                        key_decoded = str(key)
                        value_decoded = decode_with_fallback(value)

                        if "creationdate" in key_decoded.lower():
                            creation_date = value_decoded
                        elif "moddate" in key_decoded.lower():
                            modification_date = value_decoded
                        elif "author" in key_decoded.lower():
                            author = value_decoded
                        elif "producer" in key_decoded.lower():
                            producer = value_decoded
                        elif "title" in key_decoded.lower():
                            title = value_decoded
                        elif "lastmodifiedby" in key_decoded.lower():
                            last_modified_by = value_decoded
                        elif "creatortool" in key_decoded.lower():
                            creator_tool = value_decoded

            # Exibe as informações principais
            print(Fore.YELLOW + f"Creation Date: {creation_date}")
            print(Fore.YELLOW + f"Modification Date: {modification_date}")

            # Verifica inconsistências e alertas
            if author != "Not Found" and creator_tool != "Not Found" and author != creator_tool:
                print(Fore.RED + f"⚠️ Alert: The document's author ({author}) does not match the creator tool ({creator_tool}).")
            if producer and re.search(r'(Modified|Altered|Edited)', producer, re.IGNORECASE):
                print(Fore.RED + f"⚠️ Alert: The document's producer field indicates it might have been modified ({producer}).")
            if title and re.search(r'(Copy|Duplicate|Altered)', title, re.IGNORECASE):
                print(Fore.RED + f"⚠️ Alert: The document's title suggests it might be a copy or duplicate ({title}).")
            if author != "Not Found" and last_modified_by != "Not Found" and author != last_modified_by:
                print(Fore.RED + f"⚠️ Alert: The document's author ({author}) does not match the last modified by field ({last_modified_by}).")

            # Verifica alterações na data
            if creation_date != modification_date and modification_date != "Not Found":
                print(Fore.RED + f"⚠️ Alert: The document was modified on {modification_date} after its creation on {creation_date}!")

            if creation_date == modification_date:
                print(Fore.GREEN + "✅ No modifications detected in dates.")

    except PDFEncryptionError:
        print(Fore.RED + "Error: Incorrect password provided.")
    except Exception as e:
        print(Fore.RED + f"Error checking integrity: {e}")
