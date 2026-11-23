# Guia de Contribuicao — kored

Obrigado pelo interesse em contribuir com o **kored**.

O objetivo e construir uma ferramenta confiavel, tecnicamente solida e de alto valor real para a comunidade Linux — de iniciantes a engenheiros de sistemas.

---

## Principios que nao se negociam

1. **Seguranca por design:** Qualquer funcionalidade que interaja com o sistema operacional deve respeitar o principio do menor privilegio. Nenhuma acao e executada sem validacao previa e confirmacao explicita do usuario.
2. **Sem execucao autonoma:** A IA nunca roda comandos por conta propria. O humano esta sempre no loop.
3. **Decisoes documentadas:** Mudancas arquiteturais relevantes devem ser propostas e registradas em [docs/DECISIONS.md](DECISIONS.md).
4. **Zero emojis:** Nem no codigo, nem nos logs, nem na documentacao.
5. **Codigo em ingles, documentacao em portugues:** Identificadores, variaveis e funcoes em ingles; docs e comentarios em portugues.

---

## Como contribuir

1. Faca um fork do repositorio no GitHub.
2. Crie uma branch descritiva para a sua feature ou correcao:
   ```bash
   git checkout -b feat/nome-da-melhoria
   # ou
   git checkout -b fix/nome-do-bug
   ```
3. Implemente, escreva ou atualize os testes correspondentes em `tests/`.
4. Valide a suite completa antes de commitar:
   ```bash
   make test
   ```
5. Commite com mensagens semanticas (lowercase):
   ```
   feat(modulo): descricao curta do que foi feito
   fix(cli): corrigir exibicao do spinner ao usar --diag
   docs: atualizar ROADMAP com fase 6
   ```
6. Envie para o seu fork e abra um **Pull Request** descrevendo:
   - O que foi alterado e por que.
   - Testes executados.
   - Se ha impacto no `config/allowed_commands.yaml` ou no comportamento de seguranca.

---

## Estrutura do projeto

```text
kored/
├── main.py                     # Ponto de entrada
├── kored                       # Executavel direto (./kored)
├── Makefile                    # Ciclo de vida: test, install, deb, clean
├── requirements.txt            # Dependencias Python
├── config/
│   └── allowed_commands.yaml   # Whitelist de comandos e padroes bloqueados
├── src/
│   ├── cli.py                  # Interface CLI principal
│   ├── ollama_client.py        # Cliente Ollama com streaming
│   ├── os_inspector.py         # Leitura do ambiente do sistema
│   ├── prompt_builder.py       # Construcao de prompts e contexto
│   ├── probes.py               # Sondas seguras de estado do sistema
│   ├── diagnostics.py          # Motor de diagnostico
│   ├── executor.py             # Executor controlado com validacao
│   ├── action_parser.py        # Parser de acoes estruturadas kored-action
│   └── audit.py                # Auditoria e persistencia de relatorios
├── tests/                      # Suite de testes (unittest)
├── scripts/                    # Instalacao, desinstalacao, build .deb, autocompletar
└── docs/                       # Documentacao tecnica e historico do projeto
```

---

## Padroes de codigo

- Python 3.10+, sem dependencias externas desnecessarias.
- Use `rich` para saida no terminal — sem `print()` direto no CLI.
- Novos modulos em `src/`, novos testes em `tests/test_<modulo>.py`.
- Nao quebre a suite: `make test` deve sempre passar com `OK`.
