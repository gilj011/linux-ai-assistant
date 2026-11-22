# Histórico de Sessões — Linux AI Assistant

---

## Sessão: 2026-11-22

### Participantes
* Usuário (`gcampos`)
* Assistente de Desenvolvimento (`Antigravity`)

### Objetivos da Sessão
* Análise detalhada do documento inicial (`start.md`).
* Discussão e alinhamento sobre hardware alvo, modelos de IA, segurança e escopo do MVP.
* Estruturação formal dos documentos do projeto e preparação do repositório Git.

### Resumo das Discussões e Decisões
1. **Hardware Alvo:** Foco em viabilizar o uso em máquinas com GPU de 8GB de VRAM (referência: AMD Radeon RX 580) ou CPUs com 16GB de RAM.
2. **Escolha do Modelo:** Selecionado `qwen2.5:7b` como modelo principal e `qwen2.5:3b` como alternativa ultraleve para inferência local via Ollama.
3. **Segurança e Executor Controlado:** Alinhada a necessidade de uma lista de comandos permitidos (whitelist) auditável e diretamente editável pelo usuário.
4. **Escopo do MVP (Fase 1):** Definido um assistente em linha de comando (CLI) em Python que responde dúvidas de comandos com rapidez, fluidez (streaming) e didática, contextualizado pela distribuição Linux do usuário.
5. **Evolução de Identidade e Postura:**
   - Transição do conceito infantilizado ("Professor Linux") para **kored** — copiloto de engenharia de sistemas Linux.
   - Nome oficial adotado: **kored** (*Kore* + *daemon*), executável diretamente via `./kored`.
   - Adicionado indicador visual de carregamento (spinner animado) enquanto o modelo processa.
   - Implementado suporte a histórico de conversa multi-turn (`/api/chat`), permitindo perguntas e respostas sequenciais contextualizadas.
   - Registrado ADR 005 em `DECISIONS.md`.

### Próximos Passos
* Conectar o repositório ao GitHub.
* Implementar o leitor de ambiente do sistema (`os_inspector`) e cliente Ollama no MVP em Python.
