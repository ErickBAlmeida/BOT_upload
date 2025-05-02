import time
import pandas as pd
from openpyxl import load_workbook, Workbook
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

class Validador:
    def __init__(self):
        # Configurando Navegador
        self.navegador = webdriver.Chrome()
        self.navegador.get("https://octopus.retake.com.br/entrar/?next=/dashboard/")
        self.navegador.maximize_window()

        # Manipulação de Excel - ENTRADA - PANDAS
        self.planilha_entrada = pd.read_excel('banco_de_gcpj.xlsx', sheet_name='01')
        self.total_de_itens = self.planilha_entrada.shape[0]
        self.linha = 0

        # Manipulação de Excel - SAIDA - OPENPYXL
        self.planilha_saida = load_workbook("gcpjs_nao_processados.xlsx")
        self.sheet_saida = self.planilha_saida['01']
        
        self.logar()
        self.pesquisar()
        self.scroll_page()
        time.sleep(4)
        # self.achar_arquivos()
    
    def logar(self):
        self.navegador.find_element("id", "id_username").send_keys("erickalmeida@barros.adv.br")
        self.navegador.find_element("id", "id_password").send_keys("@Videocassete21")
        self.navegador.find_element("class name", "submit-btn").click()

    def ponteiro(self):
        try:
            for _ in range(self.total_de_itens):
                gcpj = self.planilha_entrada.at[self.linha, 'BRADESCO']
                self.linha += 1
                return gcpj
            
        except Exception as e:
            print(f"Erro so processar Banco de dados Excel.\n{e}")
    
    def pesquisar(self):
        global gcpj
        gcpj = self.ponteiro()
        print(f'Processo: {gcpj}')

        self.lupa = self.navegador.find_element("class name", "mdi-magnify").click()
        # WebDriverWait(self.navegador,7)
        time.sleep(1)

        self.search_bar = self.navegador.find_element("id", "main-search")
        self.search_bar.click()
        self.search_bar.send_keys(str(gcpj) + Keys.ENTER)

        # time.sleep(7)
        link_processo =("partial link text", str(gcpj)) #link do processo
        try:
            WebDriverWait(self.navegador, 10).until(
                EC.presence_of_element_located(link_processo)
            )
            WebDriverWait(self.navegador,2).until(
                EC.element_to_be_clickable(link_processo)
            )
        except:
            print(f"Erro de conexão, não foi possível concluir a pesquisa. GCPJ: {gcpj}")
            
        self.navegador.find_element("partial link text", str(gcpj)).click()
                            
    def scroll_page(self):
        arquivos = ("link text", "Arquivos")
        elemento = WebDriverWait(self.navegador, 10).until(
            EC.presence_of_element_located(arquivos)
        )
        self.navegador.execute_script("arguments[0].scrollIntoView({block: 'center'})", elemento)
        self.navegador.find_element("link text", "Arquivos").click()

        time.sleep(2)
        self.navegador.execute_script("arguments[0].scrollIntoView({block: 'start'})", elemento)

        campo_de_pastas = self.navegador.find_element("id", "directory-tree")
        pastas = campo_de_pastas.find_elements(By.XPATH, "./*") #seleciona todas as pastas dentro do campo de pastas

        if not pastas:
            self.armazenar_gcpj(gcpj)
        else:
            print("há pastas")
    
    def armazenar_gcpj(self, processo):
        novo_gcpj = [processo]

        self.sheet_saida.append(novo_gcpj)
        self.planilha_saida.save("gcpjs_nao_processados.xlsx")
        
        print("Item armazenado com sucesso!")
    
if __name__ == "__main__":
    try:
        automacao = Validador()
    except Exception as e:
        print(e)
    