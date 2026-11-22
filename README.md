# 🐧 Linux AI Assistant

[![Status](https://img.shields.io/badge/status-planejamento%20%2F%20MVP-orange)](ROADMAP.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/AI-Ollama%20Local-black.svg)](https://ollama.com/)

> **Um assistente de IA local, didático e seguro que ensina você a dominar o Linux enquanto resolve seus problemas.**

---

## 🎯 Proposta

A maioria dos iniciantes ou pessoas que migram do Windows para o Linux se deparam com o medo do terminal e a frustração com erros crípticos.

O **Linux AI Assistant** nasceu para mudar isso. Ele não é uma caixa-preta que altera seu sistema às cegas; ele é um **parceiro didático** que:
1. **Compreende seu sistema:** Lê informações reais do seu ambiente (distro, versão, kernel) para não sugerir comandos genéricos incompatíveis.
2. **Explica o que faz:** Ensina o significado de cada comando, flag e permissão antes de qualquer ação.
3. **Execução 100% Local:** Todo o processamento de inteligência artificial roda na sua máquina através do [Ollama](https://ollama.com/), sem telemetria e sem enviar seus dados para a nuvem.
4. **Segurança em primeiro lugar:** A IA nunca executa comandos sem autorização. Possui um validador com uma lista de comandos permitidos totalmente editável por você.

---

## 🚀 Começando

### Pré-requisitos
* Sistema operacional Linux baseado em Debian (Ubuntu, Debian, Linux Mint, Pop!_OS, Zorin OS, etc.).
* Python 3.10 ou superior.
* [Ollama](https://ollama.com/) instalado e rodando.

### Modelo Recomendado
Para hardware com cerca de 8GB de VRAM ou mais (ou computadores com 16GB de RAM):
```bash
ollama run qwen2.5:7b
```
*(Para máquinas com restrição de memória, o modelo `qwen2.5:3b` também é suportado e extremamente ágil).*

---

## 📚 Documentação do Projeto

* 📋 [Visão Geral e Objetivos (PROJECT.md)](PROJECT.md)
* 🏗️ [Arquitetura Técnica (ARCHITECTURE.md)](ARCHITECTURE.md)
* 🗺️ [Roteiro de Desenvolvimento (ROADMAP.md)](ROADMAP.md)
* ⚖️ [Registro de Decisões Técnicas (DECISIONS.md)](DECISIONS.md)
* 📝 [Registro de Sessões (SESSION_LOG.md)](SESSION_LOG.md)

---

## 🤝 Como Contribuir

Contribuições são muito bem-vindas! Consulte o guia [CONTRIBUTING.md](CONTRIBUTING.md) para saber como colaborar com ideias, código e documentação.

---

## 📄 Licença

Este projeto é distribuído sob a licença [MIT](LICENSE).
# linux-ai-assistant
# linux-ai-assistant
