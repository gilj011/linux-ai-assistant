# Linux AI Assistant — Projeto

> Assistente de IA local, didático e seguro para usuários de Linux.

---

## 1. Visão Geral

O **Linux AI Assistant** é um assistente de inteligência artificial executado **100% localmente**, projetado para tornar o ecossistema Linux mais acessível, compreensível e amigável, especialmente para iniciantes e pessoas em processo de migração do Windows.

Diferente de chatbots convencionais que apenas cospem comandos ou de scripts que executam ações como uma caixa-preta, a premissa central deste projeto é:

> **"Resolver problemas hoje e ensinar o usuário a resolvê-los sozinho amanhã."**

O assistente atua de forma combinada como:
* **Assistente Técnico:** Ajuda a encontrar e formular comandos para tarefas do dia a dia.
* **Ferramenta de Diagnóstico:** Inspeciona o ambiente real do sistema (versão da distro, kernel, logs, serviços) para contextualizar a ajuda.
* **Professor Linux:** Explica de forma didática o que cada comando, parâmetro e permissão significa.
* **Guardião de Segurança:** Possui um executor controlado com validação prévia e autorização explícita do usuário.

---

## 2. Pilares Fundamentais

1. **Privacidade e Execução Local:**
   * Utiliza modelos locais via [Ollama](https://ollama.com/) (como Qwen 2.5 7B / 3B). Nenhum dado do sistema do usuário ou do terminal é enviado para serviços de nuvem de terceiros.
2. **Didática e Autonomia:**
   * Nunca apenas entregar um comando isolado; sempre explicar o porquê, suas opções e impactos.
3. **Segurança Estrita (Human-in-the-Loop):**
   * A IA nunca executa comandos diretamente.
   * O sistema possui uma lista de comandos permitidos auditável e editável pelo usuário.
   * Toda ação que modifica o sistema exige confirmação explícita após explicação do impacto.
4. **Foco Inicial no Ecossistema Debian-based:**
   * Distribuições suportadas inicialmente: Debian, Ubuntu, Linux Mint, Pop!_OS, Zorin OS e Elementary OS.

---

## 3. Público-Alvo

1. **Usuários em transição:** Pessoas vindas do Windows que sentem estranheza com conceitos como montagem de discos, permissões e ausência de arquivos `.exe`.
2. **Iniciantes no terminal:** Usuários que têm receio de quebrar o sistema ao digitar comandos.
3. **Usuários intermediários:** Administradores e desenvolvedores que buscam diagnósticos rápidos de serviços (`systemd`), redes (`ip`/`nmcli`) e logs (`journalctl`).
