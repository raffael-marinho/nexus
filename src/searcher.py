import re
from pathlib import Path
from collections import defaultdict
import datetime

class MecanismoBusca:
    def __init__(self, diretorio_base):
        self.diretorio_base = Path(diretorio_base)
        
        # --- ESTRUTURAS DE DADOS: ÍNDICE INVERTIDO ---
        # Mapeiam uma chave (ex: palavra, extensão, data) para um Conjunto (Set) de arquivos.
        self.indice_nomes = defaultdict(set)
        self.indice_extensoes = defaultdict(set)
        self.indice_datas = defaultdict(set)
        self.todos_arquivos = set()
        
        self.indexado = False

    def _tokenizar(self, texto):
        """Quebra o nome do arquivo em palavras base (ignorando símbolos e números irrelevantes)."""
        return re.findall(r'[a-zA-Z0-9]+', texto.lower())

    def indexar_arquivos(self):
        """
        Varre a pasta recursivamente e constrói a árvore de busca na memória.
        Isso é executado apenas uma vez (ou quando o usuário manda atualizar).
        """
        self.indice_nomes.clear()
        self.indice_extensoes.clear()
        self.indice_datas.clear()
        self.todos_arquivos.clear()

        if not self.diretorio_base.exists() or not self.diretorio_base.is_dir():
            return 0

        for caminho in self.diretorio_base.rglob('*'):
            if caminho.is_file():
                self.todos_arquivos.add(caminho)
                
                # 1. Indexa pela Extensão
                ext = caminho.suffix.lower()
                self.indice_extensoes[ext].add(caminho)
                
                # 2. Indexa pela Data (Formato: YYYY-MM)
                try:
                    timestamp = caminho.stat().st_mtime
                    data_str = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m')
                    self.indice_datas[data_str].add(caminho)
                except Exception:
                    pass
                    
                # 3. Indexa pelo Nome (Índice Invertido Clássico)
                tokens = self._tokenizar(caminho.stem)
                for token in tokens:
                    self.indice_nomes[token].add(caminho)
        
        self.indexado = True
        return len(self.todos_arquivos)

    def buscar(self, termo="", extensao="", data_ano_mes=""):
        """
        Realiza a busca cruzando as árvores.
        Usa Teoria de Conjuntos (Intersection) para performance ultra-rápida.
        """
        if not self.indexado:
            self.indexar_arquivos()

        # Começamos assumindo que todos os arquivos são válidos
        resultados = set(self.todos_arquivos)

        
        # Filtro 1: Extensão (O(1))
        if extensao:
            extensao = extensao.lower()
            if not extensao.startswith('.'):
                extensao = '.' + extensao
            resultados = resultados.intersection(self.indice_extensoes.get(extensao, set()))

        # Filtro 2: Data (O(1))
        if data_ano_mes:
            resultados = resultados.intersection(self.indice_datas.get(data_ano_mes, set()))

        # Filtro 3: Nome do Arquivo (O(N) sobre chaves, O(1) na interseção)
        if termo:
            termo = termo.lower()
            arquivos_com_termo = set()
            
            # Busca parcial (Se buscar "relat", acha "relatorio")
            for chave_token, arquivos in self.indice_nomes.items():
                if termo in chave_token:
                    arquivos_com_termo.update(arquivos)
            
            resultados = resultados.intersection(arquivos_com_termo)

        # Retorna os caminhos ordenados alfabeticamente
        return sorted(list(resultados))