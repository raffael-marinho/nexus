import customtkinter as ctk
from tkinter import filedialog
import logging
import threading
from pathlib import Path

# Certifique-se que o import está correto para o nome do seu arquivo
from src.core import OrganizadorArquivos 

ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  

class TextHandler(logging.Handler):
    """Classe segura para thread que envia logs para a GUI"""
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        # O segredo: agendar a atualização na thread principal da interface
        self.text_widget.after(0, self._append_text, msg)

    def _append_text(self, msg):
        try:
            self.text_widget.configure(state="normal")
            self.text_widget.insert("end", msg + "\n")
            self.text_widget.see("end") 
            self.text_widget.configure(state="disabled")
        except Exception:
            pass

class FileOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Organizador de Arquivos - Raffael Marinho")
        self.geometry("750x600")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1) 

        # --- Frames de Seleção ---
        self.frame_origem = ctk.CTkFrame(self)
        self.frame_origem.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        ctk.CTkLabel(self.frame_origem, text="Pasta de Origem (Onde estão os arquivos?):", font=("Roboto", 14, "bold")).pack(side="top", anchor="w", padx=10, pady=5)
        self.entry_origem = ctk.CTkEntry(self.frame_origem, placeholder_text="Ex: C:/Users/silva/Downloads")
        self.entry_origem.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        ctk.CTkButton(self.frame_origem, text="Selecionar", command=self.selecionar_origem, width=100).pack(side="right", padx=10)

        self.frame_destino = ctk.CTkFrame(self)
        self.frame_destino.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(self.frame_destino, text="Pasta de Destino (Para onde vão?):", font=("Roboto", 14, "bold")).pack(side="top", anchor="w", padx=10, pady=5)
        self.entry_destino = ctk.CTkEntry(self.frame_destino, placeholder_text="Ex: D:/Backup")
        self.entry_destino.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        ctk.CTkButton(self.frame_destino, text="Selecionar", command=self.selecionar_destino, width=100).pack(side="right", padx=10)

        # --- Ações ---
        self.frame_acoes = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_acoes.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.switch_simulacao = ctk.CTkSwitch(self.frame_acoes, text="Modo Simulação (Só testa)")
        self.switch_simulacao.select() 
        self.switch_simulacao.pack(side="left", padx=10)

        self.btn_executar = ctk.CTkButton(self.frame_acoes, text="INICIAR ORGANIZAÇÃO", 
                                          command=self.iniciar_thread, 
                                          fg_color="#2CC985", hover_color="#229A65",
                                          height=40, font=("Roboto", 14, "bold"))
        self.btn_executar.pack(side="right", padx=10, fill="x", expand=True)

        # --- Log ---
        ctk.CTkLabel(self, text="Log de Execução:", anchor="w").grid(row=3, column=0, padx=20, pady=(10,0), sticky="w")
        self.textbox_log = ctk.CTkTextbox(self, state="disabled", font=("Consolas", 12))
        self.textbox_log.grid(row=4, column=0, padx=20, pady=(5, 20), sticky="nsew")

        self.setup_logging()

    def setup_logging(self):
        # Limpa handlers anteriores para evitar duplicação ou conflitos
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            
        logger.setLevel(logging.INFO)
        
        # Handler da Interface
        text_handler = TextHandler(self.textbox_log)
        formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S')
        text_handler.setFormatter(formatter)
        logger.addHandler(text_handler)
        
        # Handler do Terminal (para você ver erros críticos no VS Code)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    def selecionar_origem(self):
        path = filedialog.askdirectory()
        if path:
            self.entry_origem.delete(0, "end")
            self.entry_origem.insert(0, path)

    def selecionar_destino(self):
        path = filedialog.askdirectory()
        if path:
            self.entry_destino.delete(0, "end")
            self.entry_destino.insert(0, path)

    def iniciar_thread(self):
        threading.Thread(target=self.executar_organizacao, daemon=True).start()

    def executar_organizacao(self):
        origem = self.entry_origem.get()
        destino = self.entry_destino.get()
        simulacao = bool(self.switch_simulacao.get())

        if not origem or not destino:
            logging.error("ERRO: Selecione as pastas de origem e destino!")
            return

        self.btn_executar.configure(state="disabled", text="Processando...")
        self.textbox_log.configure(state="normal")
        self.textbox_log.delete("1.0", "end")
        self.textbox_log.configure(state="disabled")

        try:
            organizador = OrganizadorArquivos(Path(origem), Path(destino), simulacao=simulacao)
            organizador.executar()
            
            logging.info("="*30)
            logging.info("PROCESSO FINALIZADO!")
            if simulacao:
                logging.info("Dica: Desmarque 'Modo Simulação' para mover os arquivos.")
        except Exception as e:
            logging.error(f"Erro fatal: {e}")
        finally:
            # Reabilita o botão (usando after para segurança de thread)
            self.after(0, lambda: self.btn_executar.configure(state="normal", text="INICIAR ORGANIZAÇÃO"))

if __name__ == "__main__":
    app = FileOrganizerApp()
    app.mainloop()