import ctypes
import os
from ctypes import wintypes, windll, POINTER, Structure, c_char_p, c_void_p, c_ulong, c_wchar_p
from ctypes.wintypes import DWORD, HANDLE, LPCSTR

class CERT_CONTEXT(Structure):
    _fields_ = [
        ("dwCertEncodingType", DWORD),
        ("pbCertEncoded", c_void_p),
        ("cbCertEncoded", DWORD),
        ("pCertInfo", c_void_p),
        ("hCertStore", HANDLE),
    ]

PCERT_CONTEXT = POINTER(CERT_CONTEXT)

class CRYPT_DATA_BLOB(Structure):
    _fields_ = [
        ("cbData", DWORD),
        ("pbData", c_void_p),
    ]

PCRYPT_DATA_BLOB = POINTER(CRYPT_DATA_BLOB)

crypt32 = windll.crypt32
crypt32.CertOpenSystemStoreW.argtypes = [wintypes.HANDLE, wintypes.LPCWSTR]
crypt32.CertOpenSystemStoreW.restype = HANDLE
crypt32.CertEnumCertificatesInStore.argtypes = [HANDLE, PCERT_CONTEXT]
crypt32.CertEnumCertificatesInStore.restype = PCERT_CONTEXT
crypt32.CertGetNameStringW.argtypes = [PCERT_CONTEXT, DWORD, DWORD, c_void_p, wintypes.LPWSTR, DWORD]
crypt32.CertGetNameStringW.restype = DWORD
crypt32.CertCloseStore.argtypes = [HANDLE, DWORD]
crypt32.CertCloseStore.restype = wintypes.BOOL
crypt32.CertDeleteCertificateFromStore.argtypes = [PCERT_CONTEXT]
crypt32.CertDeleteCertificateFromStore.restype = wintypes.BOOL
crypt32.CertDuplicateCertificateContext.argtypes = [PCERT_CONTEXT]
crypt32.CertDuplicateCertificateContext.restype = PCERT_CONTEXT
crypt32.CertFreeCertificateContext.argtypes = [PCERT_CONTEXT]
crypt32.CertFreeCertificateContext.restype = wintypes.BOOL
crypt32.PFXImportCertStore.argtypes = [POINTER(CRYPT_DATA_BLOB), wintypes.LPCWSTR, DWORD]
crypt32.PFXImportCertStore.restype = HANDLE
crypt32.CertAddCertificateContextToStore.argtypes = [HANDLE, PCERT_CONTEXT, DWORD, POINTER(PCERT_CONTEXT)]
crypt32.CertAddCertificateContextToStore.restype = wintypes.BOOL

CERT_NAME_SIMPLE_DISPLAY_TYPE = 4
CERT_STORE_CLOSE_FLAG = 0
CERT_STORE_ADD_REPLACE_EXISTING = 3
CRYPT_EXPORTABLE = 0x00000001
PKCS12_IMPORT_RESERVED_MASK = 0xffff0000

def listar_certificados():
    """Lista todos os certificados digitais instalados no repositório 'MY' (Personal)"""
    
    store = crypt32.CertOpenSystemStoreW(0, "MY")
    
    if not store:
        print("Erro ao abrir o repositório de certificados.")
        return
    
    print("Certificados digitais instalados no repositório 'MY' (Personal):\n")
    
    cert_context = None
    count = 0
    
    while True:
        cert_context = crypt32.CertEnumCertificatesInStore(store, cert_context)
        
        if not cert_context:
            break
        
        count += 1
        
        buffer_size = crypt32.CertGetNameStringW(
            cert_context,
            CERT_NAME_SIMPLE_DISPLAY_TYPE,
            0,
            None,
            None,
            0
        )
        
        if buffer_size > 1:
            buffer = ctypes.create_unicode_buffer(buffer_size)
            crypt32.CertGetNameStringW(
                cert_context,
                CERT_NAME_SIMPLE_DISPLAY_TYPE,
                0,
                None,
                buffer,
                buffer_size
            )
            cert_name = buffer.value
        else:
            cert_name = "Nome não disponível"
        
        print(f"{count}. {cert_name}")
    
    crypt32.CertCloseStore(store, CERT_STORE_CLOSE_FLAG)
    
    if count == 0:
        print("\nNenhum certificado encontrado no repositório 'MY'.")
    else:
        print(f"\nTotal de certificados encontrados: {count}")

def obter_nome_certificado(cert_context):
    """Obtém o nome de um certificado"""
    buffer_size = crypt32.CertGetNameStringW(
        cert_context,
        CERT_NAME_SIMPLE_DISPLAY_TYPE,
        0,
        None,
        None,
        0
    )
    
    if buffer_size > 1:
        buffer = ctypes.create_unicode_buffer(buffer_size)
        crypt32.CertGetNameStringW(
            cert_context,
            CERT_NAME_SIMPLE_DISPLAY_TYPE,
            0,
            None,
            buffer,
            buffer_size
        )
        return buffer.value
    else:
        return "Nome não disponível"

def desinstalar_todos_certificados(confirmar=True):
    """
    Desinstala todos os certificados digitais do repositório 'MY' (Personal)
    
    ATENÇÃO: Esta operação é IRREVERSÍVEL e pode afetar aplicações que dependem
    desses certificados. Use com cuidado!
    
    Args:
        confirmar (bool): Se True, solicita confirmação antes de desinstalar
    """
    
    print("=" * 70)
    print("ATENÇÃO: OPERAÇÃO PERIGOSA")
    print("=" * 70)
    print("Esta função irá DESINSTALAR TODOS os certificados digitais")
    print("do repositório 'MY' (Personal) do Windows.")
    print("\nEsta operação é IRREVERSÍVEL!")
    print("Certificados desinstalados não podem ser recuperados facilmente.")
    print("=" * 70)
    
    if confirmar:
        resposta = input("\nDeseja realmente continuar? (digite 'SIM' para confirmar): ")
        if resposta.upper() != "SIM":
            print("\nOperação cancelada pelo usuário.")
            return
    
    store = crypt32.CertOpenSystemStoreW(0, "MY")
    
    if not store:
        print("Erro ao abrir o repositório de certificados.")
        return
    
    print("\nIniciando desinstalação dos certificados...\n")
    
    certificados_removidos = []
    certificados_falharam = []
    certificados_para_deletar = []
    cert_context = None
    
    while True:
        cert_context = crypt32.CertEnumCertificatesInStore(store, cert_context)
        
        if not cert_context:
            break
        
        cert_duplicado = crypt32.CertDuplicateCertificateContext(cert_context)
        
        if cert_duplicado:
            cert_name = obter_nome_certificado(cert_context)
            certificados_para_deletar.append((cert_duplicado, cert_name))
    
    for cert_duplicado, cert_name in certificados_para_deletar:
        if crypt32.CertDeleteCertificateFromStore(cert_duplicado):
            certificados_removidos.append(cert_name)
            print(f"✓ Removido: {cert_name}")
        else:
            error_code = ctypes.get_last_error()
            certificados_falharam.append((cert_name, error_code))
            print(f"✗ Falha ao remover: {cert_name} (Erro: {error_code})")
        
        crypt32.CertFreeCertificateContext(cert_duplicado)
    
    crypt32.CertCloseStore(store, CERT_STORE_CLOSE_FLAG)
    
    print("\n" + "=" * 70)
    print("RESUMO DA OPERAÇÃO")
    print("=" * 70)
    print(f"Certificados removidos com sucesso: {len(certificados_removidos)}")
    print(f"Certificados que falharam: {len(certificados_falharam)}")
    
    if certificados_removidos:
        print("\nCertificados removidos:")
        for i, nome in enumerate(certificados_removidos, 1):
            print(f"  {i}. {nome}")
    
    if certificados_falharam:
        print("\nCertificados que falharam ao remover:")
        for i, (nome, erro) in enumerate(certificados_falharam, 1):
            print(f"  {i}. {nome} (Erro: {erro})")
    
    print("=" * 70)

def instalar_certificado_pfx(caminho_pfx, senha=None, substituir_existente=True):
    """
    Instala um certificado digital a partir de um arquivo .pfx no Windows
    
    Args:
        caminho_pfx (str): Caminho completo para o arquivo .pfx
        senha (str, optional): Senha do arquivo .pfx. Se None, será solicitada
        substituir_existente (bool): Se True, substitui certificado existente com mesmo nome
    
    Returns:
        bool: True se a instalação foi bem-sucedida, False caso contrário
    """
    
    if not os.path.exists(caminho_pfx):
        print(f"Erro: Arquivo não encontrado: {caminho_pfx}")
        return False
    
    if not caminho_pfx.lower().endswith('.pfx'):
        print(f"Erro: O arquivo deve ter extensão .pfx")
        return False
    
    if senha is None:
        import getpass
        senha = getpass.getpass("Digite a senha do certificado .pfx: ")
    
    print(f"\nInstalando certificado: {os.path.basename(caminho_pfx)}")
    print("=" * 70)
    
    try:
        with open(caminho_pfx, 'rb') as f:
            pfx_data = f.read()
    except Exception as e:
        print(f"Erro ao ler o arquivo .pfx: {e}")
        return False
    
    pfx_buffer = (ctypes.c_ubyte * len(pfx_data)).from_buffer(bytearray(pfx_data))
    pfx_blob = CRYPT_DATA_BLOB()
    pfx_blob.cbData = len(pfx_data)
    pfx_blob.pbData = ctypes.cast(pfx_buffer, c_void_p)
    
    senha_unicode = c_wchar_p(senha) if senha else None
    
    pfx_store = crypt32.PFXImportCertStore(
        ctypes.byref(pfx_blob),
        senha_unicode,
        0
    )
    
    if not pfx_store:
        error_code = ctypes.get_last_error()
        print(f"Erro ao importar o arquivo .pfx (Código: {error_code})")
        
        if error_code == 87:
            print("Possível causa: Senha incorreta ou arquivo .pfx corrompido")
        elif error_code == 13:
            print("Possível causa: Arquivo .pfx inválido ou corrompido")
        
        return False
    
    system_store = crypt32.CertOpenSystemStoreW(0, "MY")
    
    if not system_store:
        print("Erro ao abrir o repositório de certificados do sistema.")
        crypt32.CertCloseStore(pfx_store, CERT_STORE_CLOSE_FLAG)
        return False
    
    certificados_instalados = []
    cert_context = None
    
    while True:
        cert_context = crypt32.CertEnumCertificatesInStore(pfx_store, cert_context)
        
        if not cert_context:
            break
        
        cert_name = obter_nome_certificado(cert_context)
        cert_duplicado = crypt32.CertDuplicateCertificateContext(cert_context)
        
        if cert_duplicado:
            flag = CERT_STORE_ADD_REPLACE_EXISTING if substituir_existente else 0
            resultado = crypt32.CertAddCertificateContextToStore(
                system_store,
                cert_duplicado,
                flag,
                None
            )
            
            if resultado:
                certificados_instalados.append(cert_name)
                print(f"✓ Instalado: {cert_name}")
            else:
                error_code = ctypes.get_last_error()
                print(f"✗ Falha ao instalar: {cert_name} (Erro: {error_code})")
            
            crypt32.CertFreeCertificateContext(cert_duplicado)
    
    crypt32.CertCloseStore(pfx_store, CERT_STORE_CLOSE_FLAG)
    crypt32.CertCloseStore(system_store, CERT_STORE_CLOSE_FLAG)
    
    print("\n" + "=" * 70)
    if certificados_instalados:
        print("INSTALAÇÃO CONCLUÍDA COM SUCESSO")
        print("=" * 70)
        print(f"Certificados instalados: {len(certificados_instalados)}")
        for i, nome in enumerate(certificados_instalados, 1):
            print(f"  {i}. {nome}")
        print("=" * 70)
        return True
    else:
        print("NENHUM CERTIFICADO FOI INSTALADO")
        print("=" * 70)
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--desinstalar":
        desinstalar_todos_certificados()
    elif len(sys.argv) > 1 and sys.argv[1] == "--instalar":
        if len(sys.argv) < 3:
            print("Uso: python manipulador_certificado.py --instalar <caminho_do_arquivo.pfx> [senha]")
            print("\nExemplo:")
            print("  python manipulador_certificado.py --instalar certificado.pfx")
            print("  python manipulador_certificado.py --instalar certificado.pfx minha_senha")
        else:
            caminho_pfx = sys.argv[2]
            senha = sys.argv[3] if len(sys.argv) > 3 else None
            instalar_certificado_pfx(caminho_pfx, senha)
    else:
        listar_certificados()
        print("\n" + "=" * 70)
        print("Comandos disponíveis:")
        print("  python manipulador_certificado.py                    - Lista certificados")
        print("  python manipulador_certificado.py --instalar <arquivo.pfx> [senha]")
        print("  python manipulador_certificado.py --desinstalar       - Remove todos os certificados")
        print("=" * 70)
