'''
    ========== FUNÇÕES DE AUTOMAÇÃO WHATSAPP ==========
'''

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import urllib
import time
import random
import csv
import os

global navegador

def registrar_mensagem(numero, status, erro="sem erros"):
    # Certifica se há um diretório "Output", se não, cria um.
    os.makedirs('Output', exist_ok=True)
    # Define o caminho do arquivo.
    pathOutput = os.path.join('Output', 'log.csv')
    # Titulos do arquivo csv.
    titulos = ['Numero', 'Status', 'Erro']
    
    mensagem = [numero, status, erro]

    with open(pathOutput, mode='a', encoding='utf-8', newline='') as file:
        # Cria um objeto writer para escrever no arquivo CSV.
        writer = csv.writer(file)
        # Verifica se o arquivo já existe. Se não existir, escreve os títulos.
        if not os.path.exists(pathOutput):
            writer.writerow(titulos)
        
        # Escreve a mensagem no arquivo.
        writer.writerow(mensagem)

def abrir_whatsapp():
    global navegador
    navegador = webdriver.Chrome()
    # Acessa o whatsapp
    navegador.get("https://web.whatsapp.com")
    # Verifica de a lista de elementos é menor que 1 (se for menor que 1 é porque nõa há elemento na tela e portanto não carregou.)
    while len(navegador.find_elements(By.ID, 'side')) < 1:
        # Se a lista estiver vazia, espere até aparecer algum elemento.
        time.sleep(1)

def enviar_mensagem(numero, texto, nome):

    # Procura
    nomeSubstituir = "(nome)"
    texto = texto.replace(nomeSubstituir, nome)

    # Formata a string para ser aceito na url.
    texto = urllib.parse.quote(texto)

    link = f"https://web.whatsapp.com/send?phone={numero}&text={texto}"

    # Abre o whatsapp no link e número específicado.
    navegador.get(link)
    # Verifica de a lista de elementos é menor que 1 (se for menor que 1 é porque nõa há elemento na tela e portanto não carregou.)
    while len(navegador.find_elements(By.ID, 'side')) < 1:
        # Se a lista estiver vazia, espere até aparecer algum elemento.
        time.sleep(1)
    time.sleep(6)


    # Verifica se o número é válido.
    try:
        if len(navegador.find_elements(By.XPATH, '//*[@id="app"]/div/span[2]/div/span/div/div/div/div/div/div[1]')) < 1:
            # Procura o botão de enviar de efetua o click.
            navegador.find_element(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[2]/button/span').click()
            mensagem = f"{numero}, enviado, sem erros"
            print(mensagem)
            registrar_mensagem(numero, "enviado", "sem erros")
        else:
            mensagem = f"{numero}, numero inválido, sem erros"
            print(mensagem)
            registrar_mensagem(numero, "não enviado", "sem erros")
    except Exception as e:
        mensagem = f"{numero}, erro no envio, {e}"
        print(mensagem)
        registrar_mensagem(numero, "não enviado", e)

def envio_em_massa(df ,textos, DELAY_MIN, DELAY_MAX, DELAY_MINCONTADOR, DELAY_MAXCONTADOR, CONTADOR):
    
    contador = 0
    
    for index, row in df.iterrows():

        numero = str(row['numero'])
        nome = str(row['nome'])

        enviar_mensagem(numero, random.choice(textos), nome)

        # Valor aleatório entre 2 minutos e 5 minutos.
        time.sleep(random.randint(DELAY_MIN, DELAY_MAX))

        # Verifica quantas mensagens foram enviadas.
        contador += 1

        # Se forem enviadas mais de 50 mensagens, espere mais tempo.
        if contador > CONTADOR:
            time.sleep(random.randint(DELAY_MINCONTADOR, DELAY_MAXCONTADOR))
            contador = 0