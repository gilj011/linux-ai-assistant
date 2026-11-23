# Arquitetura Tecnica — kored

---

## 1. Visao Geral

O kored e uma ferramenta de inteligencia de sistemas Linux executada 100% localmente. A arquitetura foi projetada com base em modularidade, seguranca e desacoplamento entre a camada de inteligencia (LLM) e a camada do sistema operacional.

```text
┌─────────────────────────────────────────────────────────────┐
│                       Camada de UI                          │
│   CLI Interativo (Python + Rich)                            │
│   GUI Desktop (Futuro — TUI textual ou GTK4)                │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Nucleo da Aplicacao                      │
│                                                             │
│  ┌───────────────────────┐       ┌───────────────────────┐  │
│  │   System Inspector    │       │     LLM Provider      │  │
│  │  (Sondas read-only)   │       │  (Ollama — Qwen 2.5)  │  │
│  └───────────┬───────────┘       └───────────┬───────────┘  │
│              │                               │              │
│              └───────────────┬───────────────┘              │
│                              ▼                              │
│                  PromptBuilder + ContextEngine              │
│                              │                              │
│                              ▼                              │
│                      ActionParser                           │
│               (detecta blocos kored-action)                 │
│                              │                              │
│                              ▼                              │
│                  ControlledExecutor                         │
│           ┌────────────────────────────┐                    │
│           │  Validacao contra whitelist│                    │
│           │  Bloqueio de padroes       │                    │
│           │  Autorizacao humana [s/N]  │                    │
│           │  AuditLogger               │                    │
│           └────────────────────────────┘                    │
└──────────────────────────────┬──────────────────────────────┘
                               │ (somente comandos validados
                               ▼  e explicitamente autorizados)
┌─────────────────────────────────────────────────────────────┐
│               Sistema Operacional                           │
│          (Distribuicoes Debian-based)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Modulos

### `src/os_inspector.py` — OsInspector
- Le `/etc/os-release`, `uname -srm`, detecta gerenciadores de pacotes (`apt`, `dpkg`, `flatpak`, `snap`).
- Execucao estritamente read-only, sem privilegios de root.

### `src/ollama_client.py` — OllamaClient
- Comunicacao HTTP com Ollama em `http://localhost:11434`.
- Suporte a streaming via `/api/chat` (multi-turn, array de mensagens com roles).
- Legado `/api/generate` para consultas single-turn.
- Tratamento de Ollama offline com mensagem de erro clara.

### `src/prompt_builder.py` — PromptBuilder
- Constroi o prompt de sistema com identidade do kored, contexto do SO, modo operacional (READONLY/ASSISTED) e instrucoes de formatacao de acoes.

### `src/probes.py` — SystemProbes
- Sondas seguras e read-only: memoria (`free -m`), disco (`df -h`), servicos com falha (`systemctl --failed`), logs criticos (`journalctl -p 3 -xb`), interfaces de rede (`ip -br a`), status de servico especifico.
- Todas as sondas capturam excecoes silenciosamente para nao quebrar o diagnostico.

### `src/diagnostics.py` — DiagnosticEngine
- Orquestra as sondas do `SystemProbes`.
- `run_health_check()` — varredura completa do sistema.
- `run_service_check(service_name)` — foco em um servico especifico.
- Formata as evidencias coletadas em contexto estruturado para o LLM.

### `src/action_parser.py` — ActionParser
- Detecta e extrai blocos `kored-action` JSON embutidos nas respostas da IA.
- Suporta `write_file` e `run_command`.
- `strip_action_blocks()` remove os blocos antes de renderizar o texto ao usuario.

### `src/executor.py` — ControlledExecutor
- Carrega a whitelist de `config/allowed_commands.yaml`.
- `validate_command(cmd)` — verifica o comando contra `allowed_actions` e `blocked_patterns`.
- `execute_command(cmd)` — executa somente apos validacao e autorizacao.
- `write_file(path, content)` — cria arquivos sob autorizacao explicita.
- Usa `AuditLogger` para registrar todas as operacoes.

### `src/audit.py` — AuditLogger
- Grava em `~/.local/share/kored/audit.log` (JSONL).
- Persiste relatorios de diagnostico em `~/.local/share/kored/reports/diag_<timestamp>.log`.
- Metodos: `log_action()`, `log_diagnostic()`, `get_history()`.

### `src/cli.py` — KoredCLI
- Interface principal com `rich`.
- Modos: `readonly` (padrao) e `assisted` (`--assisted` / `-a`).
- Comandos internos da sessao: `diag`, `servico <nome>`, `historico`, `modo`, `sair`.
- `_handle_proposed_actions()` — exibe acoes propostas e solicita autorizacao `[s/N]`.
- Spinner animado durante processamento.

---

## 3. Modos Operacionais

| Modo | Flag | Comportamento |
|------|------|---------------|
| Seguro (readonly) | padrao | Consultas e diagnosticos; zero acoes no sistema |
| Assistido | `--assisted` / `-a` | IA pode propor `write_file` e `run_command`; exige `[s/N]` para cada acao |

---

## 4. Formato de Acao (kored-action)

No modo assistido, a IA pode embutir blocos JSON nas respostas:

```json
{
  "kored-action": "write_file",
  "path": "/home/usuario/correcoes.md",
  "content": "..."
}
```

```json
{
  "kored-action": "run_command",
  "command": "sudo systemctl restart docker",
  "description": "Reinicia o servico Docker"
}
```

O `ActionParser` extrai, valida e apresenta essas acoes ao usuario antes de qualquer execucao.

---

## 5. Seguranca

| Nivel de Acao | Exemplo | Fluxo |
|---|---|---|
| Leitura / Diagnostico | `uname`, `df -h`, `systemctl status` | Automatico (read-only) |
| Acao sugerida — usuario | `tar -xvf`, `git status` | Proposta pela IA, confirmacao `[s/N]` |
| Acao administrativa | `apt install`, `systemctl restart` | Proposta, validacao na whitelist, confirmacao `[s/N]` |
| Comandos proibidos | `rm -rf /`, `curl ... \| bash` | Bloqueado pelo validador antes de qualquer exibicao |

---

## 6. Dados Persistidos

| Arquivo | Proposito |
|---|---|
| `~/.local/share/kored/audit.log` | JSONL com historico de acoes e diagnosticos |
| `~/.local/share/kored/reports/diag_*.log` | Relatorios completos de diagnostico por sessao |
| `config/allowed_commands.yaml` | Whitelist editavel pelo usuario |
