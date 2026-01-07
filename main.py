from pathlib import Path
from src.core import OrganizadorArquivos

def main():
    print("=== Organizador de Arquivos OO v3.0 ===")
    print("Modo: Orientação a Objetos (POO)")
    print("-" * 40)
    
    origem_str = input("Pasta de ORIGEM (vai escanear subpastas): ").strip().strip('"')
    destino_str = input("Pasta de DESTINO: ").strip().strip('"')
    
    origem = Path(origem_str)
    destino = Path(destino_str)

    if not origem.exists():
        print(f"[ERRO] A pasta de origem não existe: {origem}")
        return

    simulacao_input = input("Apenas simular (Dry Run)? (S/N): ").strip().upper()
    eh_simulacao = simulacao_input == 'S'

    organizador = OrganizadorArquivos(origem, destino, eh_simulacao)
    
    try:
        organizador.executar()
    except KeyboardInterrupt:
        print("\n\n[!] Operação interrompida pelo usuário.")
    except Exception as e:
        print(f"\n[!] Ocorreu um erro fatal no programa principal: {e}")

if __name__ == "__main__":
    main()