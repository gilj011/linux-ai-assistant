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

---

### ADR 005: Identidade Oficial 'kored' e Postura de Engenharia de Sistemas
* **Status:** Aceita
* **Data:** 2026-11-22
* **Contexto:** A proposta inicial de "Professor Linux" soava escolar demais e limitava o alcance do assistente. Usuários avançados, desenvolvedores e sysadmins necessitam de assistência de alto nível técnico, enquanto iniciantes precisam de clareza sem condescendência. Além disso, o nome provisório precisava ser substituído por uma identidade forte e nativa do ecossistema Linux.
* **Decisão:**
  1. Definir o nome oficial do projeto e comando CLI como **`kored`** (remetendo a *Kore* + o sufixo *d* dos daemons do Linux).
  2. Evoluir a persona para um **copiloto técnico de engenharia de sistemas**, com abordagem adaptativa: clareza cirúrgica para iniciantes e profundidade de baixo nível (internals, networking, performance, debugging) para usuários experientes.
* **Consequências:**
  * *Positivas:* Posicionamento sério, profissional e atrativo para toda a comunidade Linux; eliminação de ruídos ou explicações prolixas; comando curto e natural para o terminal (`kored`).

---

### ADR 006: Chave Seletora de Modos e Autorizacao Humana Obrigatoria
* **Status:** Aceita
* **Data:** 2026-11-22
* **Contexto:** O assistente precisa ser capaz de criar arquivos de instrucao/scripts e sugerir comandos de correcao no sistema, mas a IA nao pode sob hipotese alguma executar acoes de forma autonoma sem o controle do usuario.
* **Decisão:**
  1. Criar uma chave seletora operacional com dois modos:
     - `readonly` (Modo Seguro): o kored atua apenas como consultor e analista; nenhuma acao ou gravacao em disco e executada.
     - `assisted` (Modo Assistido): a IA pode propor a criacao de arquivos e comandos de correcao via blocos estruturados `kored-action`.
  2. Implementar uma caixa de autorizacao interativa obrigatoria no CLI: toda acao proposta no modo assistido exibe resumo detalhado e exige confirmacao manual `[s/N]`. Sem o `s` explicito, nada e alterado.
  3. Validar comandos contra a lista de padroes bloqueados (`config/allowed_commands.yaml`).
* **Consequências:**
  * *Positivas:* Seguranca maxima por design, blindando o sistema contra alucinacoes da IA enquanto confere capacidade operacional real sob supervisao do usuario.
