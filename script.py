import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

class Validador:
    def __init__(self):
        # Configurando Navegador
        self.navegador = webdriver.Chrome()
        self.navegador.get("https://octopus.retake.com.br/entrar/?next=/dashboard/")
        self.navegador.maximize_window()

        # Manipulação de Excel
        self.df = pd.read_excel('banco_de_gcpj.xlsx', sheet_name='01')
        self.total_de_itens = self.df.shape[0]
        self.linha = 0
        
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
                gcpj = self.df.at[self.linha, 'BRADESCO']
                self.linha += 1
                return gcpj
            
        except Exception as e:
            print(f"Erro so processar Banco de dados Excel.\n{e}")
    
    def pesquisar(self):
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
        arquivos = self.navegador.find_element("link text", "Arquivos")
        self.navegador.execute_script("arguments[0].scrollIntoView({block: 'start'})", arquivos)

    # def achar_arquivos(self):
    #     try:
    #         for item in self.arquivos:
    #             if "Arquivos" in item.text:
    #                 item.click()
    #                 break

    #         documentos_diversos = self.navegador.find_element_by_xpath((f'//span[contains(text(), "{self.texto1}")]'))
    #         documentos_gcpj = self.navegador.find_element_by_xpath((f'//span[contains(text(), "{self.texto2}")]'))
            
    #     except:
            # ...
    
    # def rodar_planilha(self):
    #     #resgatar CGPJ da planilha excel
    #     ...
    
    # def faltantes(self):
    #     #armazenar GCPJ detectdos como faltantes em um arquivo TXT
    #     ...        
    
if __name__ == "__main__":
    try:
        automacao = Validador()
    except Exception as e:
        print(e)
    