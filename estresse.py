# Importação das bibliotecas necessárias
import sys  # Biblioteca para manipulação de sistema e argumentos de linha de comando
import requests  # Biblioteca para fazer requisições HTTP
import threading  # Para rodar múltiplas requisições usando threads
import time  # Importando o módulo time, necessário para medir o tempo de requisições

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QSpinBox, QProgressBar, QMessageBox  # Importação de widgets do PyQt5
from PyQt5.QtCore import Qt  # Para manipular eventos e propriedades do PyQt, como o cursor
from PyQt5.QtGui import QColor, QPalette, QFont  # Para personalizar a interface gráfica, como cores e fontes
from reportlab.lib.pagesizes import letter  # Para definir o tamanho da página do relatório em PDF
from reportlab.pdfgen import canvas  # Para gerar e manipular documentos PDF

# Definindo a classe principal da aplicação
class AplicativoTesteEstresse(QWidget):
    def __init__(self):
        super().__init__()  # Chama o inicializador da classe QWidget (classe base)
        self.init_ui()  # Inicializa a interface gráfica

        # Inicializando variáveis para armazenar os resultados do teste de estresse
        self.resultado = []
        self.contagem_sucesso = 0
        self.contagem_erro = 0  # Corrigindo o nome da variável para 'erro'
        self.total_requisicoes = 0
        self.tempos_requisicoes = []

    def init_ui(self):
        # Inicializa a interface gráfica com widgets e configurações de layout
        self.setWindowTitle("Teste de Estresse")  # Define o título da janela
        self.setFixedSize(500, 400)  # Define o tamanho fixo da janela
        layout = QVBoxLayout()  # Layout vertical para organizar os widgets

        # Definindo a fonte padrão da aplicação
        font = QFont("Arial", 10)
        self.setFont(font)

        # Personalizando a cor de fundo da janela
        palette = self.palette()  # Pega a paleta de cores padrão
        palette.setColor(QPalette.Background, QColor(240, 248, 255))  # Define a cor de fundo
        self.setPalette(palette)

        # Criando e adicionando widgets
        self.label_url = QLabel("Digite a URL para o teste de estresse:")
        self.label_url.setStyleSheet("color: #333;")  # Estilizando a label
        layout.addWidget(self.label_url)  # Adiciona o widget ao layout

        # Campo de entrada de texto para a URL
        self.entry_url = QLineEdit(self)
        self.entry_url.setPlaceholderText("Ex: https://www.exemplo.com")  # Placeholder para o campo de texto
        self.entry_url.setStyleSheet("background-color: white; padding: 5px; border-radius: 5px;")  # Estilo do campo de texto
        layout.addWidget(self.entry_url)

        # Label para o número de requisições
        self.label_requisicoes = QLabel("Número de requisições:")
        self.label_requisicoes.setStyleSheet("font-weight: bold; color: #333;")
        layout.addWidget(self.label_requisicoes)

        # SpinBox para número de requisições
        self.spin_requisicoes = QSpinBox(self)
        self.spin_requisicoes.setValue(99)  # Valor padrão
        self.spin_requisicoes.setMinimum(1)  # Valor mínimo
        self.spin_requisicoes.setStyleSheet("background-color: white; padding: 5px; border-radius: 5px;")
        layout.addWidget(self.spin_requisicoes)

        # Botão para iniciar o teste
        self.button_iniciar = QPushButton("Iniciar Teste de Estresse", self)
        self.button_iniciar.setStyleSheet("background-color: #28a745; color: white; border-radius: 5px; padding: 10px; font-size: 14px;")
        self.button_iniciar.setCursor(Qt.PointingHandCursor)  # Alterando o cursor para mão ao passar por cima
        self.button_iniciar.clicked.connect(self.iniciar_teste)  # Conectando o clique do botão à função iniciar_teste
        layout.addWidget(self.button_iniciar)

        # Barra de progresso para indicar o andamento do teste
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setStyleSheet("QProgressBar {background-color: #f0f0f0; border-radius: 5px; color: #28a745;}")  # Estilo da barra de progresso
        layout.addWidget(self.progress_bar)

        # Label para mostrar os resultados do teste
        self.label_resultado = QLabel("", self)
        self.label_resultado.setStyleSheet("font-weight: bold; color: #333;")
        layout.addWidget(self.label_resultado)

        # Definindo o layout da janela
        self.setLayout(layout)

    def iniciar_teste(self):
        # Função chamada quando o botão "Iniciar Teste de Estresse" é clicado
        url = self.entry_url.text()  # Obtém a URL do campo de texto
        numero_requisicoes = self.spin_requisicoes.value()  # Obtém o número de requisições do SpinBox
        self.enviar_requisicoes(url, numero_requisicoes)  # Chama a função para enviar as requisições

    def enviar_requisicoes(self, url, numero_requisicoes):
        # Função responsável por enviar as requisições HTTP
        self.resultado = []  # Resetando os resultados
        self.contagem_sucesso = 0
        self.contagem_erro = 0  # Corrigido
        self.tempos_requisicoes = []  # Resetando os tempos das requisições

        # Função para realizar uma única requisição HTTP
        def fazer_requisicao():
            try:
                inicio = time.time()  # Marca o tempo de início da requisição
                resposta = requests.get(url)  # Envia a requisição HTTP GET
                tempo_resposta = time.time() - inicio  # Calcula o tempo de resposta
                self.contagem_sucesso += 1  # Incrementa o contador de sucesso
                self.tempos_requisicoes.append(tempo_resposta)  # Armazena o tempo da requisição
                self.resultado.append(f"Status: {resposta.status_code}, Tempo: {tempo_resposta:.4f} segundos")
            except Exception as e:  # Caso ocorra um erro
                self.contagem_erro += 1  # Incrementa o contador de erros
                self.resultado.append(f"Error: {e}")  # Armazena o erro

            self.total_requisicoes += 1  # Incrementa o total de requisições
            self.atualizar_barra_progresso()  # Atualiza a barra de progresso

        # Criando uma lista de threads, cada uma para fazer uma requisição
        threads = []
        for _ in range(numero_requisicoes):
            t = threading.Thread(target=fazer_requisicao)  # Cria uma nova thread para cada requisição
            threads.append(t)
            t.start()  # Inicia a thread

        # Aguarda todas as threads terminarem antes de continuar
        for t in threads:
            t.join()

        # Após todas as requisições, mostra os resultados e gera o PDF
        self.mostrar_resultados()
        self.gerar_relatorio_pdf(numero_requisicoes)

    def atualizar_barra_progresso(self):
        # Função para atualizar a barra de progresso
        progresso = int((self.total_requisicoes / self.spin_requisicoes.value()) * 100)
        self.progress_bar.setValue(progresso)

    def mostrar_resultados(self):
        # Função para exibir os resultados na interface gráfica
        media_tempo = sum(self.tempos_requisicoes) / len(self.tempos_requisicoes) if self.tempos_requisicoes else 0
        self.label_resultado.setText(
            f"Total de requisições: {self.total_requisicoes}\n"
            f"Success: {self.contagem_sucesso}\n"
            f"Error: {self.contagem_erro}\n"
            f"Tempo Médio de Resposta: {media_tempo:.4f} segundos"
        )

        self.progress_bar.setValue(100)  # Barra de progresso chega a 100%

    def gerar_relatorio_pdf(self, numero_requisicoes):
        # Função para gerar o relatorio em PDF
        arquivo_pdf = "Relatorio_teste_estresse.pdf"  # Nome do arquivo PDF
        c = canvas.Canvas(arquivo_pdf, pagesize=letter)  # Cria o objeto PDF com tamanho de página "letter"
        c.setFont("Helvetica", 12)  # Define a fonte para o PDF

        # Escreve as informações principais no PDF
        c.drawString(100, 750, "Relatorio de Teste de Estresse")
        c.drawString(100, 730, f"Total de Requisicoes: {self.total_requisicoes}")
        c.drawString(100, 710, f"Success: {self.contagem_sucesso}")
        c.drawString(100, 690, f"Error: {self.contagem_erro}")
        c.drawString(100, 670, f"Tempo Médio de Resposta: {sum(self.tempos_requisicoes) / len(self.tempos_requisicoes):.4f} segundos")

        # Escreve o log de cada requisição no PDF
        posicao_y = 650  # Posição inicial para escrever os logs
        for linha in self.resultado:
            c.drawString(100, posicao_y, linha[:100])  # Escreve a linha do log (limitada a 100 caracteres)
            posicao_y -= 15  # Move a posição para a próxima linha
            if posicao_y < 100:  # Se o texto alcançar o final da página, cria uma nova página
                c.showPage()
                posicao_y = 750

        # Salva o arquivo PDF
        c.save()  
        print(f"Relatório PDF gerado: {arquivo_pdf}")

def iniciar_teste(self):
    # Função para iniciar o teste de estresse ao clicar no botão
    url = self.entry_url.text()  # Pega a URL inserida pelo usuário
    numero_requisicoes = self.spin_requisicoes.value()  # Pega o número de requisições

    # Verifica se a URL foi fornecida
    if not url:
        QMessageBox.critical(self, "Error", "Por favor, insira uma URL válida.")  # Mostra uma mensagem de erro
        return

    # Desabilita o botão para evitar múltiplos cliques durante o teste
    self.button_iniciar.setEnabled(False)
    self.progress_bar.setValue(0)  # Reseta a barra de progresso
    self.total_requisicoes = 0  # Reseta o contador de requisições

    # Inicia o teste em uma thread separada para não bloquear a interface gráfica
    threading.Thread(target=self.enviar_requisicoes, args=(url, numero_requisicoes)).start()
    self.button_iniciar.setEnabled(True)  # Habilita o botão novamente após o início do teste

# Bloco principal que executa a aplicação
if __name__ == "__main__":
    app = QApplication(sys.argv)  # Cria a aplicação Qt
    janela = AplicativoTesteEstresse()  # Cria a janela do aplicativo
    janela.show()  # Exibe a janela
    sys.exit(app.exec_())  # Executa o loop da aplicação Qt e garante o fechamento correto
