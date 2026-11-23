# Historico de Sessoes — kored

---

## Sessao 01 — 2026-11-22

**Participantes:** gcampos (usuario), Antigravity (agente de desenvolvimento)

### Objetivos
- Definicao inicial do projeto a partir do documento de ideacao (`IDEACAO_INICIAL.md`).
- Alinhamento de hardware alvo, modelo de IA, seguranca e escopo do MVP.
- Estruturacao do repositorio Git e documentacao inicial.

### Decisoes tomadas
- Hardware de referencia: AMD Radeon RX 580 (8 GB VRAM), Pop!_OS 24.04 LTS, Kernel 7.2.15.
- Modelo: `qwen2.5:7b` principal, `qwen2.5:3b` fallback.
- Executor com whitelist auditavel e confirmacao humana obrigatoria.
- MVP: CLI interativo em Python + Rich com streaming de tokens.
- Nome oficializado: **kored** (*Kore* + *d*). ADR 005 registrado.
- Spinner animado e historico de conversa multi-turn via `/api/chat`.

---

## Sessao 02 — 2026-11-22 (continuacao)

### Objetivos
- Implementar as fases 1 a 5 do roadmap.

### Entregas

**Fase 1 — MVP CLI**
- `src/os_inspector.py` — le `/etc/os-release`, `uname`, detecta gerenciadores de pacotes.
- `src/ollama_client.py` — cliente Ollama com streaming e suporte multi-turn.
- `src/prompt_builder.py` — construcao de prompts com consciencia de modo.
- `src/cli.py` — CLI interativo completo com spinner e toggle de modo.
- `main.py` — ponto de entrada.
- `kored` — executavel com `chmod +x`.

**Fase 2 — Diagnosticos**
- `src/probes.py` — sondas read-only: memoria, disco, servicos com falha, logs criticos, rede.
- `src/diagnostics.py` — `DiagnosticEngine` com `run_health_check()` e `run_service_check()`.

**Fase 3 — Executor Controlado**
- `src/executor.py` — `ControlledExecutor` com whitelist YAML, validacao e execucao sob autorizacao.
- `src/action_parser.py` — parser de blocos `kored-action` (write_file, run_command).
- `src/cli.py` atualizado — `_handle_proposed_actions()`, chave seletora, flag `--assisted`.

**Fase 4 — Auditoria**
- `src/audit.py` — `AuditLogger` gravando em `~/.local/share/kored/audit.log` (JSONL).
- Persistencia de relatorios em `~/.local/share/kored/reports/`.
- Comando `historico` / flag `--audit` com tabela Rich.

**Fase 5 — Instalacao e Empacotamento**
- `scripts/install.sh` — instalacao em `~/.local/bin/kored` ou `/usr/local/bin/kored`.
- `scripts/uninstall.sh` — remocao limpa.
- `scripts/kored_completion.bash` — autocompletar Bash nativo.
- `scripts/build_deb.sh` — pacote `dist/kored_0.3.0_all.deb` via `dpkg-deb`.
- `Makefile` — targets: `test`, `install`, `uninstall`, `deb`, `clean`.

**Suite de testes**
- 27 testes passando: `Ran 27 tests in 0.036s — OK`
- Cobertura: `os_inspector`, `ollama_client`, `prompt_builder`, `cli`, `diagnostics`, `action_parser`, `executor`, `audit`.

### Erros resolvidos
| Problema | Solucao |
|----------|---------|
| `git push` com senha falhou (GitHub descontinuou auth por senha) | Configurado Personal Access Token |
| `ModuleNotFoundError: No module named 'src'` ao rodar `src/cli.py` diretamente | Injecao de `PROJECT_ROOT` no `sys.path` em `cli.py` |
| `dpkg-deb: control directory has bad permissions 777` | `chmod 755` explicitamente apos criar `DEBIAN/` |
| `cp: cannot stat 'LICENSE'` no build_deb | Copia de LICENSE tornou-se condicional |
| Emojis residuais apos primeiro sweep | Scan completo com regex confirma zero emojis |
