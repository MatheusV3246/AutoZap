import warnings
warnings.filterwarnings("ignore")

import os
import time
from time import sleep

import pandas as pd
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

class Engine:
    def __init__(self, profile_dir=None):
        self.tempo_exe = ""
        self.n_contatos = ""
        try:
            self.navegador = webdriver.Chrome()
            self.navegador.minimize_window()
        except Exception as e:
            print(f"Erro ao inicializar o navegador: {e}")
    
    def login(self):
        """Realiza o login no WhatsApp Web."""
        self.navegador.get("https://web.whatsapp.com")
        self.navegador.maximize_window()
        try:
            WebDriverWait(self.navegador, 60).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[2]/div[3]/header/header/div/div/h1'))
            )
            self.navegador.minimize_window()
            return 200
        except TimeoutException:
            return 404

    def processa_base(self, caminho_arquivo):
        """Processa o arquivo de contatos."""
        _, extensao = os.path.splitext(caminho_arquivo)
        try:
            match extensao:
                case ".xlsx":
                    contatos = pd.read_excel(caminho_arquivo)
                case ".csv":
                    contatos = pd.read_csv(caminho_arquivo, sep=";")
                case _:
                    raise ValueError("Formato de arquivo não suportado")
            
            if not {"Número", "Nome"}.issubset(contatos.columns):
                raise ValueError("A fonte de dados deve conter as colunas 'Número' e 'Nome'")
            
            numeros = contatos["Número"].astype(str).tolist()
            nomes = contatos["Nome"].astype(str).tolist()
            #Recebe números de contatos
            self.n_contatos = len(numeros)
            return numeros, nomes
        except Exception as e:
            print(f"Erro ao processar base de contatos: {e}")
            return [], []

    def enviar_final(self, numeros, nomes, mensagem_orig, endosso, saudacao_swicth):
        """Envia mensagens para a lista de contatos."""
        inicio = time.time() 
        link = "link"

        for i, numero in enumerate(numeros):
            saudacao = self._get_saudacao(saudacao_swicth, nomes[i])
            mensagem = self._criar_mensagem(saudacao, mensagem_orig, link, endosso)
            
            situacao = self._tentar_enviar_mensagem(numero, mensagem)
            self.log_envio(situacao, i, nomes[i], numero)

            if (i + 1) % 15 == 0 :
                if (i + 1) >= 150:
                    break
                sleep(6)

        self._calcular_tempo_execucao(inicio, i + 1)
    
    def _get_saudacao(self, saudacao_swicth, nome):
        """Obtém a saudação personalizada."""
        saudacoes = {
            "Bom dia": f"Bom dia, {nome}!",
            "Boa tarde": f"Boa tarde, {nome}!",
            "Boa noite": f"Boa noite, {nome}!",
            "Olá": f"Olá, {nome}!",
            "Oi": f"Oi, {nome}!",
            "Prezado": f"Prezado, {nome}!",
            "Vocativo": f"{nome}!"
        }
        return saudacoes.get(saudacao_swicth, "")

    def _criar_mensagem(self, saudacao, mensagem_orig, link, endosso):
        """Cria a mensagem a ser enviada."""
        return f'''
{saudacao}
{mensagem_orig}

_Caso deseje não receber mais este tipo de comunicação automatizada:_
_Preencha o seguinte formulário_: <{link}>
*AutoZap - Automação de Mensagens*
_Em serviço de:_    
*{endosso}*                 
'''

    def _steps_enviar_mensagem(self, numero, mensagem):
        try:
            search_button = WebDriverWait(self.navegador, 60).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div[2]/div[3]/header/header/div/span/div/span/div[1]/div/span'))
            )
            search_button.click()

            search_field = WebDriverWait(self.navegador, 60).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div[1]/span/div/span/div/div[1]/div[2]/div[2]/div/div[1]/p'))
            )
            search_field.send_keys(numero)
            sleep(1)
            search_field.send_keys(Keys.ENTER)

            pyperclip.copy(mensagem)

            campo_mensagem = WebDriverWait(self.navegador, 60).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p'))
            )
            campo_mensagem.send_keys(Keys.CONTROL + "v")
            sleep(0.25)
            campo_mensagem.send_keys(Keys.ENTER)

            return "Sucesso"
        
        except (NoSuchElementException, TimeoutException, ElementClickInterceptedException) as e:
            return e.__class__.__name__
        
        except Exception as e:
            return str(e)

    def _tentar_enviar_mensagem(self, numero, mensagem):
        """Tenta enviar a mensagem com várias tentativas em caso de falha."""
        max_tentativas = 3
        tentativas = 0
        while tentativas < max_tentativas:
            status_envio = self._steps_enviar_mensagem(numero, mensagem)
            if status_envio == "Sucesso":
                return "Sucesso"
            
            tentativas += 1
            print(f"Tentativa {tentativas} falhou com o erro: {status_envio}. Tentando novamente...")
            sleep(5)  # Tempo de espera antes de tentar novamente
        
        return f"Falha após {max_tentativas} tentativas: {status_envio}"

    def log_envio(self, situacao, iteracao, nome, numero):
        """Registra o log do envio."""
        with open('log/log_envio.txt', 'a') as log_file:
            if situacao == None:
                situacao = "Falha"

            log_message = f"{situacao} ao enviar a {int(iteracao)+1} mensagem para {nome} de numero: {numero}"
            log_file.write(log_message)
            print(log_message)

    def _calcular_tempo_execucao(self, inicio, total_mensagens):
        """Calcula e exibe o tempo total de execução."""
        fim = time.time()
        tempo = fim - inicio
        minutos = int(tempo // 60)
        segundos = int(tempo % 60)
        self.tempo_exe = f"Você enviou {total_mensagens} mensagens em {minutos} minutos e {segundos} segundos"
