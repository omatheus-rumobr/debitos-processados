
import undetected_chromedriver as uc
import time
from PIL import Image
from PrettyColorPrinter import add_printer
import pytesseract
import rapidfuzz
import pandas as pd
import numpy as np
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from bs4 import BeautifulSoup
import re

add_printer(1)
import mousekey
import pyautogui

mkey = mousekey.MouseKey()
mkey.enable_failsafekill("ctrl+e")

# Configurar pyautogui para não falhar se o mouse sair da tela
pyautogui.FAILSAFE = False

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def get_screenshot_tesser(minlen=2):
    img_capturar = Image.open("Capturar.PNG")
    df = pytesseract.image_to_data(img_capturar, output_type="data.frame")
    df = df.dropna(subset="text")
    df = df.loc[df.text.str.len() > minlen].reset_index(drop=True)
    return df

def move_mouse(
    x,
    y,
    variationx=(-5, 5),
    variationy=(-5, 5),
    up_down=(0.2, 0.3),
    min_variation=-10,
    max_variation=10,
    use_every=4,
    sleeptime=(0.009, 0.019),
    linear=90,
):
    """
    Move o mouse para uma posição específica com movimento natural.
    
    Args:
        x, y: Coordenadas de destino
        variationx, variationy: Variação aleatória nas coordenadas
        up_down: Tempo de delay para clique
        min_variation, max_variation: Variação mínima e máxima
        use_every: Frequência de uso
        sleeptime: Tempo de espera entre movimentos
        linear: Percentual de linearidade do movimento
    """
    try:
        # Validar coordenadas
        if x is None or y is None:
            print(f"Coordenadas inválidas: x={x}, y={y}")
            return
        
        # Converter para float e validar
        try:
            x_float = float(x)
            y_float = float(y)
        except (ValueError, TypeError):
            print(f"Erro ao converter coordenadas: x={x}, y={y}")
            return
        
        # Verificar se são números válidos (não NaN ou Inf)
        if not np.isfinite(x_float) or not np.isfinite(y_float):
            print(f"Coordenadas não são números finitos: x={x_float}, y={y_float}")
            return
        
        # Validar limites da tela (assumindo resolução mínima de 800x600)
        if x_float < 0 or y_float < 0 or x_float > 10000 or y_float > 10000:
            print(f"Coordenadas fora dos limites válidos: x={x_float}, y={y_float}")
            return
        
        # Calcular coordenadas finais com variação
        x_final = int(x_float) - random.randint(*variationx)
        y_final = int(y_float) - random.randint(*variationy)
        
        # Validar coordenadas finais
        if not np.isfinite(x_final) or not np.isfinite(y_final):
            print(f"Coordenadas finais inválidas: x={x_final}, y={y_final}")
            return
        
        mkey.left_click_xy_natural(
            x_final,
            y_final,
            delay=random.uniform(*up_down),
            min_variation=min_variation,
            max_variation=max_variation,
            use_every=use_every,
            sleeptime=sleeptime,
            print_coords=True,
            percent=linear,
        )
    except Exception as e:
        print(f"Erro ao mover mouse para ({x}, {y}): {e}")
        # Tentar movimento simples como fallback
        try:
            import pyautogui
            pyautogui.moveTo(int(x_float) if 'x_float' in locals() else int(x), 
                           int(y_float) if 'y_float' in locals() else int(y), 
                           duration=0.5)
            pyautogui.click()
        except Exception as e2:
            print(f"Erro no fallback do movimento do mouse: {e2}")

def extrair_dados_cte(html_content):
    """
    Extrai apenas o valor da Base Cálculo ICMS do HTML usando BeautifulSoup.
    
    Returns:
        str: Valor da Base Cálculo ICMS formatado (ex: "8930.73") ou "0.00" em caso de erro
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extrair Base Cálculo ICMS
        valor_operacao = "0.00"
        # Procurar pela tabela que contém "Base Cálculo ICMS"
        base_icms_th = soup.find('th', string=re.compile(r'Base Cálculo ICMS', re.I))
        if base_icms_th:
            valor_row = base_icms_th.find_parent('tr').find_next_sibling('tr')
            if valor_row:
                cells = valor_row.find_all('td')
                if len(cells) >= 2:
                    # A segunda coluna (índice 1) é a Base Cálculo ICMS
                    valor_texto = cells[1].get_text(strip=True)
                    # Converter formato brasileiro (8.930,73) para formato numérico (8930.73)
                    valor_texto = valor_texto.replace('.', '').replace(',', '.')
                    try:
                        valor_float = float(valor_texto)
                        valor_operacao = f"{valor_float:.2f}"
                    except:
                        valor_operacao = "0.00"
        
        return valor_operacao
        
    except Exception as e:
        print(f"Erro ao extrair Base Cálculo ICMS: {e}")
        import traceback
        traceback.print_exc()
        return "0.00"

def ler_chaves_documentos_fiscais(caminho_json='debitos_processados.json'):
    """
    Lê o arquivo JSON e extrai todos os valores do campo idDocumentoFiscal.
    
    Args:
        caminho_json: Caminho do arquivo JSON
        
    Returns:
        list: Lista com todos os valores de idDocumentoFiscal
    """
    try:
        with open(caminho_json, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        chaves = []
        for item in dados.get('dados', []):
            chave = item.get('idDocumentoFiscal')
            if chave:
                chaves.append(chave)
        
        print(f"Total de {len(chaves)} chaves encontradas no arquivo JSON.")
        return chaves
        
    except Exception as e:
        print(f"Erro ao ler arquivo JSON: {e}")
        import traceback
        traceback.print_exc()
        return []

def atualizar_debitos_json_com_base_icms(dados_base_icms, caminho_json='debitos_processados.json'):
    """
    Atualiza o arquivo debitos_processados.json adicionando o campo baseCalculoICMS
    para cada registro que tiver idDocumentoFiscal correspondente às chaves coletadas.
    
    Args:
        dados_base_icms: Dicionário com chave -> valor da base cálculo ICMS
        caminho_json: Caminho do arquivo JSON
    """
    try:
        # Ler o arquivo JSON
        with open(caminho_json, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        # Contador de registros atualizados
        registros_atualizados = 0
        
        # Para cada registro no JSON
        for item in dados.get('dados', []):
            chave_documento = item.get('idDocumentoFiscal')
            
            # Se a chave existe no dicionário de base ICMS coletado
            if chave_documento and chave_documento in dados_base_icms:
                # Adicionar o campo baseCalculoICMS
                item['baseCalculoICMS'] = dados_base_icms[chave_documento]
                registros_atualizados += 1
                print(f"Base Cálculo ICMS adicionada ao documento {chave_documento}: {dados_base_icms[chave_documento]}")
        
        # Salvar o arquivo JSON atualizado
        with open(caminho_json, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        
        print(f"Arquivo {caminho_json} atualizado com sucesso. {registros_atualizados} registro(s) atualizado(s).")
        return True
        
    except Exception as e:
        print(f"Erro ao atualizar debitos_processados.json: {e}")
        import traceback
        traceback.print_exc()
        return False

def consultar_chave_cte(driver, url, valor_chave, dados_base_icms_memoria):
    """
    Faz a consulta completa de uma chave CTE específica.
    
    Args:
        driver: Instância do WebDriver
        url: URL da página de consulta
        valor_chave: Chave do documento fiscal a ser consultada
        dados_base_icms_memoria: Dicionário para armazenar os resultados
        
    Returns:
        bool: True se a consulta foi bem-sucedida, False caso contrário
    """
    try:
        print(f"\n{'='*80}")
        print(f"Iniciando consulta para chave: {valor_chave}")
        print(f"{'='*80}")
        
        # Navegar para a URL
        driver.get(url)
        time.sleep(1)
        
        # Processar captcha
        df = get_screenshot_tesser(minlen=2)
        df = pd.concat([df,pd.DataFrame(rapidfuzz.process_cpp.cdist(["sou", "pameno"], df.text.to_list())).T.rename(columns={0: "sou", 1: "pameno"})],axis=1)

        try:
            vamosclicar = np.diff(df.loc[((df.sou == df.sou.max()) & (df.sou > 90)) | ((df.pameno == df.pameno.max()) & (df.pameno > 90))][:2].index)[0] == 1
        except Exception:
            vamosclicar = False

        if vamosclicar:
            try:
                x, y = df.loc[df.sou == df.sou.max()][["left", "top"]].__array__()[0]
                if np.isfinite(x) and np.isfinite(y):
                    move_mouse(
                        x+550,
                        y+580,
                        variationx=(-10, 10),
                        variationy=(-10, 10),
                        up_down=(0.2, 0.3),
                        min_variation=-10,
                        max_variation=10,
                        use_every=4,
                        sleeptime=(0.009, 0.019),
                        linear=90,
                    )
                else:
                    print(f"Coordenadas inválidas do OCR: x={x}, y={y}")
            except Exception as e:
                print(f"Erro ao processar clique do captcha: {e}")
            
            time.sleep(1)
            
            # Preencher campo de chave de acesso
            try:
                print("Procurando campo de chave de acesso...")
                campo_chave = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_txtChaveAcessoResumo"))
                )
                campo_chave.click()
                print("Campo clicado com sucesso")
                
                campo_chave.clear()
                
                campo_chave.send_keys(valor_chave)
                print(f"Valor digitado no campo: {valor_chave}")
                
                time.sleep(2)
                
                # Clicar no botão Continuar
                try:
                    print("Procurando botão Continuar...")
                    botao_continuar = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_btnConsultarHCaptcha"))
                    )
                    botao_continuar.click()
                    print("Botão Continuar clicado com sucesso")
                except Exception as e:
                    print(f"Erro ao clicar no botão Continuar: {e}")
                    return False
                
                time.sleep(2)
                
                # Clicar no botão Consulta Completa
                try:
                    print("Procurando botão Consulta Completa...")
                    botao_consulta_completa = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_btnConsultaCompleta"))
                    )
                    
                    botao_consulta_completa.click()
                    print("Botão Consulta Completa clicado com sucesso")
                    
                    time.sleep(1)
                    try:
                        alert = driver.switch_to.alert
                        alert.accept()
                        print("Alerta de confirmação aceito")
                    except Exception:
                        print("Nenhum alerta encontrado ou já foi tratado")
                    
                    time.sleep(2)
                    
                    # Confirmar certificado
                    print("Pressionando Enter para confirmar certificado...")
                    try:
                        pyautogui.press('enter')
                        time.sleep(1)

                        # Extrair Base Cálculo ICMS
                        try:
                            print("Capturando HTML da página para scraping...")
                            html_content = driver.page_source
                            
                            print("Extraindo Base Cálculo ICMS...")
                            valor_base_icms = extrair_dados_cte(html_content)
                            
                            if valor_base_icms and valor_base_icms != "0.00":
                                # Armazenar chave e valor no dicionário em memória
                                dados_base_icms_memoria[valor_chave] = valor_base_icms
                                print(f"✓ Base Cálculo ICMS extraída com sucesso para chave {valor_chave}: {valor_base_icms}")
                                return True
                            else:
                                print(f"✗ Erro: Não foi possível extrair Base Cálculo ICMS para chave {valor_chave}")
                                return False
                        except Exception as e:
                            print(f"Erro ao fazer scraping da página: {e}")
                            return False
                    except Exception as e:
                        print(f"Erro ao pressionar Enter com pyautogui: {e}")
                        return False
                except Exception as e:
                    print(f"Erro ao clicar no botão Consulta Completa: {e}")
                    return False
            except Exception as e:
                print(f"Erro ao preencher campo de chave de acesso: {e}")
                return False
        else:
            print("Não foi possível processar o captcha")
            return False
            
    except Exception as e:
        print(f"Erro geral na consulta da chave {valor_chave}: {e}")
        import traceback
        traceback.print_exc()
        return False

url = 'https://www.cte.fazenda.gov.br/portal/consultaRecaptcha.aspx?tipoConsulta=resumo&tipoConteudo=cktLvUUKqh0='

# Ler todas as chaves do arquivo JSON
print("Lendo chaves do arquivo debitos_processados.json...")
chaves_documentos = ler_chaves_documentos_fiscais('debitos_processados.json')

if not chaves_documentos:
    print("Nenhuma chave encontrada no arquivo JSON. Encerrando...")
    exit(1)

# Dicionário em memória para armazenar chave -> valor da base cálculo ICMS
dados_base_icms_memoria = {}

driver = uc.Chrome()

try:
    driver.maximize_window()
    
    # Processar cada chave
    total_chaves = len(chaves_documentos)
    for indice, valor_chave in enumerate(chaves_documentos, 1):
        print(f"\n[{indice}/{total_chaves}] Processando chave {indice} de {total_chaves}...")
        
        # Fazer a consulta
        sucesso = consultar_chave_cte(driver, url, valor_chave, dados_base_icms_memoria)
        
        if sucesso:
            print(f"✓ Consulta concluída com sucesso para chave {indice}/{total_chaves}")
        else:
            print(f"✗ Falha na consulta da chave {indice}/{total_chaves}")
        
        # Fechar a aba atual e abrir uma nova para a próxima consulta
        if indice < total_chaves:  # Não fechar na última iteração
            print("Fechando aba atual e preparando para próxima consulta...")
            try:
                # Abrir uma nova aba primeiro
                driver.switch_to.new_window('tab')
                time.sleep(1)
                
                # Fechar a aba anterior
                handles = driver.window_handles
                if len(handles) > 1:
                    # Mudar para a aba anterior
                    driver.switch_to.window(handles[0])
                    driver.close()
                    # Mudar para a nova aba
                    driver.switch_to.window(handles[1])
                    print("Aba fechada e nova aba ativada com sucesso")
            except Exception as e:
                print(f"Erro ao gerenciar abas: {e}. Continuando com a aba atual...")
            
            time.sleep(1)
        
        # Pequeno delay entre consultas
        time.sleep(2)

finally:
    print("\n" + "="*80)
    print("Fechando navegador...")
    driver.quit()
    
    # Após processar todas as chaves, atualizar o arquivo JSON
    if dados_base_icms_memoria:
        print(f"\nAtualizando debitos_processados.json com {len(dados_base_icms_memoria)} registro(s)...")
        atualizar_debitos_json_com_base_icms(dados_base_icms_memoria)
    else:
        print("\nNenhum dado de Base Cálculo ICMS coletado para atualizar o JSON.")
