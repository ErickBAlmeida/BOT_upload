# BOT Upload Automático de Documentos

Este projeto automatiza o processo de verificação e upload de anexos não cadastrados no sistema, utilizando Selenium para automação de navegador e integração com API para envio de documentos.

## Funcionalidades

- Acessa o sistema web automaticamente e realiza login.
- Pesquisa processos e verifica a existência de pastas de anexos.
- Renomeia arquivos conforme regras pré-definidas.
- Realiza upload de documentos via API.
- Move pastas para diretórios específicos conforme o status do upload (FEITOS, NÃO_ENCONTRADOS, PARA_ANALISE).
- Notifica o usuário em caso de erros.

## Estrutura do Projeto

- [`script.py`](script.py): Script principal de automação com Selenium.
- [`upload.py`](upload.py): Responsável pelo tratamento e upload dos arquivos.
- `.env`: Armazena variáveis de ambiente sensíveis.
- `README.MD`: Este arquivo.
- `.gitignore`: Ignora arquivos sensíveis e cache do Python.

## Como usar

1. Instale as dependências:
    ```sh
    pip install selenium python-dotenv requests win10toast
    ```
2. Configure o arquivo `.env` com as variáveis necessárias.
3. Coloque os arquivos PDF a serem anexados na pasta `\Desktop\anexos\NOMEPROCESSO`.
4. Execute o script principal:
    ```sh
    python [script.py](http://_vscodecontentref_/0)
    ```

## Observações

- O projeto foi desenvolvido para ambiente Windows.
- É necessário ter o ChromeDriver compatível com sua versão do Google Chrome instalado.
- O sistema move automaticamente as pastas processadas para o desktop, conforme o resultado do upload.