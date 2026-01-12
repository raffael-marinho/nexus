import sys
from pathlib import Path
from src.core import OrganizadorArquivos
from src.monitor import MonitorPasta

def limpar_caminho(caminho_str):
    if not caminho_str:
        return None 
    limpo = caminho_str.strip().strip('"').strip("'")
    path_obj = Path(limpo).expanduser().resolve()
    return path_obj

def main():
    print("\n" + "="*50)
    print("   ORGANIZADOR DE ARQUIVOS MULTIPLATAFORMA v4.0")
    print("="*50)
    print("Este programa organiza arquivos soltos na raiz da pasta escolhida.")
    print("-" * 50)
    
    while True:
        origem_input = input(">> Digite o caminho da pasta de ORIGEM(Monitorada): ")
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

    print("\n" + "-" * 50)
    print("O que você deseja fazer?")
    print("1. Organizar tudo AGORA (Execução Única)")
    print("2. Ficar MONITORANDO em Tempo Real (Automático)")
    print("-" * 50)
    
    escolha = input(">> Escolha uma opção (1 ou 2): ").strip()

    try:
        if escolha == '1':
            simulacao_input = input(">> Apenas SIMULAR? (S/N) [Padrão: S]: ").strip().upper()
            eh_simulacao = simulacao_input != 'N'

            if eh_simulacao:
                print("\n[MODO SIMULAÇÃO] Nada será movido.")
            else:
                print("\n[MODO REAL] Arquivos SERÃO movidos.")

            organizador = OrganizadorArquivos(origem, destino, eh_simulacao)
            organizador.executar()

        elif escolha == '2':
            print("\n[!] INICIANDO VIGILÂNCIA...")
            print(f"[!] Todos os novos arquivos em '{origem.name}' serão movidos para '{destino.name}'.")
            print("[!] Pressione Ctrl+C para encerrar.")
            
            organizador = OrganizadorArquivos(origem, destino, simulacao=False)
            
            monitor = MonitorPasta(organizador)
            monitor.iniciar() 

        else:
            print("\n[!] Opção inválida. Reinicie o programa.")

    except KeyboardInterrupt:
        print("\n\n[!] Operação interrompida pelo usuário (Ctrl+C).")
    except Exception as e:
        print(f"\n[CRÍTICO] Ocorreu um erro não tratado: {e}")
    finally:
        print("\nPrograma finalizado.")

if __name__ == "__main__":
    main()