# kored — Linux Systems Intelligence

[![Status](https://img.shields.io/badge/status-MVP%20ativo-orange)](ROADMAP.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/AI-Ollama%20Local-black.svg)](https://ollama.com/)

> **Copiloto local de engenharia de sistemas, troubleshooting e assistencia tecnica para Linux.**

---

## Sobre o kored

O **kored** (*Kore* + *daemon*) e um assistente de inteligencia de sistemas Linux executado **100% localmente**. 

Ele foi desenhado para ser uma ferramenta de cabeceira tanto para quem esta aprendendo a dominar o terminal quanto para engenheiros de software, SREs e sysadmins experientes que buscam produtividade, debugging avancado e entendimento profundo dos *internals* do sistema operacional.

### Diferenciais:
1. **Engenharia de Sistemas:** Sem respostas condescendentes. Praticas modernas de producao, foco em performance e seguranca.
2. **Contexto Real do Host:** Le automaticamente o ambiente (`/etc/os-release`, kernel, package managers) para respostas cirurgicas e sob medida.
3. **Memoria de Conversa Multi-Turn:** Permite dialogos continuos de troubleshooting sem perder o historico do problema.
4. **100% Local & Privado:** Inferencia via [Ollama](https://ollama.com/) com modelos de alta performance tecnica (`Qwen 2.5 7B`). Seus comandos e dados nunca saem da maquina.
5. **Seguranca por Design:** Validacao estrita e lista editavel de comandos permitidos antes de qualquer execucao.

---

## Utilizacao Rapida

### Pre-requisitos
* Sistema Linux baseado em Debian (Pop!_OS, Ubuntu, Debian, Mint, etc.).
* Python 3.10 ou superior.
* [Ollama](https://ollama.com/) instalado com o modelo recomendado:
  ```bash
  ollama run qwen2.5:7b
  ```

### Execucao

```bash
# Modo Interativo Continuo (Modo Seguro - Somente Leitura)
./kored

# Modo Assistido (permite propor criacao de arquivos e comandos sob aprovacao humana)
./kored --assisted
# ou: ./kored -a

# Consulta Rapida Direta
./kored "como debugar conexoes TCP em estado TIME_WAIT com ss"

# Varredura Diagnostica de Saude do Sistema
./kored --diag

# Diagnostico de Servico Especifico
./kored --service docker

# Historico de Auditoria de Acoes
./kored --audit
```

---

## Instalacao no Sistema e Empacotamento

### Instalacao Rapida via Makefile
Para poder chamar `kored` de qualquer pasta do terminal:

```bash
# Instalacao para o usuario atual (~/.local/bin/kored):
make install

# Ou instalacao global no sistema (requer sudo):
sudo make install
```

### Geracao de Pacote Debian (.deb)
Para gerar o pacote de instalacao `.deb` nativo para Pop!_OS, Ubuntu ou Debian:

```bash
make deb
# O pacote sera gerado em dist/kored_0.3.0_all.deb

# Para instalar o pacote:
sudo dpkg -i dist/kored_0.3.0_all.deb
```

---

## Documentacao do Projeto

* [Visao Geral e Principios (PROJECT.md)](PROJECT.md)
* [Arquitetura Tecnica (ARCHITECTURE.md)](ARCHITECTURE.md)
* [Roteiro de Desenvolvimento (ROADMAP.md)](ROADMAP.md)
* [Registro de Decisoes Tecnicas (DECISIONS.md)](DECISIONS.md)
* [Historico de Sessoes (SESSION_LOG.md)](SESSION_LOG.md)

---

## Licenca

Distribuido sob a licenca [MIT](LICENSE).
