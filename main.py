from pathlib import Path
from src.utils import configurar_logger
from src.core import escanear_arquivos, processar_movimentacao

def main():
    print("=== Organizador de Arquivos v2.0 (Modular + Recursivo) ===")
    
    origem_str = input("Pasta de ORIGEM (vai escanear subpastas): ").strip().strip('"')
    destino_str = input("Pasta de DESTINO: ").strip().strip('"')
    
    origem = Path(origem_str)
    destino = Path(destino_str)

    if not origem.exists():
        print("Erro: Pasta de origem não existe.")
        return

    simulacao = input("Apenas simular? (S/N): ").strip().upper() == 'S'

    log_path = configurar_logger(origem)
    
    print("\nEscaneando arquivos e subpastas...")
    arquivos = escanear_arquivos(origem)
    total = len(arquivos)
    print(f"Encontrados {total} arquivos.")

    stats = {'sucesso': 0, 'duplicado': 0, 'erro': 0}

    for arquivo in arquivos:
        resultado = processar_movimentacao(arquivo, destino, simulacao)
        stats[resultado] += 1

    print("\n" + "="*30)
    print("Relatório Final")
    print(f"Sucesso/Movidos: {stats['sucesso']}")
    print(f"Duplicatas (Ignoradas): {stats['duplicado']}")
    print(f"Erros: {stats['erro']}")
    print(f"Log: {log_path}")
    print("="*30)

if __name__ == "__main__":
    main()