import threading
from PyQt5.QtCore import pyqtSignal, QObject
from main import Engine
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, QFileDialog, QComboBox, QScrollArea, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap, QMovie
from PyQt5.QtCore import Qt

class Worker(QObject):
    update_info = pyqtSignal(str)
    finished = pyqtSignal() 

    def __init__(self, engine):
        super().__init__()
        self.engine = engine

    def login(self):
        response_login = self.engine.login()
        messages = {
            200: "Login efetuado com sucesso!",
            404: "Erro ao logar! Verifique sua conexão ou o WhatsApp Web.",
        }
        self.update_info.emit(messages.get(response_login, "Login ainda está pendente. Tente novamente."))

    def send_message(self, contato, tratamento, mensagem, endosso, saudacao_swicth):
        self.update_info.emit(f"Enviando {self.engine.n_contatos} mensagens personalizadas, por favor aguarde...")
        if not (contato and tratamento and mensagem):
            self.update_info.emit("Por favor, carregue todos os dados necessários antes de enviar.")
            self.finished.emit()
            return
        
        self.engine.enviar_final(contato, tratamento, mensagem, endosso, saudacao_swicth)
        self.update_info.emit(self.engine.tempo_exe)
        self.finished.emit()

class Application(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = Engine()
        self.cam_ico = "images/ico.png"
        self.cam_logo = "images/logo.png"
        self.cam_loading = "images/loading.gif"
        self.fontsize = "10pt"
        self.font_family = "Calibri"
        self.contato = []
        self.tratamento = []
        self.mensagem = ""
        self.endosso = ""
        self.saudacao_swicth = ""
        self.loading_label = None
        self.loading_animation = None
        self.stop_animation = False

        self._setup_ui()
        
        self.worker = Worker(self.engine)
        self.worker.update_info.connect(self._display_info)
        self.worker.finished.connect(self._stop_loading_animation) 

    def _display_info(self, texto):
        self.label_info.setText(texto)
        QMessageBox.information(self, "Informação", texto)

    def _start_login(self):
        threading.Thread(target=self.worker.login).start()

    def _select_file(self):
        caminho_arquivo, _ = QFileDialog.getOpenFileName(
            self, "Selecione um arquivo do computador!", "", "Excel files (*.xlsx);;CSV files (*.csv)"
        )

        if caminho_arquivo:
            try:
                self.contato, self.tratamento = self.engine.processa_base(caminho_arquivo)
                self._display_info(f"Base de contatos com {self.engine.n_contatos} contatos!")
            except Exception as e:
                self._display_info(f"Erro ao carregar o arquivo: {e}")

    def _load_message(self):
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
        threading.Thread(target=self.worker.send_message, args=(self.contato, self.tratamento, self.mensagem, self.endosso, self.saudacao_swicth)).start()

    def _start_loading_animation(self):
        if self.loading_label is None:
            self.loading_label = QLabel(self)
            self.loading_label.setAlignment(Qt.AlignCenter)
            self.loading_label.setFixedSize(100, 100)

            self.loading_layout = QHBoxLayout()
            self.loading_layout.addStretch()
            self.loading_layout.addWidget(self.loading_label)
            self.loading_layout.addStretch()
            self.frame_layout.addLayout(self.loading_layout)

        self.stop_animation = False
        self.loading_animation = QMovie(self.cam_loading)
        self.loading_label.setMovie(self.loading_animation)
        self.loading_animation.start()

    def _stop_loading_animation(self):
        self.stop_animation = True
        if self.loading_label:
            self.loading_animation.stop()
            self.frame_layout.removeItem(self.loading_layout)
            self.loading_label.deleteLater()
            self.loading_label = None
            
    def _style_global(self):
        style = f"""
            QLabel {{
                font-size: {self.fontsize};
                font-family: {self.font_family};
                font-weight: bold; 
            }}
            QPushButton {{
                font-size: {self.fontsize};
                background-color: #075e54;
                color: #ffffff;
                border-radius: 10px;
                font-family: {self.font_family};
                font-weight: bold; 
            }}
            QComboBox {{
                font-size: {self.fontsize};
                font-family: {self.font_family};
            }}
            QTextEdit {{
                font-size: {self.fontsize};
                font-family: {self.font_family};
            }}
            QScrollArea {{
                border: none;
            }}
        """
        return style

    def _setup_ui(self):
        self.setWindowTitle("AutoZap")
        self.setGeometry(100, 100, 550, 700)
        self.setWindowIcon(QIcon(self.cam_ico))

        self.setStyleSheet(self._style_global())

        main_layout = QVBoxLayout(self)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        scroll_content = QWidget(scroll_area)
        self.frame_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)

        main_layout.addWidget(scroll_area)

        self._create_widgets()

    def _load_logo_image(self):
        try:
            pixmap = QPixmap(self.cam_logo)
            label_imagem = QLabel(self)
            label_imagem.setPixmap(pixmap)
            label_imagem.setAlignment(Qt.AlignCenter)
            self.frame_layout.addWidget(label_imagem)
        except Exception as e:
            print(f"Erro ao carregar a imagem: {e}")

    def _create_widgets(self):

        self.label_info = QLabel("Envie mensagem automática para contatos do seu WhatsApp!", self)
        self.label_info.setStyleSheet("color: #25D366;")
        self.label_info.setAlignment(Qt.AlignCenter)

        self._load_logo_image()

        login_button = QPushButton("Logar no WhatsApp", self)
        login_button.clicked.connect(self._start_login)
        self.frame_layout.addWidget(login_button)

        upload_button = QPushButton("Upload da Base de Contato", self)
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
        carregar_button.clicked.connect(self._load_message)
        self.frame_layout.addWidget(carregar_button)

        enviar_button = QPushButton("Enviar Mensagem", self)
        enviar_button.clicked.connect(self._start_sending)
        self.frame_layout.addWidget(enviar_button)

        self.frame_layout.addWidget(self.label_info)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = Application()
    window.show()
    sys.exit(app.exec_())
