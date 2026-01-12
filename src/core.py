import shutil
import logging
from pathlib import Path
from src.config import MAPA_EXTENSOES, MESES_PT
from src.utils import FileAnalyzer, FileRenamer, LogManager

class OrganizadorArquivos:
    def __init__(self, origem: Path, destino: Path, simulacao: bool = False):
        self.origem = origem
        self.destino = destino
        self.simulacao = simulacao        
        self.stats = {
            'sucesso': 0,
            'renomeado': 0,
            'duplicado': 0,
            'erro': 0
        }

    def executar(self):
        LogManager.configurar(self.origem)
        logging.info(f"=== Iniciando Organização (Simulação: {self.simulacao}) ===")
        logging.info(f"Origem: {self.origem}")
        logging.info(f"Destino: {self.destino}")

        arquivos = self._escanear_arquivos()
        total = len(arquivos)
        
        if total == 0:
            logging.info("Nenhum arquivo encontrado para organizar.")
            print("Nenhum arquivo encontrado.")
            return

        print(f"\nEncontrados {total} arquivos. Iniciando processamento...")

        for arquivo in arquivos:
            self.processar_unico_arquivo(arquivo)
        
        self._exibir_relatorio_final()

    def _escanear_arquivos(self):
        lista_arquivos = []
        for item in self.origem.iterdir():
            if item.is_file() and item.name != 'log_organizacao.txt' and not item.name.startswith('.'):
                lista_arquivos.append(item)
        return lista_arquivos

    def _gerar_caminho_destino(self, arquivo, data_obj):
        ext = arquivo.suffix.lower()
        
        if ext in MAPA_EXTENSOES:
            categoria, subpasta = MAPA_EXTENSOES[ext]
            caminho_relativo = Path(categoria) / subpasta
        else:
            caminho_relativo = Path("Outros")

        ano = str(data_obj.year)
        mes = MESES_PT[data_obj.month]
        
        return self.destino / caminho_relativo / ano / mes
    
    def processar_unico_arquivo(self, arquivo):
        try:
            data_arq = FileAnalyzer.obter_data_criacao(arquivo)
            
            pasta_final = self._gerar_caminho_destino(arquivo, data_arq)
            caminho_destino_previsto = pasta_final / arquivo.name

            if caminho_destino_previsto.exists():
                hash_origem = FileAnalyzer.calcular_md5(arquivo)
                hash_destino = FileAnalyzer.calcular_md5(caminho_destino_previsto)

                if hash_origem == hash_destino:
                    logging.warning(f"DUPLICATA: {arquivo.name} já existe no destino. Ignorado.")
                    self.stats['duplicado'] += 1
                    return 
                else:
                    caminho_destino_final = FileRenamer.make_unique_name(caminho_destino_previsto)
                    
                    logging.info(f"RENOMEADO: {arquivo.name} será salvo como {caminho_destino_final.name}")
                    self.stats['renomeado'] += 1
            else:
                caminho_destino_final = caminho_destino_previsto

            if self.simulacao:
                logging.info(f"[SIMULAÇÃO] Moveria: {arquivo.name} -> {caminho_destino_final}")
                self.stats['sucesso'] += 1
            else:
                pasta_final.mkdir(parents=True, exist_ok=True)
                
                shutil.move(str(arquivo), str(caminho_destino_final))
                
                logging.info(f"MOVIDO: {arquivo.name} -> {caminho_destino_final}")
                self.stats['sucesso'] += 1

        except Exception as e:
            logging.error(f"FALHA em {arquivo.name}: {e}")
            self.stats['erro'] += 1

    def _exibir_relatorio_final(self):
        """Imprime o resumo da operação no console."""
        print("\n" + "="*40)
        print("RELATORIO DE EXECUCAO")
        print("="*40)
        print(f"[OK] Sucesso (Movidos): {self.stats['sucesso']}")
        print(f"[!]  Renomeados:       {self.stats['renomeado']}")
        print(f"[-]  Duplicatas:       {self.stats['duplicado']}")
        print(f"[X]  Erros:            {self.stats['erro']}")
        print("="*40)
