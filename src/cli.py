"""
Interface de Linha de Comando (CLI) interativa do Linux AI Assistant.
Apresenta respostas didáticas em tempo real com streaming e destaque de sintaxe.
"""

import argparse
from pathlib import Path
import sys
from typing import Optional

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
    """Controlador da interface de terminal do assistente."""

    def __init__(self, model: str = "qwen2.5:7b", base_url: Optional[str] = None):
        self.context: SystemContext = OSInspector.get_system_context()
        self.client = OllamaClient(base_url=base_url, model=model)
        self.system_prompt = PromptBuilder.build_system_prompt(self.context)

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
        """Envia a pergunta ao modelo e exibe a resposta formatada em tempo real."""
        if is_explain_mode:
            user_prompt = PromptBuilder.build_explain_command_prompt(question)
            title = f"🔍 Explicando comando: [bold yellow]{question}[/bold yellow]"
        else:
            user_prompt = question
            title = f"💡 Dúvida: [bold yellow]{question}[/bold yellow]"

        console.print()
        console.rule(title)

        full_response = ""
        try:
            with Live(Markdown(""), console=console, refresh_per_second=10) as live:
                for token in self.client.stream_generate(
                    prompt=user_prompt,
                    system_prompt=self.system_prompt,
                ):
                    full_response += token
                    live.update(Markdown(full_response))
        except KeyboardInterrupt:
            console.print("\n[yellow][Interrompido pelo usuário][/yellow]")
        console.rule(style="dim")
        console.print()

    def run_interactive(self) -> None:
        """Executa o loop interativo no terminal."""
        self.print_banner()
        self.check_ollama_status()

        console.print(
            "[dim]Comandos especiais: 'sair' para encerrar | 'info' para ver o sistema | "
            "'explain <comando>' para dissecar um comando.[/dim]\n"
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
            elif lower_cmd == "info":
                console.print(Panel(self.context.to_prompt_context(), title="🖥️  Contexto do Sistema", border_style="green"))
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
                    "- Digite qualquer dúvida sobre Linux (ex: [italic]'como ver portas abertas'[/italic])\n"
                    "- Use [italic]'explain <comando>'[/italic] para entender detalhadamente um comando\n"
                    "- Digite [italic]'info'[/italic] para checar a detecção do seu sistema\n"
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
