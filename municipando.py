import pandas as pd
import json

# Carregar o mapeamento de estados para siglas
with open('estados_siglas.json', 'r', encoding='utf-8') as f:
    estados_data = json.load(f)

# Criar dicionário de mapeamento: nome do estado -> sigla
estado_para_sigla = {item['estado']: item['sigla'] for item in estados_data}

# Ler o arquivo XLS
# O cabeçalho está na linha 6 (índice 6)
# Os dados começam na linha 7
print("Lendo arquivo XLS...")
df = pd.read_excel('RELATORIO_DTB_BRASIL_2024_MUNICIPIOS.xls', header=None)

# Encontrar a linha do cabeçalho (linha 6, índice 6)
# Definir os nomes das colunas manualmente baseado na estrutura conhecida
df.columns = df.iloc[6].values  # Usar a linha 6 como cabeçalho
df = df.iloc[7:].reset_index(drop=True)  # Remover as primeiras 7 linhas e resetar índice

# Verificar se as colunas existem
colunas_existentes = df.columns.tolist()
print(f"Colunas encontradas: {colunas_existentes}")

# Identificar as colunas necessárias
nome_uf_col = None
codigo_col = None
nome_municipio_col = None

for col in df.columns:
    col_str = str(col).strip()
    col_lower = col_str.lower()
    
    # Procurar coluna Nome_UF
    if 'nome_uf' in col_lower or (col_str == 'Nome_UF'):
        nome_uf_col = col
    
    # Procurar coluna Código Município Completo
    if 'código município completo' in col_lower or 'codigo municipio completo' in col_lower:
        codigo_col = col
    
    # Procurar coluna Nome_Município
    if 'nome_município' in col_lower or 'nome_municipio' in col_lower:
        nome_municipio_col = col

print(f"Colunas identificadas:")
print(f"  Nome_UF: {nome_uf_col}")
print(f"  Código Município Completo: {codigo_col}")
print(f"  Nome_Município: {nome_municipio_col}")

# Verificar se todas as colunas foram encontradas
if nome_uf_col is None or codigo_col is None or nome_municipio_col is None:
    print("\nErro: Não foi possível encontrar todas as colunas necessárias!")
    print("Colunas disponíveis:")
    for i, col in enumerate(df.columns):
        print(f"  {i}: '{col}'")
    raise ValueError("Colunas necessárias não encontradas no arquivo")

# Extrair apenas as colunas necessárias
df_selecionado = df[[nome_uf_col, codigo_col, nome_municipio_col]].copy()

# Remover linhas com valores nulos
df_selecionado = df_selecionado.dropna()

# Converter código para string e remover espaços
df_selecionado[codigo_col] = df_selecionado[codigo_col].astype(str).str.strip()

# Mapear nome do estado para sigla
def obter_sigla_uf(nome_estado):
    """Converte nome do estado para sigla"""
    if pd.isna(nome_estado):
        return None
    nome_estado_str = str(nome_estado).strip()
    return estado_para_sigla.get(nome_estado_str, None)

# Aplicar o mapeamento
df_selecionado['sigla_uf'] = df_selecionado[nome_uf_col].apply(obter_sigla_uf)

# Remover linhas onde não foi possível mapear a sigla
df_selecionado = df_selecionado.dropna(subset=['sigla_uf'])

# Criar lista de dicionários no formato desejado
resultado = []
for _, row in df_selecionado.iterrows():
    resultado.append({
        'sigla_uf': row['sigla_uf'],
        'codigo': str(row[codigo_col]).strip(),
        'nome': str(row[nome_municipio_col]).strip()
    })

# Salvar em arquivo JSON
output_file = 'codigo_nome_municipios_com_sigla.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(resultado, f, ensure_ascii=False, indent=2)

print(f"\nProcessamento concluído!")
print(f"Total de municípios processados: {len(resultado)}")
print(f"Arquivo salvo em: {output_file}")

# Mostrar alguns exemplos
print("\nPrimeiros 5 registros:")
for i, item in enumerate(resultado[:5]):
    print(f"{i+1}. {item}")
