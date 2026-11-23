# Roadmap — kored

---

## Fase 1 — MVP CLI (Concluida)

- [x] Modulo de inspecao de ambiente (`os_inspector`) lendo `/etc/os-release` e `uname`.
- [x] Cliente Ollama com streaming e suporte multi-turn (`/api/chat`).
- [x] CLI interativo com `rich`: destaque de codigo Bash, spinner, formatacao de paineis.
- [x] Whitelist inicial de comandos (`config/allowed_commands.yaml`).
- [x] Identidade oficial **kored** e executavel `./kored`.

---

## Fase 2 — Diagnosticos e Analise de Logs (Concluida)

- [x] Sondas seguras read-only (`SystemProbes`): memoria, disco, servicos com falha, logs criticos, rede.
- [x] Motor de diagnostico (`DiagnosticEngine`): `run_health_check()` e `run_service_check()`.
- [x] Flags `--diag` e `--service <nome>` no CLI e comando `diag` na sessao interativa.

---

## Fase 3 — Executor Controlado e Resolucao Assistida (Concluida)

- [x] `ControlledExecutor` com validacao contra whitelist YAML.
- [x] Sanitizacao e bloqueio de padroes perigosos (`blocked_patterns`).
- [x] Chave seletora: Modo Seguro (readonly) vs Modo Assistido (`--assisted`).
- [x] `ActionParser` para blocos `kored-action` (`write_file`, `run_command`).
- [x] Caixa de autorizacao humana obrigatoria `[s/N]` para toda acao proposta.

---

## Fase 4 — Auditoria e Persistencia (Concluida)

- [x] `AuditLogger` gravando em `~/.local/share/kored/audit.log` (JSONL).
- [x] Persistencia de relatorios em `~/.local/share/kored/reports/diag_*.log`.
- [x] Comando `historico` / flag `--audit` com tabela Rich no terminal.
- [x] Registro de aprovacoes, recusas e resultados de execucao.

---

## Fase 5 — Empacotamento e Distribuicao (Concluida)

- [x] `scripts/install.sh` — instalacao em `~/.local/bin/kored` ou `/usr/local/bin/kored`.
- [x] `scripts/uninstall.sh` — remocao limpa de todos os artefatos instalados.
- [x] `scripts/kored_completion.bash` — autocompletar nativo para Bash.
- [x] `scripts/build_deb.sh` — pacote `dist/kored_0.3.0_all.deb` via `dpkg-deb`.
- [x] `Makefile` com targets: `test`, `install`, `uninstall`, `deb`, `clean`.
- [x] Suite de testes: 27 testes passando (`make test`).

---

## Fase 6 — Configuracao do Usuario (Planejada)

- [ ] `config/kored.yaml` — modelo preferido, modo padrao, idioma, nivel de verbosidade.
- [ ] Carregamento automatico das preferencias ao iniciar.
- [ ] Comando `kored --config` para editar as preferencias sem abrir o arquivo manualmente.

---

## Fase 7 — Diagnosticos Avancados (Planejada)

- [ ] Sondas de I/O de disco (`iostat`).
- [ ] Sockets e portas abertas (`ss -tulpn`).
- [ ] Descritores de arquivo por processo (`lsof`).
- [ ] Uso de CPU por processo (`ps aux` estruturado).
- [ ] Relatorio consolidado de saude com nivel de severidade por sonda.

---

## Fase 8 — Interface TUI (Planejada)

- [ ] Dashboard em terminal com `textual`.
- [ ] Paineis ao vivo: servicos, memoria, disco, logs recentes.
- [ ] Chat integrado ao dashboard.
- [ ] Zero dependencia de Wayland/X11 — funciona em qualquer terminal.

---

## Fase 9 — Interface Grafica Desktop (Longo Prazo)

- [ ] Avaliacao entre GTK4/Libadwaita (nativo GNOME/Pop!_OS) e Tauri (WebView multiplataforma).
- [ ] Reaproveitamento total do nucleo Python das fases anteriores.
- [ ] Empacotamento como `.deb` com icone e entrada no menu do sistema.
