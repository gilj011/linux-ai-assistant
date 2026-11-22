# Roadmap — Linux AI Assistant

Este documento acompanha as fases de planejamento, desenvolvimento e lançamento do projeto.

---

## Fase 1 — MVP (Foco Atual)
**Objetivo:** Construir um assistente CLI interativo, rápido e didático para dúvidas e comandos Linux, integrado ao Ollama local.

- [x] Alinhamento inicial de objetivos e princípios (`start.md`).
- [x] Definição da arquitetura e modelo de referência (`Qwen 2.5 7B`).
- [x] Estruturação da documentação e repositório Git.
- [ ] Implementar módulo de inspeção de ambiente (`os_inspector`) lendo `/etc/os-release` e `uname`.
- [ ] Implementar cliente Ollama com streaming e tratamento de conexão offline.
- [ ] Criar CLI com `rich` para exibição formatada (explicações didáticas + blocos de código Bash destacados).
- [ ] Implementar sistema de configuração inicial (`config.yaml`) e lista inicial de comandos permitidos (`allowed_commands.yaml`).
- [ ] Validação prática do assistente em terminal real.

---

## Fase 2 — Diagnósticos e Análise de Logs
**Objetivo:** Capacitar o assistente a diagnosticar problemas reais a partir de logs e estado de serviços.

- [ ] Coleta segura de estado de serviços (`systemctl status`).
- [ ] Análise de logs do sistema via `journalctl -p 3 -xb`.
- [ ] Diagnóstico de conectividade de rede (`ip`, `ping`, `nmcli`).
- [ ] Formatação de diagnósticos em evidências: Causa Provável, Gravidade e Solução Sugerida.

---

## Fase 3 — Executor Controlado e Resolução Assistida
**Objetivo:** Permitir a execução segura de comandos sugeridos sob estrita supervisão do usuário.

- [ ] Motor validador de comandos contra a whitelist configurável pelo usuário.
- [ ] Sanitização e bloqueio de injeção de comandos / pipes perigosos.
- [ ] Interface de confirmação interativa com explicação prévia de efeitos colaterais.
- [ ] Histórico e log local de auditoria de operações executadas.

---

## Fase 4 — Modo Professor Linux
**Objetivo:** Fortalecer a capacitação e aprendizado contínuo do usuário.

- [ ] Modo `--explain <comando>` para dissecção detalhada de sintaxe e flags.
- [ ] Exercícios práticos e tutoriais passo a passo de conceitos fundamentais (permissões `chmod`/`chown`, links simbólicos, redirecionamentos).
- [ ] Glossário interativo de termos do ecossistema Linux.

---

## Fase 5 — Interface Gráfica e Distribuição
**Objetivo:** Levar o assistente para além do terminal e facilitar a instalação em massa.

- [ ] Avaliação e desenvolvimento da interface gráfica (GTK4/Libadwaita ou Tauri).
- [ ] Criação de pacote de instalação `.deb`.
- [ ] Testes de compatibilidade em Ubuntu, Linux Mint, Debian, Pop!_OS e Zorin OS.
- [ ] Documentação de instalação pública e lançamento v1.0.
