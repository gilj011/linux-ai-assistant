"""
Interface de Linha de Comando (CLI) interativa do Linux AI Assistant.
Apresenta respostas didáticas em tempo real com streaming, memória de conversa e indicador de carregamento.
"""

import argparse
from pathlib import Path
import sys
from typing import Dict, List, Optional

# Garante que a raiz do projeto esteja no sys.path mesmo ao executar diretamente
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from src.ollama_client import OllamaClient
from src.os_inspector import OSInspector, SystemContext
from src.prompt_builder import PromptBuilder

console = Console()


class LinuxAssistantCLI:
    """Controlador da interface de terminal do assistente com memória de sessão."""

    MAX_HISTORY_MESSAGES = 20

    def __init__(self, model: str = "qwen2.5:7b", base_url: Optional[str] = None):
        self.context: SystemContext = OSInspector.get_system_context()
        self.client = OllamaClient(base_url=base_url, model=model)
        self.system_prompt = PromptBuilder.build_system_prompt(self.context)
        self.conversation_history: List[Dict[str, str]] = []
        self.reset_conversation()

    def reset_conversation(self) -> None:
        """Reinicia o histórico da conversa mantendo o prompt do sistema."""
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]

    def _trim_history_if_needed(self) -> None:
        """Mantém o histórico dentro de limites saudáveis de contexto."""
        if len(self.conversation_history) > self.MAX_HISTORY_MESSAGES:
            system_msg = self.conversation_history[0]
            # Mantém os últimos 14 turnos de mensagem
            self.conversation_history = [system_msg] + self.conversation_history[-14:]

    def print_banner(self) -> None:
        """Exibe o cabeçalho inicial do assistente com as informações do sistema."""
        header_text = Text()
        header_text.append("🐧 Linux AI Assistant ", style="bold cyan")
        header_text.append("— Professor & Assistente Técnico Local\n", style="bold white")
        header_text.append(f"Ambiente: {self.context.distro_name} {self.context.distro_version} ", style="green")
        header_text.append(f"({self.context.arch}) | ", style="dim")
        header_text.append(f"Modelo: {self.client.model}", style="yellow")

        console.print(Panel(header_text, border_style="cyan", padding=(1, 2)))

    def check_ollama_status(self) -> bool:
        """Verifica se o Ollama está operacional e alerta o usuário se não estiver."""
        ok, msg = self.client.check_connection()
        if not ok:
            console.print(
                Panel(
                    f"[bold red]Aviso de Conexão com Ollama:[/bold red]\n\n{msg}\n\n"
                    "[dim]Dica: em outro terminal, execute 'ollama serve' ou inicie o serviço do Ollama.[/dim]",
                    title="⚠️  Serviço Local Offline",
                    border_style="red",
                )
            )
            return False
        return True

    def ask_streaming(self, question: str, is_explain_mode: bool = False) -> None:
        """Envia a pergunta ao modelo com memória de contexto e exibe em streaming."""
        if is_explain_mode:
            user_content = PromptBuilder.build_explain_command_prompt(question)
            title = f"🔍 Explicando comando: [bold yellow]{question}[/bold yellow]"
        else:
            user_content = question
            title = f"💡 Dúvida: [bold yellow]{question}[/bold yellow]"

        console.print()
        console.rule(title)

        # Adiciona a mensagem do usuário ao histórico da conversa
        self.conversation_history.append({"role": "user", "content": user_content})
        self._trim_history_if_needed()

        generator = self.client.stream_chat(messages=self.conversation_history)
        first_token = ""

        try:
            # Indicador de carregamento animado enquanto o modelo processa e pensa
            with console.status(
                "[bold cyan]O Professor Linux está pensando...[/bold cyan]",
                spinner="dots",
            ):
                try:
                    first_token = next(generator)
                except StopIteration:
                    first_token = ""

            full_response = first_token
            if full_response:
                with Live(Markdown(full_response), console=console, refresh_per_second=10) as live:
                    for token in generator:
                        full_response += token
                        live.update(Markdown(full_response))
            else:
                console.print("[yellow][Nenhuma resposta gerada pelo modelo][/yellow]")

            # Armazena a resposta no histórico apenas se gerou conteúdo com sucesso
            if full_response and not full_response.startswith("\n[Erro"):
                self.conversation_history.append({"role": "assistant", "content": full_response})

        except KeyboardInterrupt:
            console.print("\n[yellow][Interrompido pelo usuário][/yellow]")
        except Exception as e:
            console.print(f"\n[red]Erro durante a geração:[/red] {str(e)}")

        console.rule(style="dim")
        console.print()

    def run_interactive(self) -> None:
        """Executa o loop interativo no terminal com memória de contexto."""
        self.print_banner()
        self.check_ollama_status()

        console.print(
            "[dim]Comandos especiais: 'sair' para encerrar | 'limpar' para reiniciar o contexto | "
            "'info' para ver o sistema | 'explain <comando>' para dissecar.[/dim]\n"
        )

        while True:
            try:
                user_input = Prompt.ask("[bold green]Linux Assistant[/bold green]").strip()
            except (KeyboardInterrupt, EOFError):
                console.print("\n[cyan]Até logo! Bons estudos no Linux.[/cyan]")
                break

            if not user_input:
                continue

            lower_cmd = user_input.lower()
            if lower_cmd in ["sair", "exit", "quit", "q"]:
                console.print("[cyan]Até logo! Bons estudos no Linux.[/cyan]")
                break
            elif lower_cmd in ["limpar", "clear", "reset"]:
                self.reset_conversation()
                console.print("[cyan]🧹 Histórico da conversa limpo! Iniciando um novo contexto.[/cyan]\n")
                continue
            elif lower_cmd == "info":
                turns = (len(self.conversation_history) - 1) // 2
                ctx_summary = self.context.to_prompt_context() + f"\n- Turnos de conversa memorizados: {max(0, turns)}"
                console.print(Panel(ctx_summary, title="🖥️  Contexto do Sistema e Sessão", border_style="green"))
                continue
            elif lower_cmd.startswith("explain "):
                target_cmd = user_input[8:].strip()
                if target_cmd:
                    self.ask_streaming(target_cmd, is_explain_mode=True)
                else:
                    console.print("[yellow]Informe o comando a ser explicado. Ex: explain tar -xvf arquivo.tar.gz[/yellow]")
                continue
            elif lower_cmd in ["ajuda", "help", "?"]:
                console.print(
                    "[bold]Como usar:[/bold]\n"
                    "- Digite qualquer dúvida sobre Linux (o assistente lembra do contexto anterior!)\n"
                    "- Use [italic]'explain <comando>'[/italic] para entender detalhadamente um comando\n"
                    "- Digite [italic]'limpar'[/italic] para esquecer a conversa anterior e começar um novo assunto\n"
                    "- Digite [italic]'info'[/italic] para checar a detecção do seu sistema e histórico\n"
                    "- Digite [italic]'sair'[/italic] para encerrar."
                )
                continue

            self.ask_streaming(user_input)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Linux AI Assistant — Assistente de comandos e professor Linux local."
    )
    parser.add_argument(
        "query",
        nargs="*",
        help="Pergunta direta ou comando para ser respondido imediatamente.",
    )
    parser.add_argument(
        "--model",
        "-m",
        default="qwen2.5:7b",
        help="Modelo do Ollama a ser utilizado (padrão: qwen2.5:7b).",
    )
    parser.add_argument(
        "--explain",
        "-e",
        action="store_true",
        help="Modo focado em dissecar e explicar os parâmetros do comando informado.",
    )

    args = parser.parse_args()
    cli = LinuxAssistantCLI(model=args.model)

    if args.query:
        question = " ".join(args.query)
        cli.print_banner()
        cli.check_ollama_status()
        cli.ask_streaming(question, is_explain_mode=args.explain)
    else:
        cli.run_interactive()


if __name__ == "__main__":
    main()
