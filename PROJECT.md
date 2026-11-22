# kored — Linux Systems Intelligence

> Copiloto local de engenharia de sistemas, troubleshooting e assistência técnica para Linux.

---

## 1. Visão Geral

O **kored** é um assistente técnico e copiloto de inteligência de sistemas Linux executado **100% localmente**, projetado para oferecer assistência de alto nível técnico, diagnósticos precisos e automação segura tanto para iniciantes quanto para engenheiros e administradores de sistemas experientes.

O nome remete ao núcleo do sistema (*Kore*) somado ao sufixo clássico dos daemons do Linux (*d*), operando como um parceiro silencioso, confiável e poderoso no terminal.

O **kored** atua de forma combinada como:
* **Copiloto Técnico:** Sugere soluções, sintaxes e comandos modernos de padrão de produção.
* **Ferramenta de Diagnóstico & Troubleshooting:** Inspeciona o ambiente real do sistema (versão da distro, kernel, logs, serviços) para contextualizar a ajuda com precisão cirúrgica.
* **Mestre em Internals de Linux:** Dissecar a mecânica interna do sistema operacional (processos, sinais, descritores, cgroups, namespaces, storage drivers, tuning de rede).
* **Guardião de Segurança:** Possui um executor controlado com validação prévia e autorização humana explícita.

---

## 2. Pilares Fundamentais

1. **Privacidade e Execução Local:**
   * Utiliza modelos locais via [Ollama](https://ollama.com/) (como `qwen2.5:7b` e `qwen2.5:3b`). Nenhum dado do sistema ou comando é enviado para nuvens externas.
2. **Abordagem Adaptativa de Engenharia:**
   * Sem infantilização ou explicações prolixas. Clareza cristalina para dúvidas cotidianas e profundidade técnica rigorosa para tópicos avançados.
3. **Padrão de Produção:**
   * Priorização de ferramentas e práticas modernas do ecossistema Linux (`ss`, `ip`, `systemctl`, journald, containers, permissões refinadas).
4. **Segurança Estrita (Human-in-the-Loop):**
   * A IA nunca executa comandos arbitrários sem validação.
   * O sistema conta com uma lista de comandos permitidos totalmente auditável e editável pelo usuário.
5. **Foco Inicial no Ecossistema Debian-based:**
   * Distribuições suportadas inicialmente: Debian, Ubuntu, Pop!_OS, Linux Mint, Zorin OS e Elementary OS.
