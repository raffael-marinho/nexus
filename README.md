# 📂 Organizador de Arquivos Automático

> Um script Python robusto e modular para organizar arquivos automaticamente baseando-se em extensões e metadados de data.

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Status](https://img.shields.io/badge/status-active-green)

## 📖 Sobre o Projeto

Este projeto é uma ferramenta de automação (scripting) desenvolvida para acabar com a bagunça digital. Ele atua no modo "Faxineira" (sob demanda), escaneando uma pasta de origem (e suas subpastas), identificando arquivos e movendo-os para uma estrutura de diretórios organizada por **Categoria**, **Ano** e **Mês**.

### ✨ Principais Funcionalidades

* **🔍 Escaneamento Recursivo:** Busca arquivos na pasta raiz e em todas as subpastas.
* **📅 Organização Cronológica Inteligente:**
    * Lê metadados **EXIF** de fotos para encontrar a data original de captura.
    * Usa a data de modificação do sistema para outros arquivos.
    * Cria pastas com nomes de meses em Português (Ex: `2025\Janeiro`).
* **🛡️ Sistema Anti-Duplicidade (MD5):**
    * Calcula o Hash MD5 dos arquivos.
    * Se o conteúdo for idêntico, o arquivo não é movido (evita duplicatas).
    * Se o nome for igual mas o conteúdo diferente, renomeia automaticamente (`arquivo_copy_1.jpg`).
* **🧪 Modo Simulação (Dry Run):** Permite ver o que será feito antes de mover qualquer arquivo.
* **📝 Logs Detalhados:** Gera um relatório completo das operações (`log_organizacao.txt`).

## 🛠️ Estrutura do Projeto

O código foi refatorado para seguir boas práticas de Engenharia de Software (Clean Code):

```text
OrganizadorArquivos/
│
├── src/                 # Código fonte modular
│   ├── __init__.py
│   ├── config.py        # Configurações (Extensões, Pastas)
│   ├── utils.py         # Funções auxiliares (Hash, EXIF, Log)
│   └── core.py          # Lógica principal (Scan e Move)
│
├── main.py              # Ponto de entrada da aplicação
├── requirements.txt     # Dependências do projeto
└── README.md            # Documentação