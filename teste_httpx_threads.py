import undetected_chromedriver as uc
import time
import json
import httpx
import math
import queue
import threading
import uuid
import os
import random
from pprint import pprint

from threading import Event, Thread
from queue import Queue
from datetime import datetime
import pytz

timeout = httpx.Timeout(
    connect=10.0,
    read=90.0,
    write=10.0,
    pool=5.0
)


pasta_resultados = 'resultados'
event = Event()
#fila = Queue()

def tamanho_fila():
    arquivo_json = 'debitos_processados.json'
    with open(arquivo_json, 'r', encoding='utf-8') as f:
        dados_json = json.load(f)
    
    # Extrair apenas os valores de idDocumentoFiscal de cada registro
    todos_dados = dados_json.get('dados', [])
    id_documentos_fiscais = []
    for registro in todos_dados:
        id_documento_fiscal = registro.get('idDocumentoFiscal')
        if id_documento_fiscal:
            id_documentos_fiscais.append(id_documento_fiscal)
    
    # Contar total de registros
    total_registros = len(id_documentos_fiscais)
    print(f"Total de registros encontrados: {total_registros}")
    return total_registros

len_fila = tamanho_fila()
fila = Queue(maxsize=len_fila+1)


class Worker(Thread):
    def __init__(self, target, queue, *, name="Worker"):
        super().__init__()
        self.name = name
        self.queue = queue
        self._target = target
        self._stoped = False
        print(self.name, "Started")
    
    def run(self):
        event.wait()
        while not self.queue.empty():
            chave = self.queue.get()
            print(self.name, chave)
            if chave == "Kill":
                self.queue.put(chave)
                self._stoped = True
                break
            self._target(chave)
    
    def join(self):
        while not self._stoped:
            time.sleep(0.1)


def processar_documentos(idDocumentoFiscal, cookies_session):
    url_documento = f"https://consumo.tributos.gov.br/servico/cbs-apuracao/api/rocs/debito/documentos_fiscais/{idDocumentoFiscal}"
    
    # Intervalo aleatório de 1 a 10 segundos antes da requisição
    intervalo_aleatorio = random.uniform(1, 10)
    # print(f'Aguardando {intervalo_aleatorio:.2f} segundos antes da requisição | {_data_hora_brasileira()}.')
    time.sleep(intervalo_aleatorio)
    
    print(f'Fazendo requisições | {_data_hora_brasileira()}.')
    response = httpx.get(
        url_documento,
        cookies=cookies_session,
        timeout=timeout
    )
    print(f'Requisição concluída | {_data_hora_brasileira()}.')

    return idDocumentoFiscal, response

def salvar_resultado(args):
    pasta_resultados = 'resultados'
    idDocumentoFiscal, resposta = args
    if resposta.status_code == 200:
        dados_documento = resposta.json()
        
        id_unico = str(uuid.uuid4())
        nome_arquivo = f"{id_unico}.json"
        caminho_arquivo = os.path.join(pasta_resultados, nome_arquivo)
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump({
                'idDocumentoFiscal': idDocumentoFiscal,
                'dados': dados_documento
            }, f, indent=4, ensure_ascii=False)
    else:
        print(f"Erro ao salvar resultado para {idDocumentoFiscal}: {resposta.text}")

def pipeline(*funcs):
    def inner(argument):
        state = argument
        for func in funcs:
            state = func(state)
    return inner



def get_pool(n_th: int):
    """Retorna um número n de Threads."""
    return [Worker(target=target, queue=fila, name=f'Worker{n}')
            for n in range(n_th)]

def _data_hora_brasileira():
    return datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M:%S')

# Criar instância do navegador com versão específica do Chrome (145)
driver = uc.Chrome(version_main=145)

try:
    # Carregar cookies do arquivo JSON
    with open('cookies.json', 'r', encoding='utf-8') as f:
        cookies = json.load(f)
    
    print(f"Cookies carregados do arquivo cookies.json ({len(cookies)} cookies encontrados)")
    
    # Abrir a URL primeiro (necessário para poder adicionar cookies)
    url = "https://consumo.tributos.gov.br/"
    driver.get(url)
    
    # Maximizar a janela do navegador (tela cheia)
    driver.maximize_window()
    
    # Adicionar os cookies carregados à sessão do navegador
    for cookie in cookies:
        # Remover campos que não são suportados pelo Selenium
        cookie_to_add = {
            'name': cookie['name'],
            'value': cookie['value'],
            'domain': cookie['domain'],
            'path': cookie['path'],
            'secure': cookie.get('secure', False),
            'httpOnly': cookie.get('httpOnly', False)
        }
        # Adicionar sameSite apenas se existir e for válido
        if 'sameSite' in cookie:
            cookie_to_add['sameSite'] = cookie['sameSite']
        
        try:
            driver.add_cookie(cookie_to_add)
        except Exception as e:
            print(f"Erro ao adicionar cookie {cookie['name']}: {e}")
    
    print("Cookies adicionados à sessão do navegador")
    
    # Recarregar a página para aplicar os cookies
    driver.get(url)
    
    # Aguardar 10 segundos
    print("Aguardando 10 segundos...")
    time.sleep(10)
    
    # Obter os cookies da sessão do navegador
    cookies_sessao = driver.get_cookies()
    
    # Converter cookies do formato Selenium para formato requests
    cookies_dict = {}
    for cookie in cookies_sessao:
        cookies_dict[cookie['name']] = cookie['value']
    
    if not os.path.exists('debitos_processados.json'):
    
        # Fazer requisição GET para o endpoint usando os cookies da sessão
        endpoint_url = "https://consumo.tributos.gov.br/servico/cbs-apuracao/api/debitos/roc"
        
        # Parâmetros base
        params_base = {
            'mes': 2,
            'ano': 2026,
            'porPagina': 1000,
            'isAntesConclusao': 'true',
            'isAposConclusao': 'false'
        }
        
        # Fazer primeira requisição para obter o total
        print(f"\nFazendo primeira requisição GET para: {endpoint_url}")
        params_primeira = params_base.copy()
        params_primeira['pagina'] = 0
        
        response = httpx.get(endpoint_url, cookies=cookies_dict, params=params_primeira, follow_redirects=True)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Erro na requisição: {response.text}")
        else:
            # Parsear resposta JSON
            try:
                resultado_json = response.json()
            except json.JSONDecodeError:
                print(f"Erro ao parsear JSON: {response.text}")
                resultado_json = None
            
            if resultado_json:
                # Obter informações de paginação
                meta = resultado_json.get('meta', {})
                total = meta.get('total', 0)
                existe_proxima_pagina = meta.get('existeProximaPagina', False)
                
                print(f"\nTotal de registros: {total}")
                print(f"Existe próxima página: {existe_proxima_pagina}")
                
                # Calcular número total de páginas (arredondando para cima)
                total_paginas = math.ceil(total / 1000)
                print(f"Total de páginas a processar: {total_paginas}")
                
                # Lista para acumular todos os dados em memória
                todos_dados = []
                
                # Adicionar dados da primeira página em memória
                dados_primeira_pagina = resultado_json.get('dados', [])
                todos_dados.extend(dados_primeira_pagina)
                print(f"Página 0 processada: {len(dados_primeira_pagina)} registros (em memória)")
                
                # Fazer requisições para as páginas restantes e acumular em memória
                for pagina in range(1, total_paginas):
                    params = params_base.copy()
                    params['pagina'] = pagina
                    
                    print(f"\nFazendo requisição para página {pagina}...")
                    response = httpx.get(endpoint_url, cookies=cookies_dict, params=params, follow_redirects=True)
                    
                    if response.status_code != 200:
                        print(f"Erro na requisição da página {pagina}: {response.text}")
                        continue
                    
                    try:
                        resultado_pagina = response.json()
                        dados_pagina = resultado_pagina.get('dados', [])
                        # Adicionar dados da página atual à lista em memória
                        todos_dados.extend(dados_pagina)
                        print(f"Página {pagina} processada: {len(dados_pagina)} registros (em memória)")
                    except json.JSONDecodeError:
                        print(f"Erro ao parsear JSON da página {pagina}: {response.text}")
                        continue
                
                # Unir todos os dados em um único registro consolidado em memória
                resultado_final = {
                    'dados': todos_dados,
                    'meta': {
                        'total_registros': len(todos_dados),
                        'total_paginas_processadas': total_paginas,
                        'total_original': total
                    }
                }
                
                # Salvar os resultados consolidados em um arquivo JSON
                arquivo_saida = 'debitos_processados.json'
                with open(arquivo_saida, 'w', encoding='utf-8') as f:
                    json.dump(resultado_final, f, indent=4, ensure_ascii=False)
                
                print(f"\n{'='*60}")
                print(f"Processamento concluído!")
                print(f"Total de registros coletados: {len(todos_dados)}")
                print(f"Total de páginas processadas: {total_paginas}")
                print(f"Dados consolidados salvos em: {arquivo_saida}")
                print(f"{'='*60}")
            
    # Coletar os valores de idDocumentoFiscal e contar total de registros
    print(f"\n{'='*60}")
    print(f"Coletando idDocumentoFiscal dos registros...")
    print(f"{'='*60}")
    
    # Carregar dados do arquivo JSON
    arquivo_json = 'debitos_processados.json'
    with open(arquivo_json, 'r', encoding='utf-8') as f:
        dados_json = json.load(f)
    
    # Extrair apenas os valores de idDocumentoFiscal de cada registro
    todos_dados = dados_json.get('dados', [])
    id_documentos_fiscais = []
    for registro in todos_dados:
        id_documento_fiscal = registro.get('idDocumentoFiscal')
        if id_documento_fiscal:
            id_documentos_fiscais.append(id_documento_fiscal)
    
    # Contar total de registros
    total_registros = len(id_documentos_fiscais)
    print(f"Total de registros encontrados: {total_registros}")
    
    # Configurar a fila global com o tamanho do total de registros
    # fila = Queue(maxsize=total_registros+1)
    
    # Iterar pelos idDocumentoFiscal e adicionar na fila global
    for id_documento_fiscal in id_documentos_fiscais:
        fila.put(id_documento_fiscal)
    #     endpoint_base = "https://consumo.tributos.gov.br/servico/cbs-apuracao/api/rocs/debito/documentos_fiscais/"
    #     url_documento = f"{endpoint_base}{id_documento_fiscal}"
 
    #     print(f'Fazendo requisições | {_data_hora_brasileira()}.')
    #     with httpx.Client(timeout=None) as client:
    #         response = client.get(url_documento, cookies=cookies_dict, follow_redirects=True)
    #         print(f'Requisição concluída | {_data_hora_brasileira()}.')
    #         if response.status_code == 200:
    #             try:
    #                 dados_documento = response.json()
                    

    #                 id_unico = str(uuid.uuid4())
    #                 nome_arquivo = f"{id_unico}.json"
    #                 caminho_arquivo = os.path.join(pasta_resultados, nome_arquivo)
                    

    #                 with open(caminho_arquivo, 'w', encoding='utf-8') as f:
    #                     json.dump({
    #                         'idDocumentoFiscal': id_documento_fiscal,
    #                         'dados': dados_documento
    #                     }, f, indent=4, ensure_ascii=False)
    #                 print(f'Arquivo salvo | {_data_hora_brasileira()}.')
    #             except json.JSONDecodeError:
    #                 print(f"  ✗ Erro ao parsear JSON para {id_documento_fiscal}")
    #         else:
    #             print(f"  ✗ Erro na requisição para {id_documento_fiscal}: Status {response.status_code}")
        
    event.set()
    fila.put("Kill")
    # exit()
    total_registros_adicionados = fila.qsize()
    print(f"\n{'='*60}")
    print(f"Coleta concluída!")
    print(f"Total de registros adicionados à fila: {total_registros_adicionados}")
    print(f"Total de registros processados: {total_registros}")
    print(f"{'='*60}")
    
    # Criar pasta resultados se não existir
    pasta_resultados = 'resultados'
    if not os.path.exists(pasta_resultados):
        os.makedirs(pasta_resultados)
        print(f"Pasta '{pasta_resultados}' criada.")
    
    # Criar função wrapper que usa os cookies do escopo
    def wrapper_processar(id_documento_fiscal):
        return processar_documentos(id_documento_fiscal, cookies_dict)
    
    target = pipeline(wrapper_processar, salvar_resultado)
    
    print('iniciando processamento...')
    # th = Worker(target=target, queue=fila, name='Worker1')
    # th.start()
    # th.join()
    
    # print(fila.queue)
    thrs = get_pool(20)
    print('starts')
    [th.start() for th in thrs]
    print('joins')
    [th.join() for th in thrs]
            
    # Função worker que processa requisições da fila
    # def worker_processar_documentos(cookies_session, fila, contador_processados, lock):
    #     endpoint_base = "https://consumo.tributos.gov.br/servico/cbs-apuracao/api/rocs/debito/documentos_fiscais/"
        
    #     while True:
    #         try:
    #             # Obter idDocumentoFiscal da fila (timeout de 1 segundo)
    #             id_documento_fiscal = fila.get(timeout=1)
                
    #             # Construir URL completa
    #             url_documento = f"{endpoint_base}{id_documento_fiscal}"
    #             #print(f"url_documento: {url_documento}")
    #             #print(f"cookies_session: {cookies_session}")
                
    #             try:
    #                 # Fazer requisição GET usando os cookies da sessão
    #                 response = httpx.get(url_documento, cookies=cookies_session, timeout=30, follow_redirects=True)
                    
    #                 if response.status_code == 200:
    #                     try:
    #                         dados_documento = response.json()
                            
    #                         # Gerar identificação única para o arquivo
    #                         id_unico = str(uuid.uuid4())
    #                         nome_arquivo = f"{id_unico}.json"
    #                         caminho_arquivo = os.path.join(pasta_resultados, nome_arquivo)
                            
    #                         # Salvar resultado em arquivo JSON
    #                         with open(caminho_arquivo, 'w', encoding='utf-8') as f:
    #                             json.dump({
    #                                 'idDocumentoFiscal': id_documento_fiscal,
    #                                 'dados': dados_documento
    #                             }, f, indent=4, ensure_ascii=False)
                            
    #                         # Atualizar contador de forma thread-safe
    #                         with lock:
    #                             contador_processados[0] += 1
    #                             processados = contador_processados[0]
    #                             if processados % 50 == 0 or processados == total_ids:
    #                                 print(f"  Processados: {processados}/{total_ids} documentos fiscais")
                            
    #                     except json.JSONDecodeError:
    #                         print(f"  ✗ Erro ao parsear JSON para {id_documento_fiscal}")
    #                 else:
    #                     print(f"  ✗ Erro na requisição para {id_documento_fiscal}: Status {response.status_code}")
                        
    #             except (httpx.RequestError, httpx.HTTPError) as e:
    #                 print(f"  ✗ Erro na requisição para {id_documento_fiscal}: {e}")
                
    #             # Marcar tarefa como concluída
    #             fila.task_done()
                
    #         except queue.Empty:
    #             # Fila vazia, encerrar thread
    #             break
    #         except Exception as e:
    #             print(f"  ✗ Erro inesperado: {e}")
    #             fila.task_done()
    
    # # Criar contador compartilhado e lock para thread-safety
    # contador_processados = [0]
    # lock_contador = threading.Lock()
    
    # # Criar e iniciar 50 threads workers
    # num_threads = 12
    # threads = []
    
    # print(f"\n{'='*60}")
    # print(f"Iniciando processamento com {num_threads} threads...")
    # print(f"{'='*60}")
    
    # for i in range(num_threads):
    #     thread = threading.Thread(
    #         target=worker_processar_documentos,
    #         args=(cookies_dict, fila_id_documentos_fiscais, contador_processados, lock_contador)
    #     )
    #     thread.daemon = True
    #     thread.start()
    #     threads.append(thread)
    
    # # Aguardar todas as tarefas da fila serem processadas
    # fila_id_documentos_fiscais.join()
    
    # # Aguardar todas as threads terminarem
    # for thread in threads:
    #     thread.join()
    
    # print(f"\n{'='*60}")
    # print(f"Processamento concluído!")
    # print(f"Total de documentos processados: {contador_processados[0]}")
    # print(f"Arquivos salvos na pasta: {pasta_resultados}")
    # print(f"{'='*60}")
    
finally:
    # Fechar o navegador
    driver.quit()
