import undetected_chromedriver as uc
from dotenv import load_dotenv
from time import sleep
import requests
import json
import math
from os import getenv
from pathlib import Path
from loguru import logger
import traceback

Path("logs").mkdir(parents=True, exist_ok=True)

logger.add(
    "logs/insercao_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="30 days",
    encoding="utf-8",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

load_dotenv()

VERSAO_CHROME = int(getenv('VERSAO_CHROME'))
URL_BASE = getenv('URL_BASE')
URL_DEBITOS = getenv('URL_DEBITOS')

MES = int(getenv('MES'))
ANO = int(getenv('ANO'))
POR_PAGINA = int(getenv('POR_PAGINA'))

params_base = {
    'mes': MES,
    'ano': ANO,
    'porPagina': POR_PAGINA,
    'isAntesConclusao': 'true',
    'isAposConclusao': 'false'
}

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


try:
    driver = uc.Chrome(version_main=VERSAO_CHROME)
    
    cookies = leitura_json('cookies.json')
    
    logger.info(f"Cookies carregados do arquivo cookies.json ({len(cookies)} cookies encontrados)")
    
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
            logger.error(f"Erro ao adicionar cookie {cookie['name']}: {e}")
    
    logger.info("Cookies adicionados à sessão do navegador")
    
    driver.get(URL_BASE)
    
    sleep(5)
    
    cookies_sessao = driver.get_cookies()
    cookies_dict = {}
    for cookie in cookies_sessao:
        cookies_dict[cookie['name']] = cookie['value']
    
    if not Path('debitos_processados.json').exists():
        endpoint_url_debitos = f"{URL_BASE}{URL_DEBITOS}"
        
        params_primeira = params_base.copy()
        params_primeira['pagina'] = 0
        
        response = requests.get(
            url=endpoint_url_debitos, 
            cookies=cookies_dict, 
            params=params_primeira
        )
        
        logger.debug(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"Erro na requisição: {response.text}")
        else:
            try:
                resultado_json = response.json()
            except json.JSONDecodeError:
                logger.error(f"Erro ao parsear JSON: {response.text}")
                resultado_json = None
            
            if resultado_json:
                meta = resultado_json.get('meta', {})
                total = meta.get('total', 0)
                existe_proxima_pagina = meta.get('existeProximaPagina', False)
                
                logger.info(f"Total de registros: {total}")
                logger.info(f"Existe próxima página: {existe_proxima_pagina}")

                total_paginas = math.ceil(total / 1000)
                logger.info(f"Total de páginas a processar: {total_paginas}")
                
                todos_dados = []
                
                dados_primeira_pagina = resultado_json.get('dados', [])
                todos_dados.extend(dados_primeira_pagina)
                logger.info(f"Página 0 processada: {len(dados_primeira_pagina)} registros (em memória)")
                
                for pagina in range(1, total_paginas):
                    params = params_base.copy()
                    params['pagina'] = pagina
                    
                    logger.info(f"Fazendo requisição para página {pagina}...")
                    response = requests.get(
                        url=endpoint_url_debitos, 
                        cookies=cookies_dict, 
                        params=params
                    )
                    
                    if response.status_code != 200:
                        logger.error(f"Erro na requisição da página {pagina}: {response.text}")
                        continue
                    
                    try:
                        resultado_pagina = response.json()
                        dados_pagina = resultado_pagina.get('dados', [])
                        todos_dados.extend(dados_pagina)
                        logger.info(f"Página {pagina} processada: {len(dados_pagina)} registros (em memória)")
                    except json.JSONDecodeError:
                        logger.error(f"Erro ao parsear JSON da página {pagina}: {response.text}")
                        continue
                
                resultado_final = {
                    'dados': todos_dados,
                    'meta': {
                        'total_registros': len(todos_dados),
                        'total_paginas_processadas': total_paginas,
                        'total_original': total
                    }
                }
                
                escrita_json("debitos_processados.json", resultado_final)
                
                logger.success("Processamento concluído!")
                logger.info(f"Total de registros coletados: {len(todos_dados)}")
                logger.info(f"Total de páginas processadas: {total_paginas}")

    if not Path('creditos_processados.json').exists():
        logger.info(f"Buscando idApuracao para {MES:02d}/{ANO}...")
        
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
                logger.error(f"Erro na requisição de apurações: {response_apuracoes.text}")
                id_apuracao = None
            else:
                resultado_apuracoes = response_apuracoes.json()
                dados_apuracoes = resultado_apuracoes.get('dados', [])
                id_apuracao = None
                mes_formatado = f"{ANO}-{MES:02d}-01"
                
                for apuracao in dados_apuracoes:
                    data_inicial = apuracao.get('dataInicial', '')
                    if data_inicial[:7] == mes_formatado[:7]:
                        id_apuracao = apuracao.get('idApuracao')
                        situacao = apuracao.get('situacao', '')
                        valor = apuracao.get('valorApuracao', 0)
                        logger.info(f"idApuracao encontrado: {id_apuracao}")
                        logger.info(f"Situação: {situacao}")
                        logger.info(f"Valor: {valor}")
                        break
                
                if id_apuracao is None:
                    logger.warning(f"Nenhum idApuracao encontrado para {MES:02d}/{ANO}")
                    logger.info("Apurações disponíveis:")
                    for apuracao in dados_apuracoes:
                        logger.info(f"  - {apuracao.get('dataInicial')}: idApuracao={apuracao.get('idApuracao')}, situação={apuracao.get('situacao')}")
                else:
                    params_creditos['idApuracao'] = id_apuracao
                    logger.success(f"idApuracao {id_apuracao} salvo para uso nas requisições")
                    
        except Exception as e:
            logger.error(f"Erro ao buscar idApuracao: {e}")
            id_apuracao = None
        
        if id_apuracao is None:
            logger.warning("Não foi possível obter o idApuracao. Continuando sem ele...")
        
        sleep(5)

        endpoint_url_creditos = "https://consumo.tributos.gov.br/servico/cbs-apuracao/api/creditos/nao_apropriados/contribuintes"

        params_primeira = params_creditos.copy()
        params_primeira['pagina'] = 0
        params_primeira['idApuracao'] = id_apuracao
        
        response = requests.get(
            url=endpoint_url_creditos, 
            cookies=cookies_dict, 
            params=params_primeira
        )
        
        if response.status_code != 200:
            logger.error(f"Erro na requisição: {response.text}")
        else:
            try:
                resultado_json_creditos = response.json()
            except json.JSONDecodeError:
                logger.error(f"Erro ao parsear JSON: {response.text}")
                resultado_json_creditos = None
            
            if resultado_json_creditos:
                    meta = resultado_json_creditos.get('meta', {})
                    total = meta.get('total', 0)
                    existe_proxima_pagina = meta.get('existeProximaPagina', False)
                    
                    total_paginas = math.ceil(total / 1000)
                    
                    todos_dados = []
                    
                    dados_primeira_pagina = resultado_json_creditos.get('dados', [])
                    todos_dados.extend(dados_primeira_pagina)
                    logger.info(f"Página 0 processada: {len(dados_primeira_pagina)} registros (em memória)")
                    
                    for pagina in range(1, total_paginas):
                        params = params_creditos.copy()
                        params['pagina'] = pagina
                        
                        logger.info(f"Fazendo requisição para página {pagina}...")
                        response = requests.get(
                            url=endpoint_url_creditos, 
                            cookies=cookies_dict, 
                            params=params
                        )
                        
                        if response.status_code != 200:
                            logger.error(f"Erro na requisição da página {pagina}: {response.text}")
                            continue
                        
                        try:
                            resultado_pagina = response.json()
                            dados_pagina = resultado_pagina.get('dados', [])
                            todos_dados.extend(dados_pagina)
                            logger.info(f"Página {pagina} processada: {len(dados_pagina)} registros (em memória)")
                        except json.JSONDecodeError:
                            logger.error(f"Erro ao parsear JSON da página {pagina}: {response.text}")
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
                    
                    logger.success("Processamento concluído!")
                    logger.info(f"Total de registros coletados: {len(todos_dados)}")
                    logger.info(f"Total de páginas processadas: {total_paginas}")

except Exception as e:
    logger.error(f"Erro: {e}")
    logger.error(f"Traceback: {traceback.format_exc()}")
finally:
    driver.quit()
