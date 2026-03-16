import json
from collections import Counter
from pathlib import Path

def verificar_duplicidades():
    """
    Lê o arquivo debitos_processados.json e verifica se há duplicidades
    no campo idDocumentoFiscal.
    """
    # Caminho do arquivo JSON
    arquivo_json = Path(__file__).parent / "debitos_processados.json"
    
    print(f"Lendo arquivo: {arquivo_json}")
    
    # Lê o arquivo JSON
    with open(arquivo_json, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Extrai todos os valores de idDocumentoFiscal
    id_documentos = []
    
    if 'dados' in dados and isinstance(dados['dados'], list):
        for registro in dados['dados']:
            if 'idDocumentoFiscal' in registro:
                id_documentos.append(registro['idDocumentoFiscal'])
    
    print(f"\nTotal de registros processados: {len(id_documentos)}")
    
    # Conta as ocorrências de cada idDocumentoFiscal
    contador = Counter(id_documentos)
    
    # Identifica duplicidades (valores que aparecem mais de uma vez)
    duplicados = {id_doc: count for id_doc, count in contador.items() if count > 1}
    
    # Exibe os resultados
    print(f"\nTotal de valores únicos de idDocumentoFiscal: {len(contador)}")
    print(f"Total de valores duplicados: {len(duplicados)}")
    
    if duplicados:
        print("\n=== VALORES DUPLICADOS ===")
        total_duplicatas = 0
        for id_doc, count in sorted(duplicados.items(), key=lambda x: x[1], reverse=True):
            print(f"  {id_doc}: aparece {count} vez(es)")
            total_duplicatas += (count - 1)  # Conta apenas as duplicatas extras
        
        print(f"\nTotal de registros duplicados (excluindo primeira ocorrência): {total_duplicatas}")
    else:
        print("\n✓ Nenhuma duplicidade encontrada! Todos os valores de idDocumentoFiscal são únicos.")
    
    return duplicados

if __name__ == "__main__":
    verificar_duplicidades()
