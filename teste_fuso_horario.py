from pathlib import Path
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import Counter

# Caminho do arquivo JSON
arquivo_json = Path("debitos_processados.json")

# Ler o arquivo JSON
print("Lendo o arquivo JSON...")
with open(arquivo_json, 'r', encoding='utf-8') as f:
    dados = json.load(f)

# Fuso horário de São Paulo
fuso_sp = ZoneInfo("America/Sao_Paulo")

# Converter datas e atualizar os registros
print("Convertendo datas para o fuso horário de São Paulo...")
registros_processados = 0

for registro in dados["dados"]:
    # Converter dataInclusao
    if "dataInclusao" in registro and registro["dataInclusao"]:
        try:
            # Parse da data UTC
            data_utc = datetime.fromisoformat(registro["dataInclusao"].replace('Z', '+00:00'))
            # Converter para São Paulo
            data_sp = data_utc.astimezone(fuso_sp)
            # Atualizar o registro com a data convertida (formato ISO com fuso)
            registro["dataInclusao"] = data_sp.isoformat()
        except Exception as e:
            print(f"Erro ao converter dataInclusao: {e}")
    
    # Converter dataEmissao
    if "dataEmissao" in registro and registro["dataEmissao"]:
        try:
            # Parse da data UTC
            data_utc = datetime.fromisoformat(registro["dataEmissao"].replace('Z', '+00:00'))
            # Converter para São Paulo
            data_sp = data_utc.astimezone(fuso_sp)
            # Atualizar o registro com a data convertida (formato ISO com fuso)
            registro["dataEmissao"] = data_sp.isoformat()
        except Exception as e:
            print(f"Erro ao converter dataEmissao: {e}")
    
    registros_processados += 1
    if registros_processados % 1000 == 0:
        print(f"Processados {registros_processados} registros...")

print(f"Total de registros processados: {registros_processados}")

# Salvar o arquivo atualizado
print("Salvando arquivo atualizado...")
with open(arquivo_json, 'w', encoding='utf-8') as f:
    json.dump(dados, f, ensure_ascii=False, indent=4)

print("Arquivo salvo com sucesso!")

# Análise de meses e anos
print("\n" + "="*50)
print("ANÁLISE DE MESES E ANOS")
print("="*50)

# Contadores para meses/anos
contador_mes_ano = Counter()
contador_ano = Counter()

for registro in dados["dados"]:
    # Usar dataEmissao como referência principal (ou dataInclusao se não houver)
    data_referencia = None
    
    if "dataEmissao" in registro and registro["dataEmissao"]:
        try:
            data_referencia = datetime.fromisoformat(registro["dataEmissao"])
        except:
            pass
    
    if not data_referencia and "dataInclusao" in registro and registro["dataInclusao"]:
        try:
            data_referencia = datetime.fromisoformat(registro["dataInclusao"])
        except:
            pass
    
    if data_referencia:
        # Formato: YYYY-MM
        mes_ano = data_referencia.strftime("%Y-%m")
        ano = data_referencia.strftime("%Y")
        
        contador_mes_ano[mes_ano] += 1
        contador_ano[ano] += 1

# Exibir resultados por mês/ano
print("\nRegistros por Mês/Ano:")
print("-" * 50)
for mes_ano in sorted(contador_mes_ano.keys()):
    ano, mes = mes_ano.split('-')
    nome_mes = {
        '01': 'Janeiro', '02': 'Fevereiro', '03': 'Março', '04': 'Abril',
        '05': 'Maio', '06': 'Junho', '07': 'Julho', '08': 'Agosto',
        '09': 'Setembro', '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro'
    }.get(mes, mes)
    print(f"{nome_mes}/{ano}: {contador_mes_ano[mes_ano]:,} registros")

# Exibir resultados por ano
print("\nRegistros por Ano:")
print("-" * 50)
for ano in sorted(contador_ano.keys()):
    print(f"{ano}: {contador_ano[ano]:,} registros")

# Resumo geral
print("\n" + "="*50)
print("RESUMO GERAL")
print("="*50)
print(f"Total de registros: {len(dados['dados']):,}")
print(f"Total de meses diferentes: {len(contador_mes_ano)}")
print(f"Total de anos diferentes: {len(contador_ano)}")
print(f"Período: {min(contador_mes_ano.keys())} até {max(contador_mes_ano.keys())}")
