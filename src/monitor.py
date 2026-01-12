import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.core import OrganizadorArquivos

class OrganizadorHandler(FileSystemEventHandler):
    def __init__(self, organizador: OrganizadorArquivos):
        self.organizador = organizador

    def on_created(self, event):
        if event.is_directory:
            return

        caminho_arquivo = Path(event.src_path)
        
        if caminho_arquivo.name.startswith('.') or caminho_arquivo.name.endswith('.tmp'):
            return

        logging.info(f"[MONITOR] Novo arquivo detectado: {caminho_arquivo.name}")
        
        time.sleep(1) 
        
        self.organizador.processar_unico_arquivo(caminho_arquivo)

class MonitorPasta:
    def __init__(self, organizador: OrganizadorArquivos):
        self.organizador = organizador
        self.observer = Observer()
        self.handler = OrganizadorHandler(organizador)

    def iniciar(self):
        pasta_origem = str(self.organizador.origem)
        
        logging.info(f"--> INICIANDO MONITORAMENTO EM TEMPO REAL: {pasta_origem}")
        logging.info("--> Pressione Ctrl+C para parar.")
        print(f"\n[Ouvindo] Monitorando a pasta: {pasta_origem}")
        print("[Ouvindo] Cole arquivos lá para ver a mágica. (Ctrl+C para sair)")

        self.observer.schedule(self.handler, pasta_origem, recursive=False)
        self.observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.parar()

    def parar(self):
        logging.info("Parando monitoramento...")
        self.observer.stop()
        self.observer.join()
        print("\nMonitoramento encerrado.")