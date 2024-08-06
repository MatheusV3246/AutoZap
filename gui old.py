import threading
from main import Engine

from tkinter import Tk, Label, Button, Text, PhotoImage, Canvas, Frame, Scrollbar
from tkinter.filedialog import askopenfilename
from tkinter import ttk
from PIL import Image, ImageTk, ImageSequence

class Application:
    def __init__(self, janela):
        self._janela = janela
        self._janela.geometry("700x750")
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
        self.info_label.config(text=texto)
        self.label_info2.config(text=texto)

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
        caminho_arquivo = askopenfilename(
            title="Selecione um arquivo do computador!",
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")]
        )

        if caminho_arquivo:
            try:
                self.contato, self.tratamento = self.engine.processa_base(caminho_arquivo)
                self._display_info("Arquivo carregado com sucesso!")
            except Exception as e:
                self._display_info(f"Erro ao carregar o arquivo: {e}")

    def _load_message(self):
        """Carrega a mensagem, saudação e endosso da interface."""
        saudacao = self.combobox.get()
        mensagem = self.mensagem_textbox.get("1.0", "end-1c").strip()
        endosso = self.endosso_textbox.get("1.0", "end-1c").strip()

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
            self.loading_label = Label(self.frame, bg="#ece5dd")
            self.loading_label.grid(column=0, row=13, padx=13, pady=5, sticky="nsew")

        self.stop_animation = False
        self.loading_animation = threading.Thread(target=self._animate_loading)
        self.loading_animation.start()

    def _animate_loading(self):
        try:
            img = Image.open(self.cam_loading)
            for frame in ImageSequence.Iterator(img):
                if self.stop_animation:
                    break
                frame_image = ImageTk.PhotoImage(frame)
                self.loading_label.config(image=frame_image)
                self.loading_label.image = frame_image
                self.loading_label.update()
                self.loading_label.after(100)
        except Exception as e:
            print(f"Erro ao carregar a imagem: {e}")

    def _stop_loading_animation(self):
        self.stop_animation = True
        if self.loading_label:
            self.loading_label.config(image='')
            self.loading_label.image = None
            self.loading_label = None

    def _setup_ui(self):
        """Configura a interface do usuário."""
        self._janela.title("AutoZap")
        self._janela.configure(bg="#ece5dd")
        self._set_window_icon()
        self._create_scrollable_frame()
        self._create_widgets()

    def _set_window_icon(self):
        """Define o ícone da janela."""
        try:
            self._janela.iconphoto(False, PhotoImage(file=self.cam_ico))
        except Exception as e:
            print(f"Erro ao definir o ícone da janela: {e}")

    def _create_scrollable_frame(self):
        """Cria um frame com barra de rolagem."""
        self.canvas = Canvas(self._janela, bg="#ece5dd", highlightthickness=0)
        self.frame = Frame(self.canvas, bg="#ece5dd")
        self.scrollbar = Scrollbar(self._janela, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        self.frame.bind("<Configure>", self.on_frame_configure)

    def _load_logo_image(self):
        """Carrega a imagem do logo."""
        try:
            imagem = Image.open(self.cam_logo)
            imagem_tk = ImageTk.PhotoImage(imagem)
            label_imagem = Label(self.frame, image=imagem_tk, bg="#ece5dd")
            label_imagem.image = imagem_tk
            label_imagem.grid(column=0, row=0, padx=10, pady=5, sticky="nsew")
        except Exception as e:
            print(f"Erro ao carregar a imagem: {e}")

    def _create_widgets(self):
        """Cria os widgets da interface."""
        self.info_label = Label(self.frame, text="Faça seu login no Whatsapp!", fg="#25D366", bg="#ece5dd", font=("Arial", 14))
        self.info_label.grid(column=0, row=1, padx=10, pady=5, sticky="nsew")

        self.label_info2 = Label(self.frame, text="Envie mensagem automática para contatos do seu WhatsApp!", fg="#25D366", bg="#ece5dd", font=("Arial", 14))
        self.label_info2.grid(column=0, row=12, padx=12, pady=5, sticky="nsew")

        self._load_logo_image()

        Button(self.frame, text="Logar no WhatsApp", command=self._start_login, bg="#075e54", fg="#ffffff", font=("Arial", 11)).grid(column=0, row=2, padx=10, pady=5, sticky="ew")
        Button(self.frame, text="Upload da Base de Contato", command=self._select_file, bg="#075e54", fg="#ffffff", font=("Arial", 11)).grid(column=0, row=3, padx=10, pady=5, sticky="ew")

        Label(self.frame, text="Selecione uma opção de Saudação Personalizada:", bg="#ece5dd", font=("Arial", 11)).grid(column=0, row=4, padx=10, pady=5, sticky="w")
        self.combobox = ttk.Combobox(self.frame, values=["Sem Saudação", "Bom dia", "Boa tarde", "Boa noite", "Olá", "Oi", "Prezado", "Vocativo"])
        self.combobox.grid(column=0, row=5, padx=10, pady=5, sticky="ew")
        self.combobox.current(0)

        Label(self.frame, text="Insira a mensagem que será enviada a sua base de contatos:", bg="#ece5dd", font=("Arial", 11)).grid(column=0, row=6, padx=10, pady=5, sticky="w")
        self.mensagem_textbox = Text(self.frame, bg="#ffffff", fg="#000000", wrap="word", height=7, font=("Arial", 11))
        self.mensagem_textbox.grid(column=0, row=7, padx=10, pady=5, sticky="w")

        Label(self.frame, text="Insira aqui o endosso/assinatura da sua mensagem:", bg="#ece5dd", font=("Arial", 11)).grid(column=0, row=8, padx=10, pady=5, sticky="w")
        self.endosso_textbox = Text(self.frame, bg="#ffffff", fg="#000000", wrap="word", height=2, font=("Arial", 11))
        self.endosso_textbox.grid(column=0, row=9, padx=10, pady=5, sticky="w")

        Button(self.frame, text="Carregar Mensagem", command=self._load_message, bg="#075e54", fg="#ffffff", font=("Arial", 11)).grid(column=0, row=10, padx=10, pady=5, sticky="ew")
        Button(self.frame, text="Enviar Mensagem", command=self._start_sending, bg="#075e54", fg="#ffffff", font=("Arial", 11)).grid(column=0, row=11, padx=10, pady=5, sticky="ew")

    def on_frame_configure(self, event):
        """Atualiza a área de rolagem quando o tamanho do frame muda."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

if __name__ == "__main__":
    janela = Tk()
    app = Application(janela)
    janela.mainloop()

