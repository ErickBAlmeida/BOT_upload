import os
import re
import shutil
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from win10toast import ToastNotifier

load_dotenv()

TOKEN = os.getenv("TOKEN")
URL = os.getenv("URL")

# Configurar cabeçalhos
headers = {
    "Authorization": f"Token {TOKEN}",
    "Accept": "application/json"
}

notificacao = ToastNotifier()

def renomear_arquivos(diretorio: str, gcpj):
    pasta = Path(diretorio)

    if not pasta.is_dir():
        print(f"\nO caminho '{diretorio}' não é um diretório válido.")
        return
    
    for arquivo in pasta.iterdir():
        if arquivo.is_file():
            nome_original = arquivo.name
            
            # Remove todos os dígitos e substitui espaços por _
            name_holder = re.sub(r'\d+', '', nome_original).replace(' ', '_')
            novo_nome = f"{gcpj}{name_holder}"

            # Tenta renomear até que seja bem-sucedido
            while True:

                novo_caminho = arquivo.parent / novo_nome
                try:
                    arquivo.rename(novo_caminho)
                    print(f"Renomeado: {nome_original} → {novo_nome}")
                    break  # Sai do loop se a renomeação for bem-sucedida
                
                except FileExistsError:
                    # Se o arquivo já existir, adiciona um _ ao final do novo nome
                    novo_nome += '_'
                    
                except Exception as e:
                    print(f"Erro ao renomear '{nome_original}': {e}")
                    break  # Sai do loop em caso de erro diferente

def upload(pasta_anexos):
    print("\nIniciando processo de upload...")

    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop") 

    # Lista apenas os arquivos no diretório especificado
    arquivos = os.listdir(pasta_anexos)

    if not arquivos:
        print("O diretório está vazio.")
        return

    for arquivo in arquivos:
        caminho_arquivo = os.path.join(pasta_anexos, arquivo)

        # Verifica se é um arquivo
        if os.path.isfile(caminho_arquivo):
            try:
                with open(caminho_arquivo, "rb") as f:
                    files = {
                        "document": (arquivo, f, "application/pdf")
                    }
                    response = requests.post(URL, files=files, headers=headers)

                print(f"\nEnviando {arquivo}... Status: {response.status_code}")

                # Caso o GCPJ não esteja no sistema, move para a pasta NÃO_ENCONTRADOS
                if response.status_code == 400:
                    
                    diretorios_nn_encotrados = os.path.join(desktop_path, 'NÃO_ENCONTRADOS')
                    os.makedirs(diretorios_nn_encotrados, exist_ok=True)
                    shutil.move(pasta_anexos, diretorios_nn_encotrados)
                    print(f"{pasta_anexos} movido para NÃO_ENCONTRADOS.")
                    continue

                # Caso ocorra um erro desconhecido, move para a pasta PARA_ANALISE
                if response.status_code != 200 and response.status_code != 404:

                    print(f"Erro na resposta: {response.text}")
                    print(f"Cabeçalhos da resposta: {dict(response.headers)}")
                    para_analise = os.path.join(desktop_path, 'PARA_ANALISE')
                    os.makedirs(para_analise, exist_ok=True)
                    shutil.move(pasta_anexos, para_analise)
                    print(f"{pasta_anexos} movido para PARA_ANALISE.")
                    continue

                print(f"Upload realizado com sucesso para {arquivo}\n")

            except Exception as e:
                print(f"\nErro ao processar arquivo {arquivo}: {str(e)}\n")
                notificacao.show_toast("ERRO:", f"Erro ao processar arquivo {arquivo}: {str(e)}", duration=2)    

def main(gcpj):
    
    diretorio = os.path.join(os.path.expanduser("~"), "Desktop", "anexos", gcpj)
    total_de_arquivos = len(os.listdir(diretorio))
    
    if os.path.isdir(diretorio):
        for arquivo in os.listdir(diretorio):            
            if re.search(r'[ \d]', arquivo):
                print(f"\nRenomeando arquivos do diretório: {diretorio}\n")
                try:
                    renomear_arquivos(diretorio, gcpj)
                except Exception as e:
                    print("\nERRO ao renomear documento", e)
                    raise
                break

            else:
                continue
        
        upload(diretorio)
        
    else:
        print(f"'{diretorio} não é um diretório válido.'")
    
    time.sleep(2)
    print(f"\n{total_de_arquivos} DOCUMENTO(S) ANEXADO(S)!!\n")
    return