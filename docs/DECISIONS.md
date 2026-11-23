# Registro de Decisoes Tecnicas (ADR) — kored

---

### ADR 001: Execucao 100% Local com Ollama
- **Status:** Aceita
- **Data:** 2026-11-22
- **Decisao:** Adotar o [Ollama](https://ollama.com/) como provedor de inferencia local padrao.
- **Motivacao:** Privacidade estrita, zero telemetria, sem custos de API, dados do usuario nunca saem da maquina.
- **Desafios:** Desempenho dependente do hardware local (RAM/VRAM).

---

### ADR 002: Modelo Qwen 2.5 7B (fallback: 3B)
- **Status:** Aceita
- **Data:** 2026-11-22
- **Decisao:** Modelo principal `qwen2.5:7b` (~4.7 GB VRAM); fallback `qwen2.5:3b` (~2.0 GB VRAM).
- **Motivacao:** Melhor benchmark de codigo e raciocinio tecnico da categoria open-weight; fluencia nativa em portugues; cabe confortavelmente em GPUs de 8 GB VRAM (ex: RX 580) ou CPUs com 16 GB RAM.
- **Alternativas descartadas:** `llama3.2:3b` (inferior em sintaxe de terminal), `deepseek-r1:7b` (cadeias de raciocinio longas que atrasam respostas diretas).

---

### ADR 003: Whitelist de Comandos e Validacao Estrita
- **Status:** Aceita
- **Data:** 2026-11-22
- **Decisao:**
  1. Separar categoricamente operacoes de leitura daquelas que alteram o sistema.
  2. Whitelist editavel pelo usuario em `config/allowed_commands.yaml`.
  3. Confirmacao humana `[s/N]` obrigatoria antes de qualquer comando que modifique o ambiente.
- **Motivacao:** IAs podem alucinar comandos destrutivos; nunca delegar execucao autonoma.

---

### ADR 004: MVP em CLI (Python + Rich)
- **Status:** Aceita
- **Data:** 2026-11-22
- **Decisao:** CLI rica e interativa em Python 3 com `rich` como entrega do MVP.
- **Motivacao:** Desenvolvimento rapido, baixo acoplamento, testavel diretamente no terminal. O nucleo e reaproveitado quando interfaces graficas forem acopladas.

---

### ADR 005: Identidade oficial 'kored'
- **Status:** Aceita
- **Data:** 2026-11-22
- **Decisao:** Nome oficial **kored** (*Kore* + sufixo *d* dos daemons Linux). Postura de copiloto de engenharia de sistemas — sem condescendencia, clareza cirurgica para iniciantes, profundidade tecnica para experientes.
- **Motivacao:** "Professor Linux" soava escolar e limitava o alcance. Sysadmins e SREs precisam de uma ferramenta de alto nivel tecnico, nao de um tutor.

---

### ADR 006: Chave Seletora de Modos e Autorizacao Humana
- **Status:** Aceita
- **Data:** 2026-11-22
- **Decisao:**
  1. Dois modos: `readonly` (somente consultas e diagnosticos) e `assisted` (pode propor acoes via blocos `kored-action`).
  2. Toda acao proposta no modo assistido exige confirmacao explicita `[s/N]` — sem `s` explicito, nada e alterado.
  3. Comandos validados contra `blocked_patterns` antes de qualquer apresentacao ao usuario.
- **Motivacao:** Capacidade operacional real sob supervisao total do usuario; zero risco de execucao autonoma.
