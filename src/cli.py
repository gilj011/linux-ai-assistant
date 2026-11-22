"""
Interface de Linha de Comando (CLI) do kored — Linux Systems Intelligence.
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


class KoredCLI:
    """Controlador da interface de terminal do kored."""

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
            self.conversation_history = [system_msg] + self.conversation_history[-14:]

    def print_banner(self) -> None:
        """Exibe o cabeçalho técnico do kored com as informações do sistema."""
        header_text = Text()
        header_text.append("⚡ kored ", style="bold cyan")
        header_text.append("— Linux Systems Intelligence & Assistant\n", style="bold white")
        header_text.append(f"Host: {self.context.distro_name} {self.context.distro_version} ", style="green")
        header_text.append(f"(Kernel {self.context.kernel} / {self.context.arch}) | ", style="dim")
        header_text.append(f"Model: {self.client.model}", style="yellow")

        console.print(Panel(header_text, border_style="cyan", padding=(1, 2)))

    def check_ollama_status(self) -> bool:
        """Verifica se o backend Ollama está operacional."""
        ok, msg = self.client.check_connection()
        if not ok:
            console.print(
                Panel(
                    f"[bold red]Falha na comunicação com o backend local:[/bold red]\n\n{msg}\n\n"
                    "[dim]Certifique-se de que o daemon do Ollama está em execução ('ollama serve').[/dim]",
                    title="⚠️  kored backend offline",
                    border_style="red",
                )
            )
            return False
        return True

    def ask_streaming(self, question: str, is_explain_mode: bool = False) -> None:
        """Processa a consulta com streaming e memória de contexto."""
        if is_explain_mode:
            user_content = PromptBuilder.build_explain_command_prompt(question)
            title = f"🔍 [bold cyan]kored[/bold cyan] :: Inspeção de comando: [bold yellow]{question}[/bold yellow]"
        else:
            user_content = question
            title = f"⚡ [bold cyan]kored[/bold cyan] :: Consulta: [bold yellow]{question}[/bold yellow]"

        console.print()
        console.rule(title)

        self.conversation_history.append({"role": "user", "content": user_content})
        self._trim_history_if_needed()

        generator = self.client.stream_chat(messages=self.conversation_history)
        first_token = ""

        try:
            with console.status(
                "[bold cyan]kored analisando...[/bold cyan]",
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

            if full_response and not full_response.startswith("\n[Erro"):
                self.conversation_history.append({"role": "assistant", "content": full_response})

        except KeyboardInterrupt:
            console.print("\n[yellow][Interrompido][/yellow]")
        except Exception as e:
            console.print(f"\n[red]Erro durante a geração:[/red] {str(e)}")

        console.rule(style="dim")
        console.print()

    def run_interactive(self) -> None:
        """Executa a sessão interativa do kored."""
        self.print_banner()
        self.check_ollama_status()

        console.print(
            "[dim]Comandos: 'sair' | 'limpar' (reset de contexto) | 'info' (telemetria do sistema) | 'explain <cmd>'.[/dim]\n"
        )

        while True:
            try:
                user_input = Prompt.ask("[bold cyan]kored[/bold cyan]").strip()
            except (KeyboardInterrupt, EOFError):
                console.print("\n[cyan]Sessão kored encerrada.[/cyan]")
                break

            if not user_input:
                continue

            lower_cmd = user_input.lower()
            if lower_cmd in ["sair", "exit", "quit", "q"]:
                console.print("[cyan]Sessão kored encerrada.[/cyan]")
                break
            elif lower_cmd in ["limpar", "clear", "reset"]:
                self.reset_conversation()
                console.print("[cyan]🧹 Contexto da sessão reiniciado.[/cyan]\n")
                continue
            elif lower_cmd == "info":
                turns = (len(self.conversation_history) - 1) // 2
                ctx_summary = self.context.to_prompt_context() + f"\n- Turnos de contexto ativos: {max(0, turns)}"
                console.print(Panel(ctx_summary, title="🖥️  kored :: Informações do Ambiente", border_style="green"))
                continue
            elif lower_cmd.startswith("explain "):
                target_cmd = user_input[8:].strip()
                if target_cmd:
                    self.ask_streaming(target_cmd, is_explain_mode=True)
                else:
                    console.print("[yellow]Informe o comando para análise. Ex: explain ss -tulnp[/yellow]")
                continue
            elif lower_cmd in ["ajuda", "help", "?"]:
                console.print(
                    "[bold]Instruções de uso do kored:[/bold]\n"
                    "- Digite consultas sobre comandos, diagnósticos, serviços ou arquitetura Linux\n"
                    "- Use [italic]'explain <comando>'[/italic] para dissecar parâmetros e mecânica\n"
                    "- Digite [italic]'limpar'[/italic] para reiniciar a memória da conversa\n"
                    "- Digite [italic]'info'[/italic] para telemetria da distro e kernel\n"
                    "- Digite [italic]'sair'[/italic] para finalizar."
                )
                continue

            self.ask_streaming(user_input)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="kored — Linux Systems Intelligence & Assistant."
    )
    parser.add_argument(
        "query",
        nargs="*",
        help="Consulta direta ou comando para ser respondido imediatamente.",
    )
    parser.add_argument(
        "--model",
        "-m",
        default="qwen2.5:7b",
        help="Modelo Ollama a ser utilizado (padrão: qwen2.5:7b).",
    )
    parser.add_argument(
        "--explain",
        "-e",
        action="store_true",
        help="Modo de dissecação e análise profunda de comando.",
    )

    args = parser.parse_args()
    cli = KoredCLI(model=args.model)

    if args.query:
        question = " ".join(args.query)
        cli.print_banner()
        cli.check_ollama_status()
        cli.ask_streaming(question, is_explain_mode=args.explain)
    else:
        cli.run_interactive()


if __name__ == "__main__":
    main()
