import customtkinter as ctk
from tkinter import filedialog
import logging
import threading
from pathlib import Path
import subprocess
import platform

from src.core import OrganizadorArquivos 
from src.searcher import MecanismoBusca # <-- Importamos nossa nova classe

ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  

class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
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

        self.title("Organizador e Buscador - Raffael Marinho")
        self.geometry("800x650")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SISTEMA DE ABAS ---
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.aba_organizar = self.tabview.add("1. Organizar Arquivos")
        self.aba_buscar = self.tabview.add("2. Busca Avançada")

        self.setup_aba_organizar()
        self.setup_aba_buscar()
        self.setup_logging()
        
        # Variável para o motor de busca
        self.motor_busca = None

    # ==========================================
    # ABA 1: ORGANIZAÇÃO (Código Original)
    # ==========================================
    def setup_aba_organizar(self):
        self.aba_organizar.grid_columnconfigure(0, weight=1)
        self.aba_organizar.grid_rowconfigure(3, weight=1)

        self.frame_origem = ctk.CTkFrame(self.aba_organizar)
        self.frame_origem.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        
        ctk.CTkLabel(self.frame_origem, text="Pasta de Origem:", font=("Roboto", 14, "bold")).pack(side="top", anchor="w", padx=10, pady=2)
        self.entry_origem = ctk.CTkEntry(self.frame_origem, placeholder_text="Ex: C:/Downloads")
        self.entry_origem.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        ctk.CTkButton(self.frame_origem, text="Selecionar", command=lambda: self.selecionar_pasta(self.entry_origem), width=100).pack(side="right", padx=10)

        self.frame_destino = ctk.CTkFrame(self.aba_organizar)
        self.frame_destino.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(self.frame_destino, text="Pasta de Destino (Backup):", font=("Roboto", 14, "bold")).pack(side="top", anchor="w", padx=10, pady=2)
        self.entry_destino = ctk.CTkEntry(self.frame_destino, placeholder_text="Ex: D:/Backup")
        self.entry_destino.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        ctk.CTkButton(self.frame_destino, text="Selecionar", command=lambda: self.selecionar_pasta(self.entry_destino), width=100).pack(side="right", padx=10)

        self.frame_acoes = ctk.CTkFrame(self.aba_organizar, fg_color="transparent")
        self.frame_acoes.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.switch_simulacao = ctk.CTkSwitch(self.frame_acoes, text="Modo Simulação")
        self.switch_simulacao.select() 
        self.switch_simulacao.pack(side="left", padx=10)

        self.btn_executar = ctk.CTkButton(self.frame_acoes, text="INICIAR ORGANIZAÇÃO", command=self.iniciar_thread_org, fg_color="#2CC985", hover_color="#229A65", height=40, font=("Roboto", 14, "bold"))
        self.btn_executar.pack(side="right", padx=10, fill="x", expand=True)

        self.textbox_log = ctk.CTkTextbox(self.aba_organizar, state="disabled", font=("Consolas", 12))
        self.textbox_log.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

    # ==========================================
    # ABA 2: BUSCA AVANÇADA (Novo Recurso)
    # ==========================================
    def setup_aba_buscar(self):
        self.aba_buscar.grid_columnconfigure(0, weight=1)
        self.aba_buscar.grid_rowconfigure(3, weight=1) # Mudou de 2 para 3 por causa do novo rótulo
        
        # 1. Controles Superiores
        frame_controles = ctk.CTkFrame(self.aba_buscar)
        frame_controles.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.btn_indexar = ctk.CTkButton(frame_controles, text="1º) Indexar Pasta de Backup", command=self.iniciar_indexacao)
        self.btn_indexar.pack(side="top", fill="x", padx=10, pady=10)
        
        lbl_info = ctk.CTkLabel(frame_controles, text="A busca usará a 'Pasta de Destino' configurada na aba 1.", text_color="gray")
        lbl_info.pack(side="top", pady=(0, 10))

        # 2. Filtros
        frame_filtros = ctk.CTkFrame(self.aba_buscar)
        frame_filtros.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(frame_filtros, text="Nome:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_busca_nome = ctk.CTkEntry(frame_filtros, placeholder_text="Ex: relatorio")
        self.entry_busca_nome.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(frame_filtros, text="Extensão:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_busca_ext = ctk.CTkEntry(frame_filtros, placeholder_text="Ex: .pdf", width=80)
        self.entry_busca_ext.grid(row=0, column=3, padx=5, pady=5)
        
        ctk.CTkLabel(frame_filtros, text="Data (Ano-Mês):").grid(row=0, column=4, padx=5, pady=5)
        self.entry_busca_data = ctk.CTkEntry(frame_filtros, placeholder_text="Ex: 2024-05", width=100)
        self.entry_busca_data.grid(row=0, column=5, padx=5, pady=5)
        
        self.btn_buscar = ctk.CTkButton(frame_filtros, text="🔍 Buscar", command=self.realizar_busca, fg_color="#3b82f6")
        self.btn_buscar.grid(row=0, column=6, padx=10, pady=5)
        
        frame_filtros.grid_columnconfigure(1, weight=1)

        # 3. Resultados
        self.lbl_dica = ctk.CTkLabel(self.aba_buscar, text="💡 Dica: Dê um duplo-clique no caminho de um arquivo abaixo para abrir sua pasta.", text_color="#2CC985", font=("Roboto", 12, "bold"))
        self.lbl_dica.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="w")

        self.textbox_resultados = ctk.CTkTextbox(self.aba_buscar, font=("Consolas", 12))
        self.textbox_resultados.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        
        # O "binding" (ligação) do evento de clique duplo do mouse com a nossa função
        self.textbox_resultados.bind("<Double-Button-1>", self.abrir_local_arquivo)

    # ==========================================
    # LÓGICA COMPARTILHADA E EVENTOS
    # ==========================================
    def setup_logging(self):
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        logger.setLevel(logging.INFO)
        text_handler = TextHandler(self.textbox_log)
        text_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S'))
        logger.addHandler(text_handler)

    def selecionar_pasta(self, entry_widget):
        path = filedialog.askdirectory()
        if path:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, path)

    # --- Funções Aba 1 ---
    def iniciar_thread_org(self):
        threading.Thread(target=self.executar_organizacao, daemon=True).start()

    def executar_organizacao(self):
        origem = self.entry_origem.get()
        destino = self.entry_destino.get()
        simulacao = bool(self.switch_simulacao.get())

        if not origem or not destino:
            logging.error("ERRO: Selecione as pastas!")
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
            
            # Se moveu arquivos reais, avisa a Aba 2 que o índice está desatualizado
            if not simulacao and self.motor_busca:
                self.motor_busca.indexado = False 
                
        except Exception as e:
            logging.error(f"Erro fatal: {e}")
        finally:
            self.after(0, lambda: self.btn_executar.configure(state="normal", text="INICIAR ORGANIZAÇÃO"))

    # --- Funções Aba 2 ---
    def iniciar_indexacao(self):
        threading.Thread(target=self._processar_indexacao, daemon=True).start()
        
    def _processar_indexacao(self):
        destino = self.entry_destino.get()
        if not destino:
            self._print_resultado("ERRO: Defina a 'Pasta de Destino' na Aba 1 primeiro.")
            return
            
        self.btn_indexar.configure(state="disabled", text="Construindo Árvore...")
        self._print_resultado("Escaneando e construindo Índice Invertido...\nIsso pode demorar alguns segundos.")
        
        self.motor_busca = MecanismoBusca(destino)
        qtd = self.motor_busca.indexar_arquivos()
        
        self._print_resultado(f"Índice construído com sucesso!\n{qtd} arquivos mapeados na memória.\nPronto para buscas instantâneas.")
        self.btn_indexar.configure(state="normal", text="Atualizar Índice (Re-indexar)")

    def realizar_busca(self):
        if not self.motor_busca or not self.motor_busca.indexado:
            self._print_resultado("AVISO: Você precisa Indexar a pasta primeiro clicando no botão acima.")
            return
            
        nome = self.entry_busca_nome.get().strip()
        ext = self.entry_busca_ext.get().strip()
        data = self.entry_busca_data.get().strip()
        
        resultados = self.motor_busca.buscar(termo=nome, extensao=ext, data_ano_mes=data)
        
        self._print_resultado(f"Encontrados {len(resultados)} resultados:\n" + "-"*40 + "\n")
        
        # Mostramos no máximo 500 para não travar a UI em caso de buscas amplas
        for caminho in resultados[:500]:
            self.textbox_resultados.insert("end", f"{caminho}\n")
            
        if len(resultados) > 500:
            self.textbox_resultados.insert("end", f"\n... e mais {len(resultados)-500} arquivos ocultados.\n")

    def _print_resultado(self, texto):
        """Limpa a tela de resultados e escreve a nova mensagem."""
        self.textbox_resultados.delete("1.0", "end")
        self.textbox_resultados.insert("end", texto + "\n")

    def abrir_local_arquivo(self, event):
        """Identifica a linha clicada e abre a pasta no sistema operacional."""
        try:
            # Pega a posição exata (x, y) do clique do mouse dentro do texto e traduz para linha
            index = self.textbox_resultados.index(f"@{event.x},{event.y}")
            linha = index.split('.')[0]
            
            # Pega o texto da linha inteira (do caractere 0 até o final da linha)
            caminho_str = self.textbox_resultados.get(f"{linha}.0", f"{linha}.end").strip()
            
            caminho = Path(caminho_str)
            
            # Verifica se o texto clicado é realmente um caminho de arquivo válido
            if caminho.exists() and caminho.is_file():
                sistema = platform.system()
                
                # Comando específico para cada Sistema Operacional
                if sistema == "Windows":
                    # No Windows, abre o explorer já selecionando o arquivo
                    subprocess.run(['explorer', '/select,', str(caminho)])
                elif sistema == "Darwin": # macOS
                    subprocess.run(['open', '-R', str(caminho)])
                else: # Linux (Abre só a pasta)
                    subprocess.run(['xdg-open', str(caminho.parent)])
                    
        except Exception as e:
            logging.error(f"Erro ao tentar abrir pasta: {e}")

if __name__ == "__main__":
    app = FileOrganizerApp()
    app.mainloop()