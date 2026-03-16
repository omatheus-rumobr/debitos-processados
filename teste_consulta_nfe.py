
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
        if x is None or y is None:
            print(f"Coordenadas inválidas: x={x}, y={y}")
            return
        
        try:
            x_float = float(x)
            y_float = float(y)
        except (ValueError, TypeError):
            print(f"Erro ao converter coordenadas: x={x}, y={y}")
            return
        

        if not np.isfinite(x_float) or not np.isfinite(y_float):
            print(f"Coordenadas não são números finitos: x={x_float}, y={y_float}")
            return
        

        if x_float < 0 or y_float < 0 or x_float > 10000 or y_float > 10000:
            print(f"Coordenadas fora dos limites válidos: x={x_float}, y={y_float}")
            return
        

        x_final = int(x_float) - random.randint(*variationx)
        y_final = int(y_float) - random.randint(*variationy)
        

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
    Extrai dados do CTE do HTML usando BeautifulSoup.
    
    Returns:
        dict: Dicionário com os dados extraídos ou None em caso de erro
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        

        chave_acesso = None

        chave_th = soup.find('th', string=re.compile(r'Chave de Acesso', re.I))
        if chave_th:

            chave_row = chave_th.find_parent('tr').find_next_sibling('tr')
            if chave_row:
                chave_td_content = chave_row.find('td')
                if chave_td_content:
                    chave_texto = chave_td_content.get_text(strip=True)

                    chave_acesso = re.sub(r'[^\d]', '', chave_texto)
        
        if not chave_acesso:
            print("Erro: Não foi possível extrair a chave de acesso")
            return None
        

        tipo_documento = None
        if len(chave_acesso) >= 23:
            print(f"Chave de acesso>>> {chave_acesso}")
            codigo_tipo = chave_acesso[20:22]
            print(f"Codigo de tipo>>> {codigo_tipo}")
            if codigo_tipo == "57":
                tipo_documento = "CT-e"
            elif codigo_tipo == "55":
                tipo_documento = "NF-e"
            else:
                tipo_documento = f"Desconhecido ({codigo_tipo})"
                print(f"Aviso: Código de tipo desconhecido: {codigo_tipo}")
        else:
            print(f"Aviso: Chave de acesso muito curta ({len(chave_acesso)} caracteres), não é possível determinar o tipo")
            tipo_documento = "Desconhecido"
        

        origem = {}
        emitente_titulo = soup.find('div', class_='dfe-titulo', string=re.compile(r'EMITENTE', re.I))
        if emitente_titulo:
            emitente_table = emitente_titulo.find_next_sibling('table')
            if emitente_table:
                rows = emitente_table.find_all('tr')
                if len(rows) >= 2:
                    data_row = rows[1]
                    cells = data_row.find_all('td')
                    if len(cells) >= 4:
                        origem = {
                            'cnpj': cells[0].get_text(strip=True),
                            'nome': cells[1].get_text(strip=True),
                            'inscricaoEstadual': cells[2].get_text(strip=True),
                            'uf': cells[3].get_text(strip=True)
                        }
        

        destino = {}
        destinatario_titulo = soup.find('div', class_='dfe-titulo', string=re.compile(r'DESTINATÁRIO', re.I))
        if destinatario_titulo:
            destinatario_table = destinatario_titulo.find_next_sibling('table')
            if destinatario_table:
                rows = destinatario_table.find_all('tr')
                if len(rows) >= 2:
                    data_row = rows[1]
                    cells = data_row.find_all('td')
                    if len(cells) >= 4:
                        destino = {
                            'cnpj': cells[0].get_text(strip=True),
                            'nome': cells[1].get_text(strip=True),
                            'inscricaoEstadual': cells[2].get_text(strip=True),
                            'uf': cells[3].get_text(strip=True)
                        }
        

        valor_operacao = "0.00"
        valor_th = soup.find('th', string=re.compile(r'Valor Total do Serviço', re.I))
        if valor_th:
            valor_row = valor_th.find_parent('tr').find_next_sibling('tr')
            if valor_row:
                cells = valor_row.find_all('td')
                if len(cells) >= 3:
                    valor_texto = cells[2].get_text(strip=True)
                    valor_texto = valor_texto.replace('.', '').replace(',', '.')
                    try:
                        valor_float = float(valor_texto)
                        valor_operacao = f"{valor_float:.2f}"
                    except:
                        valor_operacao = "0.00"
        
        dados_cte = {
            "chaveDocumento": chave_acesso,
            "numeroDocumento": chave_acesso,
            "tipoDocumento": tipo_documento,
            "origem": origem,
            "destino": destino,
            "valorOperacao": valor_operacao,
            "seguro": "0.00",
            "frete": "0.00"
        }
        
        return dados_cte
        
    except Exception as e:
        print(f"Erro ao extrair dados do CTE: {e}")
        import traceback
        traceback.print_exc()
        return None

def atualizar_debitos_json(chave_documento, dados_cte, caminho_json='debitos_processados.json'):
    """
    Atualiza o arquivo debitos_processados.json com os dados extraídos do CTE.
    
    Args:
        chave_documento: Chave do documento para buscar no JSON
        dados_cte: Dicionário com os dados extraídos do CTE
        caminho_json: Caminho do arquivo JSON
    """
    try:

        with open(caminho_json, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        

        encontrado = False
        for item in dados.get('dados', []):
            if item.get('idDocumentoFiscal') == chave_documento:

                item.update(dados_cte)
                encontrado = True
                print(f"Dados do CTE adicionados ao documento {chave_documento}")
                break
        
        if not encontrado:
            print(f"Aviso: Documento {chave_documento} não encontrado em debitos_processados.json")
            return False
        

        with open(caminho_json, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        
        print(f"Arquivo {caminho_json} atualizado com sucesso")
        return True
        
    except Exception as e:
        print(f"Erro ao atualizar debitos_processados.json: {e}")
        import traceback
        traceback.print_exc()
        return False

options = uc.ChromeOptions()
userdir = "c:\\chromeprofiletest"
options.add_argument(f"--user-data-dir={userdir}")
driver = uc.Chrome(options=options)
driver.maximize_window()



url = 'https://www.nfe.fazenda.gov.br/portal/principal.aspx'



try:
    driver.get(url)

    time.sleep(10)

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
        
        time.sleep(10)
        

        try:
            print("Procurando campo de chave de acesso...")
            campo_chave = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_txtChaveAcessoResumo"))
            )
            campo_chave.click()
            print("Campo clicado com sucesso")
            

            campo_chave.clear()
            

            valor_chave = "41260275958926000193550010000044331707396274"
            campo_chave.send_keys(valor_chave)
            print(f"Valor digitado no campo: {valor_chave}")
            
            time.sleep(10)
            

            try:
                print("Procurando botão Continuar...")
                botao_continuar = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_btnConsultarHCaptcha"))
                )
                botao_continuar.click()
                print("Botão Continuar clicado com sucesso")
            except Exception as e:
                print(f"Erro ao clicar no botão Continuar: {e}")
            

            time.sleep(10)
            

            
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
                
                print("Aguardando 5 segundos antes do clique...")

                time.sleep(2)
                

                print("Pressionando Enter para confirmar certificado...")
                try:

                    pyautogui.press('enter')

                    time.sleep(0.5)
                    print("Enter pressionado para confirmar certificado")
                    time.sleep(2)
                    exit()

                    try:
                        print("Capturando HTML da página para scraping...")
                        html_content = driver.page_source
                        

                        print("Extraindo dados do CTE...")
                        dados_cte = extrair_dados_cte(html_content)
                        
                        if dados_cte:
                            print("Dados extraídos com sucesso:")
                            print(json.dumps(dados_cte, indent=2, ensure_ascii=False))
                            

                            chave_documento = dados_cte.get('chaveDocumento')
                            if chave_documento:
                                print(f"Atualizando debitos_processados.json com chave: {chave_documento}")
                                atualizar_debitos_json(chave_documento, dados_cte)
                            else:
                                print("Erro: Chave do documento não encontrada nos dados extraídos")
                        else:
                            print("Erro: Não foi possível extrair dados do CTE")
                            
                    except Exception as e:
                        print(f"Erro ao fazer scraping da página: {e}")
                        import traceback
                        traceback.print_exc()
                    
                    time.sleep(10)
                except Exception as e:
                    print('ESTA CAINDO AQUI')
                    print(f"Erro ao pressionar Enter com pyautogui: {e}")

                    try:
                        print("Tentando com ActionChains como fallback...")
                        actions = ActionChains(driver)

                        driver.switch_to.default_content()
                        actions.send_keys(Keys.ENTER).perform()
                        time.sleep(0.5)
                        actions.send_keys(Keys.ENTER).perform()
                        print("Enter pressionado usando ActionChains")
                        time.sleep(2)
                    except Exception as e2:
                        print(f"Erro ao pressionar Enter com ActionChains: {e2}")
                
            except Exception as e:
                print(f"Erro ao clicar no botão Consulta Completa: {e}")
            
            
        except Exception as e:
            print(f"Erro ao preencher campo de chave de acesso: {e}")
        
    
finally:
    print("Fechando navegador...")
    driver.quit()
