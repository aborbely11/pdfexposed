import hashlib
import difflib
from colorama import Fore
from pdfminer.high_level import extract_text
from integrity_utils import calculate_file_hashes, decode_with_fallback
from extract_utils import extract_selected_information

def get_pdf_text(file_path, password=None):
    """
    Extrai o texto de um arquivo PDF sem imprimir a extração.
    """
    try:
        return extract_text(file_path, password=password) or ""
    except Exception as e:
        print(Fore.RED + f"Erro ao extrair texto do PDF {file_path}: {e}")
        return ""

def compare_texts(text1, text2):
    """
    Compara dois textos e exibe apenas as diferenças relevantes.
    """
    if text1 == text2:
        return False  # Nenhuma diferença encontrada
    
    lines1 = text1.splitlines()
    lines2 = text2.splitlines()
    differ = list(difflib.unified_diff(lines1, lines2, lineterm='', fromfile='PDF1', tofile='PDF2'))
    
    if not differ:
        return False
    
    print(Fore.YELLOW + "\nText differences:")
    for line in differ:
        if line.startswith('+') and not line.startswith('+++'):
            print(Fore.GREEN + line)  # Adicionado
        elif line.startswith('-') and not line.startswith('---'):
            print(Fore.RED + line)  # Removido
    return True

def compare_metadata(metadata1, metadata2):
    """
    Compara metadados de dois PDFs e exibe apenas as diferenças relevantes.
    """
    if metadata1 == metadata2:
        return False  # Nenhuma diferença encontrada
    
    changes = []
    for key in sorted(set(metadata1.keys()).union(metadata2.keys())):
        value1 = metadata1.get(key, "Not found")
        value2 = metadata2.get(key, "Not found")
        
        if value1 != value2:
            changes.append(f"{key}: {value1} -> {value2}")
    
    if not changes:
        return False
    
    print(Fore.YELLOW + "\nMetadata differences:")
    for change in changes:
        print(Fore.RED + change)
    return True

def compare_pdfs(file1, file2, password1=None, password2=None):
    """
    Compara dois PDFs, mostrando apenas as diferenças relevantes sem exibir extrações completas.
    """
    print(Fore.CYAN + f"\nComparing {file1} with {file2}...")
    
    # Hashes
    hash1_md5, hash1_sha256 = calculate_file_hashes(file1)
    hash2_md5, hash2_sha256 = calculate_file_hashes(file2)
    print(Fore.YELLOW + f"\nHashes for {file1}:\nMD5: {hash1_md5}\nSHA256: {hash1_sha256}")
    print(Fore.YELLOW + f"\nHashes for {file2}:\nMD5: {hash2_md5}\nSHA256: {hash2_sha256}")
    
    # Comparação de texto
    text1 = get_pdf_text(file1, password1)
    text2 = get_pdf_text(file2, password2)
    text_diff = compare_texts(text1, text2)
    
    # Comparação de metadados sem exibir a extração completa
    extracted1 = extract_selected_information(file1, password1, silent=True)
    extracted2 = extract_selected_information(file2, password2, silent=True)
    metadata1 = extracted1.get("metadata", {}) if extracted1 else {}
    metadata2 = extracted2.get("metadata", {}) if extracted2 else {}
    metadata_diff = compare_metadata(metadata1, metadata2)
    
    if not text_diff and not metadata_diff:
        print(Fore.GREEN + "The PDFs are identical except for their hashes.")
    
    return text_diff or metadata_diff
