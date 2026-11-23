# Linux AI Assistant — Project Foundation

> Documento inicial de definição do projeto.  
> Status: Planejamento / Ideação  
> Nome: Provisório  
> Público-alvo: Usuários iniciantes e intermediários de Linux  
> Plataforma inicial: Distribuições Linux baseadas em Debian

---

## 1. Visão geral

O Linux AI Assistant é um projeto pessoal de desenvolvimento de um assistente de inteligência artificial executado localmente no Linux.

Seu principal objetivo é facilitar a utilização do Linux, especialmente para pessoas que estão começando a utilizar o sistema operacional ou que ainda não possuem experiência com administração e manutenção de sistemas Linux.

O assistente deverá funcionar como uma combinação de:

- Assistente técnico.
- Ferramenta de diagnóstico.
- Solucionador de problemas.
- Professor de Linux.
- Auxiliar de configuração e administração do sistema.

A proposta não é desenvolver apenas um chatbot que responde perguntas sobre Linux, mas uma ferramenta capaz de compreender o ambiente operacional do usuário, analisar problemas reais e apresentar soluções contextualizadas.

Um dos principais diferenciais será a capacidade de ensinar enquanto ajuda a resolver os problemas.

## 2. Objetivos do projeto

### Objetivo principal

Desenvolver um assistente de IA local que torne o Linux mais acessível, compreensível e fácil de utilizar.

### Objetivos específicos

- Ajudar usuários a resolver problemas comuns no Linux.
- Identificar erros e possíveis causas.
- Auxiliar na configuração do sistema operacional.
- Explicar comandos e conceitos Linux de maneira didática.
- Realizar diagnósticos utilizando informações reais do sistema.
- Orientar usuários na instalação e manutenção de programas.
- Facilitar a migração de usuários provenientes do Windows.
- Incentivar o aprendizado e a autonomia dos usuários.

## 3. Público-alvo

O projeto será desenvolvido principalmente para:

1. Pessoas que estão migrando do Windows para Linux.
2. Usuários iniciantes que possuem pouca familiaridade com o terminal.
3. Usuários intermediários que precisam de auxílio em configurações e troubleshooting.
4. Pessoas interessadas em aprender administração de sistemas Linux.

A interface e a comunicação deverão priorizar uma linguagem acessível, evitando explicações excessivamente técnicas sem contextualização.

O assistente deverá conseguir explicar tanto para um iniciante quanto para alguém com conhecimentos mais avançados.

## 4. Sistemas operacionais suportados

O foco inicial será em distribuições baseadas em Debian.

Distribuições consideradas para o suporte inicial:

- Debian.
- Ubuntu.
- Linux Mint.
- Pop!_OS.
- Zorin OS.
- Elementary OS.

A arquitetura deverá permitir adicionar suporte a outras distribuições no futuro.

O projeto deverá identificar automaticamente a distribuição, sua versão, kernel e características relevantes do ambiente.

Não devemos presumir que todas as distribuições Debian-based possuem exatamente as mesmas ferramentas, configurações ou comportamentos.

## 5. Funcionalidades planejadas

### 5.1. Assistente de dúvidas

Interface de conversação para perguntas relacionadas ao Linux.

Exemplos:

- Como instalar um programa?
- Como configurar o Bluetooth?
- Como funciona o sistema de permissões?
- Qual a diferença entre APT, DPKG e Flatpak?
- Como configurar uma conexão de rede?
- Como interpretar determinado erro?

O assistente deverá apresentar explicações contextualizadas e exemplos práticos.

### 5.2. Diagnóstico inteligente

Uma das funcionalidades centrais do projeto.

O assistente deverá conseguir coletar informações do sistema operacional para compreender melhor o ambiente do usuário.

Possíveis informações coletadas:

| Informação | Ferramenta |
|---|---|
| Distribuição | `/etc/os-release` |
| Kernel | `uname` |
| Hardware PCI | `lspci` |
| Hardware USB | `lsusb` |
| Discos | `lsblk` |
| Memória | `free` |
| Serviços | `systemctl` |
| Logs | `journalctl` |
| Rede | `ip`, `nmcli` |
| Processos | `ps`, `top` |

A partir dessas informações, a IA deverá apresentar:

- Problema identificado.
- Possível causa.
- Evidências encontradas.
- Nível de gravidade.
- Solução recomendada.
- Explicação didática.

A coleta de informações deverá respeitar a privacidade do usuário.

### 5.3. Resolução de problemas

O assistente deverá ajudar na resolução de problemas reais do sistema.

Exemplo:

Um usuário encontra o seguinte erro:

```text
E: Unable to correct problems, you have held broken packages.
```

O assistente deverá:

1. Identificar que o erro está relacionado ao gerenciamento de pacotes.
2. Explicar o significado da mensagem.
3. Investigar possíveis causas.
4. Sugerir comandos apropriados.
5. Explicar o que cada comando executa.
6. Solicitar autorização antes de executar qualquer alteração.

O objetivo é evitar respostas genéricas que não considerem o ambiente real do usuário.

### 5.4. Professor Linux

O assistente também deverá funcionar como uma ferramenta de aprendizado.

Exemplo:

O usuário pergunta:

"O que é chmod?"

O assistente explica o conceito, apresenta exemplos e demonstra como funciona na prática.

Exemplo de comando:

```bash
chmod 755 arquivo.sh
```

A explicação deverá abordar permissões de leitura, escrita e execução, além da diferença entre proprietário, grupo e outros usuários.

Possíveis funcionalidades futuras:

- Explicação de comandos.
- Exemplos práticos.
- Exercícios interativos.
- Pequenas avaliações.
- Trilhas de aprendizado.
- Tutoriais contextualizados.

O objetivo é que o usuário aprenda a utilizar Linux e desenvolva autonomia.

### 5.5. Monitoramento do sistema

Funcionalidade planejada para acompanhar informações importantes do computador.

Possíveis indicadores:

- Utilização da CPU.
- Consumo de memória RAM.
- Temperatura.
- Armazenamento.
- Serviços ativos.
- Processos.
- Estado da rede.

No futuro, a IA poderá utilizar essas informações para identificar comportamentos anormais e sugerir investigações.

---

## 6. Arquitetura tecnológica inicial

A arquitetura ainda não está fechada. As tecnologias abaixo são candidatas discutidas durante a fase de planejamento.

### Linguagem principal

**Python**

Motivos:

- Boa integração com o ecossistema Linux.
- Facilidade para trabalhar com processos e comandos.
- Bibliotecas para diagnóstico e administração.
- Integração com modelos de IA.
- Facilidade de manutenção e expansão.

### Inteligência artificial

**Ollama**

Considerado como primeira opção para executar modelos localmente.

Possíveis modelos a avaliar:

- Qwen.
- Llama.
- Outros modelos compatíveis com execução local.

O projeto deverá avaliar a possibilidade de suportar diferentes mecanismos de inferência no futuro.

A execução local é uma característica central da proposta.

### Interface gráfica

Tecnologias ainda em avaliação:

- GTK4 + Libadwaita.
- Tauri.
- Interface web local.

A decisão deverá considerar integração com o desktop Linux, desempenho, facilidade de desenvolvimento e experiência do usuário.

### Backend

Possibilidade de utilizar:

- Python.
- FastAPI.
- Serviços locais para comunicação entre interface, IA e ferramentas do sistema.

### Base de conhecimento

Possíveis tecnologias:

- Markdown.
- SQLite.
- Documentação técnica estruturada.

A base de conhecimento deverá permitir organizar informações sobre distribuições, ferramentas, comandos, erros conhecidos e soluções.

---

## 7. Segurança e permissões

A segurança será um dos pilares fundamentais do projeto.

Como o assistente poderá interagir com o sistema operacional, não será aceitável permitir que a IA execute comandos arbitrários sem validação.

Princípios obrigatórios:

1. Nunca executar automaticamente comandos arbitrários gerados pela IA.
2. Separar operações de leitura das operações que modificam o sistema.
3. Implementar um executor controlado.
4. Validar comandos e parâmetros antes da execução.
5. Solicitar autorização explícita para alterações.
6. Mostrar ao usuário o comando que será executado.
7. Explicar os efeitos esperados da operação.
8. Registrar operações realizadas.
9. Evitar armazenar senhas e credenciais.
10. Aplicar o princípio do menor privilégio.

**Princípio fundamental:**

A IA recomenda e interpreta. Um componente controlado valida. O usuário autoriza. Somente então a operação é executada.

A arquitetura de segurança deverá ser planejada antes da implementação de qualquer mecanismo de execução de comandos.

---

## 8. Roadmap inicial

O desenvolvimento será dividido em etapas.

### Fase 1 — MVP

Objetivo: construir a primeira versão funcional.

- [ ] Definir nome e identidade do projeto.
- [ ] Definir arquitetura tecnológica.
- [ ] Criar estrutura do repositório.
- [ ] Desenvolver interface inicial.
- [ ] Integrar com Ollama.
- [ ] Implementar chat local.
- [ ] Identificar distribuição e versão.
- [ ] Coletar informações básicas do hardware.
- [ ] Implementar assistente de dúvidas Linux.

### Fase 2 — Diagnóstico

- [ ] Implementar coletor de informações.
- [ ] Integrar leitura de logs.
- [ ] Diagnosticar serviços.
- [ ] Analisar erros do sistema.
- [ ] Criar estrutura de evidências.
- [ ] Apresentar diagnósticos contextualizados.

### Fase 3 — Resolução

- [ ] Desenvolver executor controlado.
- [ ] Implementar validação de comandos.
- [ ] Implementar autorização do usuário.
- [ ] Criar histórico de operações.
- [ ] Implementar explicação prévia das alterações.

### Fase 4 — Educação

- [ ] Criar modo professor.
- [ ] Implementar explicação de comandos.
- [ ] Desenvolver exercícios práticos.
- [ ] Criar trilhas de aprendizado.
- [ ] Implementar acompanhamento de progresso.

### Fase 5 — Distribuição

- [ ] Criar pacote `.deb`.
- [ ] Implementar instalação simplificada.
- [ ] Testar em diferentes distribuições Debian-based.
- [ ] Criar documentação de instalação.
- [ ] Publicar o projeto no GitHub.

As fases são uma proposta inicial e poderão ser reorganizadas conforme as decisões técnicas.

---

## 9. Organização e documentação do projeto

O projeto deverá possuir documentação própria e versionada no Git.

Estrutura documental sugerida:

```text
linux-ai-assistant/
│
├── PROJECT.md
├── ARCHITECTURE.md
├── ROADMAP.md
├── DECISIONS.md
├── SESSION_LOG.md
│
├── README.md
├── CONTRIBUTING.md
├── LICENSE
│
├── src/
├── tests/
├── docs/
└── scripts/
```

### Responsabilidade de cada documento

**PROJECT.md**

Documento principal com a visão, objetivos, público-alvo e funcionalidades.

**ARCHITECTURE.md**

Documentação da arquitetura, componentes, tecnologias e comunicação entre módulos.

**ROADMAP.md**

Acompanhamento das funcionalidades planejadas, em desenvolvimento e concluídas.

**DECISIONS.md**

Registro das decisões técnicas e justificativas.

**SESSION_LOG.md**

Histórico das sessões de planejamento e desenvolvimento.

**README.md**

Apresentação pública do projeto, instalação, utilização e informações gerais.

---

## 10. Metodologia de desenvolvimento

O projeto será desenvolvido de maneira incremental e colaborativa.

Não queremos começar implementando funcionalidades sem antes compreender os problemas que elas deverão resolver.

Diretrizes:

- Discutir alternativas antes de decisões arquiteturais importantes.
- Priorizar simplicidade e manutenção.
- Evitar complexidade desnecessária.
- Documentar decisões.
- Implementar pequenas funcionalidades testáveis.
- Testar em ambientes Linux reais.
- Manter segurança como requisito fundamental.
- Não implementar funcionalidades apenas porque são tecnicamente possíveis.

O desenvolvimento deverá priorizar qualidade e consistência, não velocidade.

---

## 11. Instruções para o agente de desenvolvimento (Antigravity)

Você será um agente de apoio ao desenvolvimento deste projeto.

Sua responsabilidade será auxiliar no planejamento, arquitetura, implementação, testes, revisão de código e documentação.

### Comportamento esperado

1. Leia a documentação existente antes de propor alterações.
2. Entenda os objetivos do projeto antes de implementar funcionalidades.
3. Não tome decisões arquiteturais importantes sem apresentar alternativas e justificativas.
4. Não presuma que tecnologias ainda em avaliação já foram escolhidas.
5. Priorize soluções compatíveis com distribuições Debian-based.
6. Escreva código modular, organizado e documentado.
7. Considere segurança desde o início.
8. Explique alterações técnicas de maneira compreensível.
9. Não implemente funcionalidades fora do escopo sem discutir sua necessidade.
10. Mantenha a documentação sincronizada com a implementação.

### Regra importante

**Não comece implementando o projeto inteiro.**

A primeira responsabilidade será analisar este documento, identificar pontos que precisam ser definidos e ajudar a construir a arquitetura inicial.

As decisões deverão ser tomadas de maneira colaborativa.

---

## 12. Princípio fundamental do projeto

O Linux AI Assistant não deverá apenas resolver problemas.

Ele deverá ajudar as pessoas a compreender o Linux, perder o medo do terminal e desenvolver conhecimento suficiente para administrar seus próprios sistemas.

A proposta é transformar uma experiência muitas vezes frustrante para iniciantes em uma experiência de aprendizado.

**Queremos um assistente que resolva problemas hoje e ensine o usuário a resolvê-los sozinho amanhã.**

---

## 13. Estado atual

Neste momento, o projeto está na fase de ideação e definição.

Já foram estabelecidos:

- O propósito principal.
- O público-alvo.
- O foco inicial em Debian-based.
- A execução local como característica central.
- Os cinco módulos funcionais iniciais.
- A importância da segurança.
- A necessidade de documentação e versionamento.
- A metodologia incremental de desenvolvimento.

Ainda precisam ser definidos:

- Nome definitivo.
- Interface gráfica.
- Linguagem e arquitetura finais do backend.
- Modelo de IA.
- Estratégia de integração com o sistema.
- Gerenciamento de permissões.
- Estratégia de distribuição.
- Escopo exato do MVP.

**Próxima atividade: iniciar a discussão e definição da arquitetura técnica do MVP, sem começar a implementação antes de validar as decisões fundamentais.**

