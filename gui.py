import threading
from main import Engine
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, QFileDialog, QComboBox, QScrollArea, QFrame
from PyQt5.QtGui import QIcon, QPixmap, QMovie
from PyQt5.QtCore import Qt, QTimer

class Application(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = Engine()
        self.cam_ico = "images/ico.png"
        self.cam_logo = "images/logo.png"
        self.cam_loading = "images/loading.gif"
        self.contato = []
        self.tratamento = []
        self.mensagem = ""
        self.endosso = ""
        self.saudacao_swicth = ""
        self.loading_label = None
        self.loading_animation = None
        self.stop_animation = False

        self._setup_ui()

    def _display_info(self, texto):
        """Exibe uma mensagem de informação na interface."""
        self.info_label.setText(texto)
        self.label_info2.setText(texto)

    def _start_login(self):
        threading.Thread(target=self._login).start()

    def _login(self):
        """Realiza o login no WhatsApp."""
        response_login = self.engine.login()
        messages = {
            200: "Login efetuado com sucesso!",
            404: "Erro ao logar! Verifique sua conexão ou o WhatsApp Web.",
        }
        self._display_info(messages.get(response_login, "Login ainda está pendente. Tente novamente."))

    def _select_file(self):
        """Permite ao usuário selecionar um arquivo CSV."""
        caminho_arquivo, _ = QFileDialog.getOpenFileName(
            self, "Selecione um arquivo do computador!", "", "Excel files (*.xlsx);;CSV files (*.csv)"
        )

        if caminho_arquivo:
            try:
                self.contato, self.tratamento = self.engine.processa_base(caminho_arquivo)
                self._display_info("Arquivo carregado com sucesso!")
            except Exception as e:
                self._display_info(f"Erro ao carregar o arquivo: {e}")

    def _load_message(self):
        """Carrega a mensagem, saudação e endosso da interface."""
        saudacao = self.combobox.currentText()
        mensagem = self.mensagem_textbox.toPlainText().strip()
        endosso = self.endosso_textbox.toPlainText().strip()

        if all([saudacao, mensagem, endosso]):
            self.saudacao_swicth = saudacao
            self.mensagem = mensagem
            self.endosso = endosso
            self._display_info("Mensagem carregada com sucesso!")
        else:
            self._display_info("A mensagem está vazia. Carregue uma mensagem válida.")

    def _start_sending(self):
        self._start_loading_animation()
        threading.Thread(target=self._send_message).start()

    def _send_message(self):
        """Envia a mensagem para os contatos."""
        self._display_info("Enviando as mensagens, por favor aguarde...")
        if not (self.contato and self.tratamento and self.mensagem):
            self._display_info("Por favor, carregue todos os dados necessários antes de enviar.")
            self._stop_loading_animation()
            return
        
        self.engine.enviar(self.contato, self.tratamento, self.mensagem, self.endosso, self.saudacao_swicth)
        self._display_info(self.engine.tempo_exe)
        self._stop_loading_animation()

    def _start_loading_animation(self):
        if self.loading_label is None:
            self.loading_label = QLabel(self)
            self.loading_label.setAlignment(Qt.AlignCenter)
            self.loading_label.setFixedSize(100, 100)
            self.frame_layout.addWidget(self.loading_label)

        self.stop_animation = False
        self.loading_animation = QMovie(self.cam_loading)
        self.loading_label.setMovie(self.loading_animation)
        self.loading_animation.start()

    def _stop_loading_animation(self):
        self.stop_animation = True
        if self.loading_label:
            self.loading_animation.stop()
            self.frame_layout.removeWidget(self.loading_label)
            self.loading_label.deleteLater()
            self.loading_label = None

    def _setup_ui(self):
        """Configura a interface do usuário."""
        self.setWindowTitle("AutoZap")
        self.setGeometry(100, 100, 350, 650)
        self.setWindowIcon(QIcon(self.cam_ico))

        main_layout = QVBoxLayout(self)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        scroll_content = QWidget(scroll_area)
        self.frame_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)

        main_layout.addWidget(scroll_area)

        self._create_widgets()

    def _load_logo_image(self):
        """Carrega a imagem do logo."""
        try:
            pixmap = QPixmap(self.cam_logo)
            label_imagem = QLabel(self)
            label_imagem.setPixmap(pixmap)
            label_imagem.setAlignment(Qt.AlignCenter)
            self.frame_layout.addWidget(label_imagem)
        except Exception as e:
            print(f"Erro ao carregar a imagem: {e}")

    def _create_widgets(self):
        """Cria os widgets da interface."""
        self.info_label = QLabel("Faça seu login no Whatsapp!", self)
        self.info_label.setStyleSheet("color: #25D366;")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.frame_layout.addWidget(self.info_label)

        self.label_info2 = QLabel("Envie mensagem automática para contatos do seu WhatsApp!", self)
        self.label_info2.setStyleSheet("color: #25D366;")
        self.label_info2.setAlignment(Qt.AlignCenter)

        self._load_logo_image()

        login_button = QPushButton("Logar no WhatsApp", self)
        login_button.setStyleSheet("background-color: #075e54; color: #ffffff;")
        login_button.clicked.connect(self._start_login)
        self.frame_layout.addWidget(login_button)

        upload_button = QPushButton("Upload da Base de Contato", self)
        upload_button.setStyleSheet("background-color: #075e54; color: #ffffff;")
        upload_button.clicked.connect(self._select_file)
        self.frame_layout.addWidget(upload_button)

        saudacao_label = QLabel("Selecione uma opção de Saudação Personalizada:", self)
        self.frame_layout.addWidget(saudacao_label)

        self.combobox = QComboBox(self)
        self.combobox.addItems(["Sem Saudação", "Bom dia", "Boa tarde", "Boa noite", "Olá", "Oi", "Prezado", "Vocativo"])
        self.frame_layout.addWidget(self.combobox)

        mensagem_label = QLabel("Insira a mensagem que será enviada a sua base de contatos:", self)
        self.frame_layout.addWidget(mensagem_label)

        self.mensagem_textbox = QTextEdit(self)
        self.frame_layout.addWidget(self.mensagem_textbox)

        endosso_label = QLabel("Insira aqui o endosso/assinatura da sua mensagem:", self)
        self.frame_layout.addWidget(endosso_label)

        self.endosso_textbox = QTextEdit(self)
        self.frame_layout.addWidget(self.endosso_textbox)

        carregar_button = QPushButton("Carregar Mensagem", self)
        carregar_button.setStyleSheet("background-color: #075e54; color: #ffffff;")
        carregar_button.clicked.connect(self._load_message)
        self.frame_layout.addWidget(carregar_button)

        enviar_button = QPushButton("Enviar Mensagem", self)
        enviar_button.setStyleSheet("background-color: #075e54; color: #ffffff;")
        enviar_button.clicked.connect(self._start_sending)
        self.frame_layout.addWidget(enviar_button)

        self.frame_layout.addWidget(self.label_info2)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = Application()
    window.show()
    sys.exit(app.exec_())
