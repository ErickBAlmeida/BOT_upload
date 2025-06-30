from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import upload
import shutil
import time
import os

class Validador:
    def __init__(self):

        # Configurando ambiente
        load_dotenv()

        link = os.getenv("LINK")
        self.email = os.getenv("EMAIL")
        self.password = os.getenv("PASSWORD")

        # Configurando Navegador
        self.navegador = webdriver.Chrome()
        self.navegador.get(link)
        self.navegador.maximize_window()

        # Configurações de documentos
        self.camminho = os.path.join(os.path.expanduser("~"), "Desktop", "anexos") 
        self.desktop_path = os.path.join(os.path.expanduser("~"), "Desktop") 
        
        self.logar()

    def logar(self):
        self.navegador.find_element("id", "id_username").send_keys(self.email)
        self.navegador.find_element("id", "id_password").send_keys(self.password) # Local para senha
        self.navegador.find_element("class name", "submit-btn").click()
    
    def run(self):
        self.pesquisar()
        self.scroll_page()
    
    def ponteiro(self):
        
        for processo in os.listdir(self.camminho):
            print(f"\nprocesso: {processo}")
            self.caminho_anexos = os.path.join(self.camminho, processo)
            yield processo
    
    def pesquisar(self):

        self.gcpj = next(self.ponteiro())
        print(f'Pesquisando processo: {self.gcpj}')

        self.lupa = self.navegador.find_element("class name", "mdi-magnify").click()
        time.sleep(1)

        self.search_bar = self.navegador.find_element("id", "main-search")
        self.search_bar.clear()
        self.search_bar.click()
        self.search_bar.send_keys(str(self.gcpj) + Keys.ENTER)

        link_processo =("partial link text", str(self.gcpj)) #link do processo
        
        try:
            WebDriverWait(self.navegador, 10).until(
                EC.presence_of_element_located(link_processo)
            )
            WebDriverWait(self.navegador,2).until(
                EC.element_to_be_clickable(link_processo)
            )
            self.navegador.find_element("partial link text", str(self.gcpj)).click()
            
        except:
            print(f"Erro de conexão, não foi possível concluir a pesquisa. GCPJ: {self.gcpj}")

    def scroll_page(self):

        time.sleep(3)
        print("\nBuscando a pasta arquivos...\n")
        
        elemento = WebDriverWait(self.navegador, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[@href='#arquivos']"))
        )
        
        self.navegador.execute_script("arguments[0].scrollIntoView({block: 'center'})", elemento)
        self.navegador.find_element("link text", "Arquivos").click()

        time.sleep(.5)
        self.navegador.execute_script("arguments[0].scrollIntoView({block: 'start'})", elemento)

        campo_de_pastas = self.navegador.find_element(By.ID, "directory-tree")

        pastas = campo_de_pastas.find_elements(By.XPATH, "./li/div/a/span") # seleciona todas as pastas dentro do campo de pastas
        total_de_arquivos = campo_de_pastas.find_elements(By.XPATH, "./li/div/a/small")
        lixeiras = self.navegador.find_elements(By.XPATH, "//ul[@id='directory-tree']/li/div/i[contains(@class, 'mdi-trash-can-outline')]")

        print(f"{len(pastas)} pastas encontradas...")
        print(f"{len(lixeiras)} lixeiras encontradas...")

        time.sleep(3)    

        if len(pastas) == 0:
            print("\nO processo está vazio.\nSubindo os anexos!\n")
            upload.main(self.gcpj)
            return

        pastas_normalizadas = [s.text.strip().lower() for s in pastas]
        
        # checa se o texto possui pasta de anexos
        if not 'documentos diversos' in pastas_normalizadas and not 'documentos gcpj' in pastas_normalizadas and not 'documentação gcpj':
            print("\nO processo não possui pasta de anexos...")
            try:
                print("Preparando para o upload de arquivos.")
                upload.main(self.gcpj)
            except Exception as e:
                print(f"\nErro durante upload: {e}\n")
                raise
            
        wait = WebDriverWait(self.navegador, 10)

        for i, pasta in enumerate(pastas):       
            # scroll até a lixeiras correspondente à pasta
            self.navegador.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'})", lixeiras[i])

            texto_pasta = pasta.text.strip().lower()

            time.sleep(2)
            
            # checa se o texto possui pasta de anexos
            if texto_pasta in ['documentos diversos', 'documentos gcpj', 'documentação gcpj']:
                num_de_anexados = int(total_de_arquivos[i].text)
                print(f"\nPasta '{pasta.text.strip()}' possui {num_de_anexados} anexados e {len(os.listdir(self.caminho_anexos))} para anexar\n")
                time.sleep(2)

                # checa se precisar atualizar baseado no total de arquivos no processo
                if num_de_anexados < len(os.listdir(self.caminho_anexos)):
                    time.sleep(1)

                    # Click na lixeira
                    lixeiras[i].click()
                    time.sleep(1)
                    
                    # Aguarda o botão de confirmação estar clicável e clica
                    try:
                        confirmar_btn = wait.until(
                            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Confirmar')]"))
                        )
                        confirmar_btn.click()
                        print("Pasta excluída com sucesso.")
                        time.sleep(3)
                        
                    except Exception as e:
                        print(f"Erro ao clicar em Confirmar: {e}\n")
                        raise

                    print("\nAnexando novamente os arquivos deste processo...")
                    time.sleep(1)

                    try:
                        print("Preparando para o upload de arquivos.")
                        upload.main(self.gcpj)
                        break
                    except Exception as e:
                        print(f"\nErro durante upload: {e}\n")
                
                else:
                    print("Processo já está atualizado...")
                    break

        # Move o diretório processado para o diretório "Anexos feitos"
        diretorio_feito = os.path.join(self.desktop_path, 'FEITOS')
        os.makedirs(diretorio_feito, exist_ok=True)
        shutil.move(self.caminho_anexos, diretorio_feito)
        print(f"movendo {self.caminho_anexos} para {diretorio_feito}")
               
        time.sleep(5)

app = Validador()
for i in os.listdir(app.camminho):
    app.run()

print("\nAUTOMAÇÃO FINALIZADA!!\n")
time.sleep(20)