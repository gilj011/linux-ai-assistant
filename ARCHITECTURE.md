# Arquitetura Técnica — Linux AI Assistant

Este documento descreve a arquitetura inicial do Linux AI Assistant, detalhando a separação de responsabilidades, componentes e fluxo de dados.

---

## 1. Visão Arquitetural

A arquitetura foi projetada com base em modularidade, segurança e desacoplamento entre a camada de inteligência e a camada do sistema operacional.

```text
┌─────────────────────────────────────────────────────────────┐
│                       Camada de UI                          │
│   • CLI Interativo (Fase 1 - Python / Rich)                 │
│   • GUI Desktop (Futuro - Avaliando GTK4 ou Tauri)          │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Núcleo da Aplicação                      │
│                                                             │
│  ┌───────────────────────┐       ┌───────────────────────┐  │
│  │   System Inspector    │       │     LLM Provider      │  │
│  │ (Coleta read-only)    │       │ (Ollama - Qwen 2.5)   │  │
│  └───────────┬───────────┘       └───────────┬───────────┘  │
│              │                               │              │
│              └───────────────┬───────────────┘              │
│                              ▼                              │
│                 Context Builder & Prompt Engine             │
│                              │                              │
│                              ▼                              │
│                 Controlled Command Executor                 │
│                 ┌─────────────────────────┐                 │
│                 │ • Validador de Sintaxe  │                 │
│                 │ • Whitelist Editável    │                 │
│                 │ • Confirmação do Usuário│                 │
│                 │ • Auditoria / Logs      │                 │
│                 └─────────────────────────┘                 │
└──────────────────────────────┬──────────────────────────────┘
                               │ (Apenas comandos validados
                               ▼  e explicitamente autorizados)
┌─────────────────────────────────────────────────────────────┐
│                      Sistema Operacional                    │
│                 (Distribuições Debian-based)                │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Componentes Principais

### 2.1. System Inspector (Inspetor de Sistema)
* **Objetivo:** Coletar com segurança metadados essenciais do sistema para alimentar o contexto do modelo.
* **Características:**
  * Execução estritamente **read-only** (não altera estado, não requer privilégios de superusuário).
  * Informações coletadas:
    * Distribuição e versão: `/etc/os-release`
    * Kernel e arquitetura: `uname -srm`
    * Gerenciador de pacotes ativo: detecção de `apt`, `dpkg`, `flatpak`, `snap`
    * Recursos básicos: memória livre (`free -m`), discos (`lsblk`)

### 2.2. LLM Provider (Integração Local via Ollama)
* **Objetivo:** Orquestrar a comunicação com o motor de inferência local.
* **Modelo Referência:** `qwen2.5:7b` (com fallback para `qwen2.5:3b` para requisitos de baixo consumo de memória).
* **Comunicação:** API HTTP do Ollama (`http://localhost:11434/api/generate` ou cliente oficial em Python).
* **Formato de Saída:** Suporte a streaming de tokens para resposta imediata e interativa no terminal.

### 2.3. Controlled Command Executor (Executor Controlado)
* **Objetivo:** Garantir que nenhum comando destrutivo ou não autorizado seja executado.
* **Pilares de Segurança:**
  1. **Lista de Comandos Permitidos (Whitelist):** Arquivo de configuração auditável pelo usuário (`config/allowed_commands.yaml` ou `~/.config/linux-assistant/allowed_commands.yaml`).
  2. **Validador de Parâmetros:** Bloqueio ativo de pipes perigosos (`| bash`, `| sh`), redirecionamentos cegos e argumentos de destruição (`rm -rf /`, `mkfs`).
  3. **Autorização Explícita:** O comando a ser executado é impresso com destaque, com aviso claro do que faz, solicitando confirmação `[s/N]`.
  4. **Log de Auditoria:** Registro local com data/hora e comandos executados para rastreabilidade.

### 2.4. Interface do Usuário (CLI para o MVP)
* Construída em **Python 3** utilizando a biblioteca **Rich**:
  * Formatação de blocos de código com destaque de sintaxe Bash.
  * Painéis e alertas coloridos para níveis de risco (Informativo, Atenção, Crítico).
  * Streaming fluido no terminal.

---

## 3. Segurança e Permissões

| Nível de Ação | Exemplo de Comandos | Permissão | Fluxo |
|---|---|---|---|
| **Leitura / Diagnóstico** | `uname`, `lsblk`, `free`, `systemctl status` | Usuário comum | Coleta automatizada ou manual para diagnóstico |
| **Ação do Usuário** | `ls`, `cd`, `tar -xvf`, `git status` | Usuário comum | Sugerido pela IA, exige confirmação para rodar |
| **Ação Administrativa** | `apt install`, `systemctl restart` | Requer `sudo` | Sugerido pela IA, requer validação na whitelist + confirmação e autenticação pelo usuário |
| **Comandos Proibidos** | `rm -rf /`, `dd of=/dev/sdX`, `curl ... \| bash` | Proibido | Bloqueado sumariamente pelo validador |
