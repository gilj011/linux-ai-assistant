# Registro de Decisões Técnicas (ADR) — Linux AI Assistant

Este documento registra as principais decisões de arquitetura e design técnico adotadas no projeto, bem como suas motivações e alternativas consideradas.

---

### ADR 001: Execução 100% Local com Ollama
* **Status:** Aceita
* **Data:** 2026-11-22
* **Contexto:** O projeto precisa oferecer assistência inteligente para tarefas de administração e troubleshooting no Linux garantindo privacidade estrita e sem custos de API por requisição.
* **Decisão:** Adotar o [Ollama](https://ollama.com/) como o provedor de inferência local padrão.
* **Consequências:**
  * *Positivas:* Nenhuma telemetria ou dado confidencial de arquivos do usuário sai da máquina; facilidade de instalação e gerenciamento de modelos.
  * *Desafios:* O desempenho dependerá do hardware local (RAM/VRAM e processador do usuário).

---

### ADR 002: Modelo de Referência Qwen 2.5 7B (Fallback: 3B)
* **Status:** Aceita
* **Data:** 2026-11-22
* **Contexto:** Definir um modelo de IA capaz de rodar confortavelmente em GPUs na faixa de 8GB de VRAM (como a AMD Radeon RX 580) ou CPUs com 16GB de RAM, com excelência em sintaxe Bash/Linux e ótimo suporte ao português.
* **Decisão:**
  * Modelo principal: `qwen2.5:7b` (~4.7 GB VRAM).
  * Modelo fallback / ultraleve: `qwen2.5:3b` (~2.0 GB VRAM).
* **Consequências:**
  * *Positivas:* Qwen 2.5 tem os melhores benchmarks de código e raciocínio técnico da categoria, além de fluência nativa e natural em português.
  * *Alternativas consideradas:* `llama3.2:3b` (bom, porém inferior ao Qwen em sintaxe de terminal) e `deepseek-r1:7b` (gera cadeias de pensamento longas que podem atrasar respostas diretas de comandos).

---

### ADR 003: Validação Estrita e Whitelist de Comandos Editável
* **Status:** Aceita
* **Data:** 2026-11-22
* **Contexto:** Assistentes de IA podem sofrer de alucinações e sugerir comandos potencialmente danosos (`rm -rf`, formatações indevidas). Nunca se deve delegar execução automática de comandos para uma IA.
* **Decisão:**
  1. Separar categoricamente operações de leitura daquelas que alteram o sistema.
  2. Implementar uma lista de comandos permitidos (*whitelist*) que o próprio usuário pode auditar e editar em arquivo de configuração.
  3. Exigir confirmação humana explícita antes de rodar qualquer comando que modifique o ambiente.
* **Consequências:**
  * *Positivas:* Segurança garantida por design, mitigando riscos de destruição acidental de arquivos ou configurações.

---

### ADR 004: Início pelo MVP em CLI (Python + Rich)
* **Status:** Aceita
* **Data:** 2026-11-22
* **Contexto:** O projeto prevê interface gráfica desktop no futuro, mas precisa de validação ágil do motor de IA, contexto de sistema e didática das respostas.
* **Decisão:** Construir a Fase 1 como uma CLI rica e interativa em Python 3 com a biblioteca `rich`.
* **Consequências:**
  * *Positivas:* Desenvolvimento rápido, baixo acoplamento e facilidade de teste direto no terminal. O núcleo desenvolvido para o CLI será reaproveitado diretamente quando a interface gráfica for acoplada nas fases futuras.
