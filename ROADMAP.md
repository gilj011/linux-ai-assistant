# Roadmap — Linux AI Assistant

Este documento acompanha as fases de planejamento, desenvolvimento e lançamento do projeto.

---

## Fase 1 — MVP (Concluida)
**Objetivo:** Construir um assistente CLI interativo, rápido e didático para dúvidas e comandos Linux, integrado ao Ollama local.

- [x] Alinhamento inicial de objetivos e princípios (`start.md`).
- [x] Definição da arquitetura e modelo de referência (`Qwen 2.5 7B`).
- [x] Estruturação da documentação e repositório Git.
- [x] Implementar módulo de inspeção de ambiente (`os_inspector`) lendo `/etc/os-release` e `uname`.
- [x] Implementar cliente Ollama com streaming e tratamento de conexão offline.
- [x] Criar CLI com `rich` para exibição formatada (explicações didáticas + blocos de código Bash destacados).
- [x] Implementar sistema de configuração inicial (`config.yaml`) e lista inicial de comandos permitidos (`allowed_commands.yaml`).
- [x] Validação prática do assistente em terminal real.

---

## Fase 2 — Diagnósticos e Análise de Logs (Concluida)
**Objetivo:** Capacitar o assistente a diagnosticar problemas reais a partir de logs e estado de serviços.

- [x] Coleta segura de estado de serviços (`systemctl status` e `--failed`).
- [x] Análise de logs do sistema via `journalctl -p 3 -xb`.
- [x] Diagnóstico de conectividade de rede (`ip -br a`).
- [x] Formatação de diagnósticos em evidências com motor analítico (`DiagnosticEngine`).
- [x] Modo `--diag` e `--service` integrado ao CLI e sessão interativa (`diag`).

---

## Fase 3 — Executor Controlado e Resolução Assistida (Concluida)
**Objetivo:** Permitir a execução segura de comandos sugeridos sob estrita supervisão do usuário.

- [x] Motor validador de comandos contra a whitelist configurável pelo usuário (`ControlledExecutor`).
- [x] Sanitização e bloqueio de injeção de comandos / pipes perigosos (`blocked_patterns`).
- [x] Chave seletora operacional (Modo Seguro vs Modo Assistido).
- [x] Parser de acoes estruturadas (`write_file` e `run_command`).
- [x] Caixa de autorização humana explícita no CLI com confirmação obrigatória [s/N].
- [x] Criação segura de arquivos de instrução e scripts no disco sob autorização.

---

## Fase 4 — Auditoria e Persistencia de Relatorios (Concluida)
**Objetivo:** Rastreabilidade estrita de operacoes e historico de manutencoes.

- [x] Modulo de auditoria local (`AuditLogger` gravando em `~/.local/share/kored/audit.log`).
- [x] Persistencia automatica de relatorios de diagnostico (`~/.local/share/kored/reports/`).
- [x] Comando `historico` / `audit` interativo e flag CLI `--audit`.
- [x] Registro detalhado de aprovacoes, recusas e resultados de execucao.

---

## Fase 5 — Empacotamento e Distribuicao (Concluida)
**Objetivo:** Permitir utilizacao universal no terminal e empacotamento nativo Debian.

- [x] Script de instalacao direta no sistema (`scripts/install.sh` / `make install`).
- [x] Script de desinstalacao limpa (`scripts/uninstall.sh` / `make uninstall`).
- [x] Autocompletar nativo para Bash (`scripts/kored_completion.bash`).
- [x] Construcao automatizada de pacote `.deb` (`scripts/build_deb.sh` / `make deb`).
- [x] Makefile com comandos de ciclo de vida (`test`, `install`, `deb`, `clean`).
- [ ] Avaliacao futura de interface grafica desktop (GTK4/Libadwaita ou Tauri).
- [ ] Documentação de instalação pública e lançamento v1.0.
