import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.core import OrganizadorArquivos

class OrganizadorHandler(FileSystemEventHandler):
    def __init__(self, organizador: OrganizadorArquivos):
        self.organizador = organizador

    def _processar(self, caminho_arquivo):
        """Método auxiliar para validar e chamar o organizador"""
        caminho = Path(caminho_arquivo)
        
        print(f"[DEBUG] Evento detectado em: {caminho.name}")

        if caminho.name.startswith('.') or caminho.name.endswith('.tmp') or 'crdownload' in caminho.name:
            return

        logging.info(f"[MONITOR] Processando: {caminho.name}")
        
        time.sleep(2) 
        
        self.organizador.processar_unico_arquivo(caminho)

    def on_created(self, event):
        if not event.is_directory:
            print(f"[DEBUG] Criação detectada: {event.src_path}")
            self._processar(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            print(f"[DEBUG] Movimentação/Renomeação: {event.dest_path}")
            self._processar(event.dest_path)

class MonitorPasta:
    def __init__(self, organizador: OrganizadorArquivos):
        self.organizador = organizador
        self.observer = Observer()
        self.handler = OrganizadorHandler(organizador)

    def iniciar(self):
        pasta_origem = str(self.organizador.origem)
        
        logging.info(f"--> INICIANDO MONITORAMENTO: {pasta_origem}")
        print(f"\n[Ouvindo] Monitorando a pasta: {pasta_origem}")
        print("[Ouvindo] Cole arquivos ou salve downloads lá. (Ctrl+C para sair)")

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