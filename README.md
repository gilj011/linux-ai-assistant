# ⚡ kored — Linux Systems Intelligence

[![Status](https://img.shields.io/badge/status-MVP%20ativo-orange)](ROADMAP.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/AI-Ollama%20Local-black.svg)](https://ollama.com/)

> **Copiloto local de engenharia de sistemas, troubleshooting e assistência técnica para Linux.**

---

## 🎯 Sobre o kored

O **kored** (*Kore* + *daemon*) é um assistente de inteligência de sistemas Linux executado **100% localmente**. 

Ele foi desenhado para ser uma ferramenta de cabeceira tanto para quem está aprendendo a dominar o terminal quanto para engenheiros de software, SREs e sysadmins experientes que buscam produtividade, debugging avançado e entendimento profundo dos *internals* do sistema operacional.

### Diferenciais:
1. **Engenharia de Sistemas Séria:** Sem respostas condescendentes. Práticas modernas de produção, foco em performance e segurança.
2. **Contexto Real do Host:** Lê automaticamente o ambiente (`/etc/os-release`, kernel, package managers) para respostas cirúrgicas e sob medida.
3. **Memória de Conversa Multi-Turn:** Permite diálogos contínuos de troubleshooting sem perder o histórico do problema.
4. **100% Local & Privado:** Inferência via [Ollama](https://ollama.com/) com modelos de alta performance técnica (`Qwen 2.5 7B`). Seus comandos e dados nunca saem da máquina.
5. **Segurança por Design:** Validação estrita e lista editável de comandos permitidos antes de qualquer execução.

---

## 🚀 Utilização Rápida

### Pré-requisitos
* Sistema Linux baseado em Debian (Pop!_OS, Ubuntu, Debian, Mint, etc.).
* Python 3.10 ou superior.
* [Ollama](https://ollama.com/) instalado com o modelo recomendado:
  ```bash
  ollama run qwen2.5:7b
  ```

### Execução

```bash
# Modo Interativo Contínuo (com histórico de contexto)
./kored

# Consulta Rápida Direta
./kored "como debugar conexões TCP em estado TIME_WAIT com ss"

# Modo de Análise e Dissecação Profunda de Comando
./kored --explain "find /var/log -type f -name '*.gz' -mtime +30 -delete"
```

---

## 📚 Documentação do Projeto

* 📋 [Visão Geral e Princípios (PROJECT.md)](PROJECT.md)
* 🏗️ [Arquitetura Técnica (ARCHITECTURE.md)](ARCHITECTURE.md)
* 🗺️ [Roteiro de Desenvolvimento (ROADMAP.md)](ROADMAP.md)
* ⚖️ [Registro de Decisões Técnicas (DECISIONS.md)](DECISIONS.md)
* 📝 [Histórico de Sessões (SESSION_LOG.md)](SESSION_LOG.md)

---

## 📄 Licença

Distribuído sob a licença [MIT](LICENSE).
