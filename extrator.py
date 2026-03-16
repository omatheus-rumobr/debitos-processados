from pathlib import Path
import json

# Caminho do arquivo JSON
arquivo_json = Path("debitos_processados.json")

# Ler o arquivo JSON
with open(arquivo_json, 'r', encoding='utf-8') as f:
    dados = json.load(f)

# Extrair todos os valores de idDocumentoFiscal
ids_documentos = []
for item in dados.get("dados", []):
    if "idDocumentoFiscal" in item:
        ids_documentos.append(item["idDocumentoFiscal"])

# Formatar os valores com aspas simples e colocar dentro de parênteses
valores_formatados = "(" + ", ".join([f"'{id_doc}'" for id_doc in ids_documentos]) + ")"

# Salvar em arquivo txt
arquivo_saida = Path("id_documentos_fiscais.txt")
with open(arquivo_saida, 'w', encoding='utf-8') as f:
    f.write(valores_formatados)

print(f"Total de IDs extraídos: {len(ids_documentos)}")
print(f"Arquivo salvo em: {arquivo_saida}")
