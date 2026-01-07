import shutil
import logging
from pathlib import Path
from src.config import MAPA_EXTENSOES, MESES_PT
from src.utils import FileAnalyzer, LogManager

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
            self._processar_arquivo(arquivo)
        
        self._exibir_relatorio_final()

    def _escanear_arquivos(self):
        return [f for f in self.origem.rglob('*') 
                if f.is_file() and f.name != 'log_organizacao.txt']

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

    def _resolver_duplicidade_nome(self, caminho_arquivo):
        if not caminho_arquivo.exists():
            return caminho_arquivo

        parent = caminho_arquivo.parent
        stem = caminho_arquivo.stem
        suffix = caminho_arquivo.suffix
        counter = 1

        while True:
            novo_nome = f"{stem}_copy_{counter}{suffix}"
            novo_caminho = parent / novo_nome
            if not novo_caminho.exists():
                return novo_caminho
            counter += 1

    def _processar_arquivo(self, arquivo):
        try:
            data_arq = FileAnalyzer.obter_data_criacao(arquivo)
            pasta_final = self._gerar_caminho_destino(arquivo, data_arq)
            arquivo_destino = pasta_final / arquivo.name

            if arquivo_destino.exists():
                hash_origem = FileAnalyzer.calcular_md5(arquivo)
                hash_destino = FileAnalyzer.calcular_md5(arquivo_destino)

                if hash_origem == hash_destino:
                    logging.warning(f"DUPLICATA: {arquivo.name} já existe no destino. Ignorado.")
                    self.stats['duplicado'] += 1
                    return
                else:
                    arquivo_destino = self._resolver_conflito_nome(arquivo_destino)
                    logging.info(f"RENOMEADO: {arquivo.name} -> {arquivo_destino.name}")
                    self.stats['renomeado'] += 1

            if self.simulacao:
                logging.info(f"[SIMULAÇÃO] Moveria: {arquivo} -> {arquivo_destino}")
                self.stats['sucesso'] += 1
            else:
                pasta_final.mkdir(parents=True, exist_ok=True)
                shutil.move(str(arquivo), str(arquivo_destino))
                logging.info(f"MOVIDO: {arquivo.name} -> {arquivo_destino}")
                self.stats['sucesso'] += 1

        except Exception as e:
            logging.error(f"FALHA em {arquivo}: {e}")
            self.stats['erro'] += 1

    def _exibir_relatorio_final(self):
        """Imprime o resumo da operação no console."""
        print("\n" + "="*40)
        print("📊 Relatório de Execução")
        print("="*40)
        print(f"✅ Sucesso (Movidos): {self.stats['sucesso']}")
        print(f"⚠️  Renomeados:       {self.stats['renomeado']}")
        print(f"♻️  Duplicatas:       {self.stats['duplicado']}")
        print(f"❌ Erros:            {self.stats['erro']}")
        print("="*40)

    # def escanear_arquivos(pasta_origem):
        
    #     return [f for f in pasta_origem.rglob('*') if f.is_file() and f.name != 'log_organizacao.txt']

    # def processar_movimentacao(arquivo, pasta_destino_raiz, simulacao=False):
    #     try:
    #         data_arq = obter_data_criacao(arquivo)
    #         pasta_final = gerar_caminho_destino(pasta_destino_raiz, arquivo, data_arq)
    #         arquivo_destino = pasta_final / arquivo.name

    #         if arquivo_destino.exists():
    #             hash_origem = calcular_md5(arquivo)
    #             hash_destino = calcular_md5(arquivo_destino)

    #             if hash_origem == hash_destino:
    #                 logging.warning(f"DUPLICATA: {arquivo.name} já existe no destino. Ignorado.")
    #                 return 'duplicado'
    #             else:
    #                 arquivo_destino = resolver_duplicidade_nome(arquivo_destino)
    #                 logging.info(f"RENOMEADO: {arquivo.name} -> {arquivo_destino.name}")

    #         if simulacao:
    #             logging.info(f"[SIMULAÇÃO] Moveria: {arquivo} -> {arquivo_destino}")
    #             return 'sucesso'
    #         else:
    #             pasta_final.mkdir(parents=True, exist_ok=True)
    #             shutil.move(str(arquivo), str(arquivo_destino))
    #             logging.info(f"MOVIDO: {arquivo.name} -> {arquivo_destino}")
    #             return 'sucesso'

    #     except Exception as e:
    #         logging.error(f"FALHA em {arquivo}: {e}")
    #         return 'erro'