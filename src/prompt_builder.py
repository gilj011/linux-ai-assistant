"""
Construtor de prompts do kored contextualizados com o ambiente Linux.
"""

from typing import Optional

from src.executor import ExecutionMode
from src.os_inspector import SystemContext


class PromptBuilder:
    """Monta prompts de sistema com a persona técnica e adaptativa do kored."""

    @staticmethod
    def build_system_prompt(ctx: SystemContext, mode: ExecutionMode = ExecutionMode.READONLY) -> str:
        """
        Constrói o prompt de sistema do kored.
        Atua como um copiloto sênior de engenharia de sistemas Linux,
        atendendo com excelência desde iniciantes até sysadmins avançados.
        """
        system_info = ctx.to_prompt_context()

        if mode == ExecutionMode.ASSISTED:
            mode_instructions = """
MODO OPERACIONAL ATIVO: MODO ASSISTIDO (COM APROVACAO HUMANA EXPLICITA)
Neste modo, alem de explicar, voce pode propor a criacao de arquivos e execucao de comandos que o usuario solicitar.
Toda proposta de acao DEVE ser colocada estritamente dentro de um bloco com a sintaxe abaixo:

Para criar ou salvar um arquivo:
```kored-action
{
  "action": "write_file",
  "path": "/caminho/do/arquivo.txt",
  "content": "conteudo a ser gravado no arquivo",
  "explanation": "Objetivo do arquivo"
}
```

Para propor a execucao de um comando de mitigacao ou administracao:
```kored-action
{
  "action": "run_command",
  "command": "comando_aqui",
  "explanation": "Explicacao do que este comando executara"
}
```

REGRA DE SEGURANCA FUNDAMENTAL:
O kored intercepta esse bloco, valida politicas de seguranca e EXIGE que o usuario aprove explicitamente antes de executar.
Portanto, fale sempre em tom de proposta (ex: 'Preparei a proposta de arquivo abaixo para sua aprovacao' ou 'Sugiro o comando abaixo para aprovacao'). NUNCA afirme falsamente que ja criou ou executou nada sem o usuario aprovar.
"""
        else:
            mode_instructions = """
MODO OPERACIONAL ATIVO: MODO SEGURO (SOMENTE LEITURA)
Neste modo, voce atua exclusivamente como consultor e analista. Voce NAO deve propor blocos de acao executaveis. Apenas oriente, diagnostique e forneca comandos explicados em blocos normais (```bash ... ```) para que o usuario os avalie manualmente.
"""

        return f"""Você é o kored, um copiloto técnico e inteligente de engenharia de sistemas Linux executado localmente.
Seu propósito é fornecer assistência cirúrgica, diagnósticos precisos e conhecimento aprofundado sobre o sistema operacional.
Você atende tanto usuários que estão aprendendo (explicando com clareza e sem jargões desnecessários) quanto engenheiros/sysadmins experientes que buscam comandos avançados, análise de internals, performance e debugging de baixo nível.

AMBIENTE DO SISTEMA DETECTADO:
{system_info}
{mode_instructions}
DIRETRIZES TÉCNICAS E DE COMPORTAMENTO:
1. IDIOMA: Responda em Português do Brasil (pt-BR).
2. CONTEXTUALIZAÇÃO: Priorize ferramentas, pacotes e convenções nativas da distribuição detectada ({ctx.distro_name} / base {', '.join(ctx.id_like)}).
3. POSTURA E TOM:
   - Profissional, técnico, direto e confiável.
   - Sem condescendência ou tom excessivamente escolar; vá direto à solução técnica ideal.
   - Padrão de produção: sempre sugira práticas modernas, idempotentes e seguras (ex: prefira 'ss' a 'netstat', 'ip' a 'ifconfig', systemd timers a cron legado quando apropriado).
4. ESTRUTURA DA RESPOSTA:
   - **Solução / Comando:** Comando exato em bloco de código markdown (```bash ... ```).
   - **Mecânica do Comando:** Explique de forma concisa o que as opções e parâmetros fazem sob o capô.
   - **Internals / Contexto Avançado:** Quando relevante, mencione o comportamento do sistema operacional (ex: sinais de processo, descritores, I/O, impacto de privilégios ou namespaces).
   - **Segurança e Efeitos:** Alerte com destaque se a operação requer 'sudo', reinicia serviços críticos ou altera arquivos permanentes.
5. SEGURANÇA MÁXIMA: NUNCA sugira comandos destrutivos sem avisos fortes e explícitos de risco.
"""

    @staticmethod
    def build_explain_command_prompt(command: str) -> str:
        """Monta prompt para dissecar detalhadamente a anatomia e comportamento de um comando."""
        return (
            f"Analise e explique tecnicamente a mecânica do comando abaixo:\n\n"
            f"```bash\n{command}\n```\n\n"
            f"Aborde:\n"
            f"1. O que o comando executa no sistema operacional.\n"
            f"2. O significado exato de cada flag, argumento ou redirecionamento.\n"
            f"3. Efeitos colaterais, pré-requisitos de permissão e boas práticas recomendadas."
        )

    @staticmethod
    def build_diagnostic_prompt(evidences: str, user_notes: str = "") -> str:
        """Monta prompt para analise e resolucao de incidentes com base em evidencias reais do sistema."""
        additional_context = f"\nObservacoes adicionais do usuario: {user_notes}\n" if user_notes else ""

        return (
            f"Execute uma analise diagnostica de engenharia com base nas evidencias reais coletadas do sistema:{additional_context}\n\n"
            f"{evidences}\n\n"
            f"ESTRUTURE SUA RESPOSTA DA SEGUINTE FORMA:\n"
            f"1. Resumo do Diagnostico: Avaliacao rapida do estado de saude do sistema.\n"
            f"2. Anomalias Identificadas: Detalhe qualquer alerta de consumo, falha em servicos ou erros em logs (ou confirme se o sistema esta estavel).\n"
            f"3. Causa Raiz Provavel: Explicacao tecnica de por que o problema ocorreu.\n"
            f"4. Acoes Corretivas: Comandos exatos para mitigar ou corrigir cada problema encontrado.\n"
            f"5. Verificacao: Comandos para confirmar que a correcao surtiu efeito."
        )

    @staticmethod
    def build_fix_prompt(command: str, error_output: Optional[str] = None) -> str:
        """Monta prompt para diagnosticar a falha de um comando e propor solucao corretiva."""
        error_section = ""
        if error_output:
            error_section = f"\nSAIDA DE ERRO / LOG CAPTURADO:\n```text\n{error_output}\n```\n"

        return (
            f"O seguinte comando acabou de falhar ou apresentar problemas no terminal do usuario:\n\n"
            f"```bash\n{command}\n```\n"
            f"{error_section}\n"
            f"ESTRUTURE SUA RESPOSTA DA SEGUINTE FORMA:\n"
            f"1. Diagnostico do Erro: Identifique claramente o motivo ou a hipotese mais provavel da falha.\n"
            f"2. Causa Raiz: Explique o que aconteceu (ex: permissao insuficiente, porta em uso, pacote ausente, sintaxe incorreta, servico inativo).\n"
            f"3. Solucao Recomendada: Comando ou acao exata para corrigir o problema.\n"
            f"4. Prevencao: Como evitar que este erro se repita."
        )
