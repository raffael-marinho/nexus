import shutil
import logging
from pathlib import Path
from src.config import MAPA_EXTENSOES, MESES_PT
from src.utils import calcular_md5, obter_data_criacao

def gerar_caminho_destino(pasta_base, arquivo, data_obj):
    ext = arquivo.suffix.lower()
    
    if ext in MAPA_EXTENSOES:
        categoria, subpasta = MAPA_EXTENSOES[ext]
        caminho_relativo = Path(categoria) / subpasta
    else:
        caminho_relativo = Path("Outros")

    ano = str(data_obj.year)
    mes = MESES_PT[data_obj.month]
    
    return pasta_base / caminho_relativo / ano / mes

def resolver_duplicidade_nome(caminho_arquivo):
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

def escanear_arquivos(pasta_origem):
    
    return [f for f in pasta_origem.rglob('*') if f.is_file() and f.name != 'log_organizacao.txt']

def processar_movimentacao(arquivo, pasta_destino_raiz, simulacao=False):
    try:
        data_arq = obter_data_criacao(arquivo)
        pasta_final = gerar_caminho_destino(pasta_destino_raiz, arquivo, data_arq)
        arquivo_destino = pasta_final / arquivo.name

        if arquivo_destino.exists():
            hash_origem = calcular_md5(arquivo)
            hash_destino = calcular_md5(arquivo_destino)

            if hash_origem == hash_destino:
                logging.warning(f"DUPLICATA: {arquivo.name} já existe no destino. Ignorado.")
                return 'duplicado'
            else:
                arquivo_destino = resolver_duplicidade_nome(arquivo_destino)
                logging.info(f"RENOMEADO: {arquivo.name} -> {arquivo_destino.name}")

        if simulacao:
            logging.info(f"[SIMULAÇÃO] Moveria: {arquivo} -> {arquivo_destino}")
            return 'sucesso'
        else:
            pasta_final.mkdir(parents=True, exist_ok=True)
            shutil.move(str(arquivo), str(arquivo_destino))
            logging.info(f"MOVIDO: {arquivo.name} -> {arquivo_destino}")
            return 'sucesso'

    except Exception as e:
        logging.error(f"FALHA em {arquivo}: {e}")
        return 'erro'