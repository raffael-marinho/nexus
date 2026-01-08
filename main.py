import sys
from pathlib import Path
from src.core import OrganizadorArquivos

def limpar_caminho(caminho_str):
    if not caminho_str:
        return None
    
    limpo = caminho_str.strip().strip('"').strip("'")
    
    path_obj = Path(limpo).expanduser().resolve()
    return path_obj

def main():
    print("\n" + "="*50)
    print("   ORGANIZADOR DE ARQUIVOS MULTIPLATAFORMA v3.0")
    print("="*50)
    print("Este programa organiza arquivos soltos na raiz da pasta escolhida.")
    print("-" * 50)
    
    while True:
        origem_input = input(">> Digite o caminho da pasta de ORIGEM: ")
        origem = limpar_caminho(origem_input)

        if origem and origem.exists() and origem.is_dir():
            break
        else:
            print(f"[ERRO] A pasta não existe ou é inválida: {origem}")
            print("Tente novamente.\n")

    while True:
        destino_input = input(">> Digite o caminho da pasta de DESTINO: ")
        destino = limpar_caminho(destino_input)
        
        if not destino_input:
            destino = origem / "Arquivos_Organizados"
            print(f"   (Destino não informado. Usando padrão: {destino})")

        if not destino.exists():
            criar = input(f"   A pasta de destino não existe. Criar? (S/N): ").upper()
            if criar == 'S':
                try:
                    destino.mkdir(parents=True, exist_ok=True)
                    break
                except Exception as e:
                    print(f"[ERRO] Não foi possível criar a pasta: {e}")
            else:
                print("Por favor, escolha outro destino.")
        else:
            break

    print("-" * 50)
    simulacao_input = input(">> Apenas SIMULAR o que aconteceria? (S/N) [Padrão: S]: ").strip().upper()
    eh_simulacao = simulacao_input != 'N' 

    if eh_simulacao:
        print("\n[MODO SIMULAÇÃO ATIVADO] Nenhum arquivo será movido de verdade.")
    else:
        print("\n[MODO REAL] Arquivos SERÃO movidos.")

    try:
        organizador = OrganizadorArquivos(origem, destino, eh_simulacao)
        organizador.executar()
        
    except KeyboardInterrupt:
        print("\n\n[!] Operação interrompida pelo usuário (Ctrl+C).")
    except Exception as e:
        print(f"\n[CRÍTICO] Ocorreu um erro não tratado: {e}")
    finally:
        print("\nPrograma finalizado.")

if __name__ == "__main__":
    main()