# kored — Linux Systems Intelligence

[![Status](https://img.shields.io/badge/status-v0.3.0%20MVP-green)](docs/ROADMAP.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/AI-Ollama%20Local-black.svg)](https://ollama.com/)

> Copiloto local de engenharia de sistemas, troubleshooting e assistencia tecnica para Linux.

---

## O que e o kored

O **kored** (*Kore* + *daemon*) e um assistente de inteligencia de sistemas Linux executado **100% localmente**.

Desenhado para ser uma ferramenta de cabeceira tanto para quem esta aprendendo a dominar o terminal quanto para engenheiros de software, SREs e sysadmins experientes que buscam produtividade, debugging avancado e entendimento profundo dos internals do sistema operacional.

**Diferenciais:**

- **Sem condescendencia.** Respostas tecnicas de padrao de producao. Clareza para iniciantes, profundidade para experientes.
- **Contexto real do host.** Le automaticamente o ambiente (`/etc/os-release`, kernel, gerenciadores de pacote) para respostas cirurgicas.
- **Multi-turn.** Dialogo continuo de troubleshooting sem perder o fio da conversa.
- **100% local e privado.** Inferencia via [Ollama](https://ollama.com/) com `Qwen 2.5 7B`. Seus dados nunca saem da maquina.
- **Humano no loop.** Executor controlado: a IA nunca roda comandos sozinha. Toda acao exige `[s/N]` explicito.

---

## Pre-requisitos

- Linux baseado em Debian (Pop!_OS, Ubuntu, Debian, Mint, Zorin, Elementary).
- Python 3.10 ou superior.
- [Ollama](https://ollama.com/) instalado e rodando com o modelo recomendado:
  ```bash
  ollama pull qwen2.5:7b
  ```

---

## Uso rapido

```bash
# Modo interativo (Modo Seguro — somente consultas e diagnosticos)
./kored

# Modo Assistido (propoe acoes com aprovacao obrigatoria do usuario)
./kored --assisted
# ou: ./kored -a

# Retomar a ultima sessao de conversa
./kored --continue
# ou: ./kored -c

# Listar historico de sessoes anteriores gravadas
./kored --sessions

# Retomar uma sessao especifica pelo ID
./kored --session <ID_DA_SESSAO>

# Visualizar parametros de configuracao ativos (~/.config/kored/config.yaml)
./kored --config

# Diagnosticar o ultimo comando que falhou no terminal (le o historico do Bash/Zsh)
./kored fix

# Diagnosticar um comando especifico que falhou
./kored fix "docker compose up -d"

# Diagnosticar passando a saida de erro diretamente via pipe
docker compose up 2>&1 | ./kored fix

# Consulta direta
./kored "como debugar conexoes TCP em estado TIME_WAIT com ss"

# Varredura de saude do sistema
./kored --diag

# Diagnostico de um servico especifico
./kored --service docker

# Historico de auditoria de acoes
./kored --audit
```

**Comandos dentro da sessao interativa:**

| Comando | Acao |
|---------|------|
| `sessoes` | Lista o historico de sessoes gravadas |
| `retomar <id>` | Retoma o contexto de uma sessao anterior |
| `nova` | Inicia uma nova sessao zerada sem sair do CLI |
| `diag` | Executa varredura de saude do sistema |
| `diag <servico>` | Diagnostica servico systemd especifico (ex: diag docker) |
| `fix` | Analisa o ultimo comando que falhou no terminal do usuario |
| `fix <comando>` | Analisa a falha de um comando especifico |
| `historico` | Exibe o log de auditoria de acoes |
| `config` | Exibe os parametros de configuracao ativos |
| `modo` | Alterna entre Modo Seguro e Modo Assistido |
| `limpar` | Limpa a tela e reinicia o contexto da conversa |
| `info` | Exibe detalhes do ambiente, distro, kernel e sessao |
| `sair` | Encerra a sessao |

---

## Instalacao

### Via Makefile (recomendado)

```bash
# Instalacao para o usuario atual (~/.local/bin/kored)
make install

# Instalacao global (requer sudo)
sudo make install

# Remover instalacao
make uninstall
```

### Via pacote .deb

```bash
# Gerar o pacote
make deb
# Arquivo gerado em: dist/kored_0.3.0_all.deb

# Instalar
sudo dpkg -i dist/kored_0.3.0_all.deb
```

---

## Modos Operacionais

| Modo | Ativacao | Comportamento |
|------|----------|---------------|
| **Seguro** | padrao (`./kored`) | Somente consultas, analises e diagnosticos. Zero acoes no sistema. |
| **Assistido** | `./kored -a` | A IA pode propor criacao de arquivos e execucao de comandos. Cada acao exige aprovacao `[s/N]`. |

---

## Estrutura do projeto

```text
kored/
├── main.py                     # Ponto de entrada
├── kored                       # Executavel direto
├── Makefile                    # test, install, deb, clean
├── requirements.txt
├── config/
│   └── allowed_commands.yaml   # Whitelist editavel de comandos permitidos
├── src/
│   ├── cli.py
│   ├── ollama_client.py
│   ├── os_inspector.py
│   ├── prompt_builder.py
│   ├── probes.py
│   ├── diagnostics.py
│   ├── executor.py
│   ├── action_parser.py
│   └── audit.py
├── tests/                      # 27 testes — make test
├── scripts/                    # install.sh, uninstall.sh, build_deb.sh, kored_completion.bash
└── docs/                       # Documentacao tecnica
    ├── PROJECT.md
    ├── ARCHITECTURE.md
    ├── ROADMAP.md
    ├── DECISIONS.md
    ├── CONTRIBUTING.md
    └── SESSION_LOG.md
```

---

## Documentacao

- [Visao Geral e Principios](docs/PROJECT.md)
- [Arquitetura Tecnica](docs/ARCHITECTURE.md)
- [Roteiro de Desenvolvimento](docs/ROADMAP.md)
- [Registro de Decisoes Tecnicas](docs/DECISIONS.md)
- [Guia de Contribuicao](docs/CONTRIBUTING.md)
- [Historico de Sessoes](docs/SESSION_LOG.md)

---

## Licenca

Distribuido sob a licenca [MIT](LICENSE).
