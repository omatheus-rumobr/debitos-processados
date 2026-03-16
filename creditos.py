import undetected_chromedriver as uc
from dotenv import load_dotenv
import os
import json
from time import sleep
import requests
import math

load_dotenv()

VERSAO_CHROME = int(os.getenv('VERSAO_CHROME'))
URL_BASE = os.getenv('URL_BASE')
URL_CREDITOS = os.getenv('URL_CREDITOS')

MES = int(os.getenv('MES'))
ANO = int(os.getenv('ANO'))
POR_PAGINA = int(os.getenv('POR_PAGINA'))

params_creditos = {
    "porPagina": POR_PAGINA,
    "tipoCredito": "NORMAL",
    "mes": MES,
    "ano": ANO
}

def leitura_json(arquivo_json):
    with open(arquivo_json, 'r', encoding='utf-8') as f:
        cookies = json.load(f)
    return cookies

def escrita_json(arquivo_json, dados):
    with open(arquivo_json, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

driver = uc.Chrome(version_main=VERSAO_CHROME)

try:
    cookies = leitura_json('cookies.json')
    driver.get(URL_BASE)
    driver.maximize_window()
    
    for cookie in cookies:
        cookie_to_add = {
            'name': cookie['name'],
            'value': cookie['value'],
            'domain': cookie['domain'],
            'path': cookie['path'],
            'secure': cookie.get('secure', False),
            'httpOnly': cookie.get('httpOnly', False)
        }

        if 'sameSite' in cookie:
            cookie_to_add['sameSite'] = cookie['sameSite']
        
        try:
            driver.add_cookie(cookie_to_add)
        except Exception as e:
            print(f"Erro ao adicionar cookie {cookie['name']}: {e}")
    
    driver.get(URL_BASE)
    
    sleep(10)
    
    cookies_sessao = driver.get_cookies()
    cookies_dict = {}
    for cookie in cookies_sessao:
        cookies_dict[cookie['name']] = cookie['value']
    
    if not os.path.exists('creditos_processados.json'):
        
        # Buscar idApuração
        print(f"\n{'='*60}")
        print(f"Buscando idApuracao para {MES:02d}/{ANO}...")
        print(f"{'='*60}")
        
        url_apuracoes = "https://consumo.tributos.gov.br/servico/cbs-apuracao/api/apuracoes/contribuintes"
        params_apuracoes = {
            'pagina': 0,
            'porPagina': 100,
            'tipoTributo': 0
        }
        
        try:
            response_apuracoes = requests.get(
                url=url_apuracoes,
                cookies=cookies_dict,
                params=params_apuracoes
            )
            
            if response_apuracoes.status_code != 200:
                print(f"Erro na requisição de apurações: {response_apuracoes.text}")
                id_apuracao = None
            else:
                resultado_apuracoes = response_apuracoes.json()
                dados_apuracoes = resultado_apuracoes.get('dados', [])
                
                # Buscar o idApuracao correspondente ao mês/ano especificado
                id_apuracao = None
                mes_formatado = f"{ANO}-{MES:02d}-01"  # Formato: YYYY-MM-DD
                
                for apuracao in dados_apuracoes:
                    data_inicial = apuracao.get('dataInicial', '')
                    # Comparar apenas ano e mês (primeiros 7 caracteres: YYYY-MM)
                    if data_inicial[:7] == mes_formatado[:7]:
                        id_apuracao = apuracao.get('idApuracao')
                        situacao = apuracao.get('situacao', '')
                        valor = apuracao.get('valorApuracao', 0)
                        print(f"idApuracao encontrado: {id_apuracao}")
                        print(f"Situação: {situacao}")
                        print(f"Valor: {valor}")
                        break
                
                if id_apuracao is None:
                    print(f"⚠️  Nenhum idApuracao encontrado para {MES:02d}/{ANO}")
                    print("Apurações disponíveis:")
                    for apuracao in dados_apuracoes:
                        print(f"  - {apuracao.get('dataInicial')}: idApuracao={apuracao.get('idApuracao')}, situação={apuracao.get('situacao')}")
                else:
                    # Atualizar o params_creditos com o idApuracao encontrado
                    params_creditos['idApuracao'] = id_apuracao
                    print(f"✓ idApuracao {id_apuracao} salvo para uso nas requisições")
                    
        except Exception as e:
            print(f"Erro ao buscar idApuracao: {e}")
            id_apuracao = None
        
        if id_apuracao is None:
            print("⚠️  Não foi possível obter o idApuracao. Continuando sem ele...")
        
        sleep(5)
        # Recuperar os créditos
        
        # endpoint_url_debitos = f"{URL_BASE}{URL_CREDITOS}"
        endpoint_url_creditos = "https://consumo.tributos.gov.br/servico/cbs-apuracao/api/creditos/nao_apropriados/contribuintes"
        # params_creditos = {
        #     "porPagina": 100,
        #     "idApuracao": id_apuracao,
        #     "tipoCredito": "NORMAL",
        #     "mes": MES,
        #     "ano": ANO
        # }
        params_primeira = params_creditos.copy()
        params_primeira['pagina'] = 0
        params_primeira['idApuracao'] = id_apuracao
        
        response = requests.get(
            url=endpoint_url_creditos, 
            cookies=cookies_dict, 
            params=params_primeira
        )
        
        if response.status_code != 200:
            print(f"Erro na requisição: {response.text}")
        else:
            try:
                resultado_json_creditos = response.json()
            except json.JSONDecodeError:
                print(f"Erro ao parsear JSON: {response.text}")
                resultado_json_creditos = None
            
            if resultado_json_creditos:
                    meta = resultado_json_creditos.get('meta', {})
                    total = meta.get('total', 0)
                    existe_proxima_pagina = meta.get('existeProximaPagina', False)
                    
                    total_paginas = math.ceil(total / 1000)
                    
                    todos_dados = []
                    
                    dados_primeira_pagina = resultado_json_creditos.get('dados', [])
                    todos_dados.extend(dados_primeira_pagina)
                    
                    for pagina in range(1, total_paginas):
                        params = params_creditos.copy()
                        params['pagina'] = pagina
                        
                        response = requests.get(
                            url=endpoint_url_creditos, 
                            cookies=cookies_dict, 
                            params=params
                        )
                        
                        if response.status_code != 200:
                            print(f"Erro na requisição da página {pagina}: {response.text}")
                            continue
                        
                        try:
                            resultado_pagina = response.json()
                            dados_pagina = resultado_pagina.get('dados', [])
                            todos_dados.extend(dados_pagina)
                            print(f"Página {pagina} processada: {len(dados_pagina)} registros (em memória)")
                        except json.JSONDecodeError:
                            print(f"Erro ao parsear JSON da página {pagina}: {response.text}")
                            continue

                    resultado_final = {
                        'dados': todos_dados,
                        'meta': {
                            'total_registros': len(todos_dados),
                            'total_paginas_processadas': total_paginas,
                            'total_original': total
                        }
                    }
                    
                    escrita_json("creditos_processados.json", resultado_final)
                    
                    print(f"\n{'='*60}")
                    print(f"Processamento concluído!")
                    print(f"Total de registros coletados: {len(todos_dados)}")
                    print(f"Total de páginas processadas: {total_paginas}")
                    print(f"{'='*60}")

except Exception as e:
    print(f"Erro: {e}")

finally:
    driver.quit()
