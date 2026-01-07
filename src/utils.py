import hashlib
import logging
import os
from pathlib import Path
from datetime import datetime
from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS

class LogManager:
    @staticmethod
    def configurar(pasta_origem):
        log_file = Path(pasta_origem) / 'log_organizacao.txt'
        logging.getLogger().handlers = []
        
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            encoding='utf-8'
        )
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)
        return log_file
    
class FileAnalyzer:
    @staticmethod
    def calcular_md5(caminho_arquivo):
        hash_md5 = hashlib.md5()
        try:
            with open(caminho_arquivo, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logging.error(f"Erro ao calcular MD5 de {caminho_arquivo}: {e}")
            return None

    @staticmethod
    def obter_data_criacao(caminho_arquivo):
        data_encontrada = None
        suffix = caminho_arquivo.suffix.lower()

        if suffix in ['.jpg', '.jpeg', '.png', '.heic', '.raw', '.webp']:
            try:
                with Image.open(caminho_arquivo) as img:
                    exif_data = img._getexif()
                    if exif_data:
                        for tag, value in exif_data.items():
                            tag_name = TAGS.get(tag, tag)
                            if tag_name == 'DateTimeOriginal':
                                data_encontrada = datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                                break
            except (UnidentifiedImageError, ValueError, TypeError, AttributeError):
                pass

        if not data_encontrada:
            timestamp = os.path.getmtime(caminho_arquivo)
            data_encontrada = datetime.fromtimestamp(timestamp)

        return data_encontrada