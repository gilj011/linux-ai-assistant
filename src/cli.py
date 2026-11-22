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

from src.diagnostics import DiagnosticEngine, DiagnosticReport
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
        """Reinicia o historico da conversa mantendo o prompt do sistema."""
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]

    def _trim_history_if_needed(self) -> None:
        """Mantem o historico dentro de limites saudaveis de contexto."""
        if len(self.conversation_history) > self.MAX_HISTORY_MESSAGES:
            system_msg = self.conversation_history[0]
            self.conversation_history = [system_msg] + self.conversation_history[-14:]

    def print_banner(self) -> None:
        """Exibe o cabecalho tecnico do kored com as informacoes do sistema."""
        header_text = Text()
        header_text.append("kored ", style="bold cyan")
        header_text.append("— Linux Systems Intelligence & Assistant\n", style="bold white")
        header_text.append(f"Host: {self.context.distro_name} {self.context.distro_version} ", style="green")
        header_text.append(f"(Kernel {self.context.kernel} / {self.context.arch}) | ", style="dim")
        header_text.append(f"Model: {self.client.model}", style="yellow")

        console.print(Panel(header_text, border_style="cyan", padding=(1, 2)))

    def check_ollama_status(self) -> bool:
        """Verifica se o backend Ollama esta operacional."""
        ok, msg = self.client.check_connection()
        if not ok:
            console.print(
                Panel(
                    f"[bold red]Falha na comunicacao com o backend local:[/bold red]\n\n{msg}\n\n"
                    "[dim]Certifique-se de que o daemon do Ollama esta em execucao ('ollama serve').[/dim]",
                    title="[Aviso] kored backend offline",
                    border_style="red",
                )
            )
            return False
        return True

    def ask_streaming(self, question: str, is_explain_mode: bool = False) -> None:
        """Processa a consulta com streaming e memoria de contexto."""
        if is_explain_mode:
            user_content = PromptBuilder.build_explain_command_prompt(question)
            title = f"[bold cyan]kored[/bold cyan] :: Inspecao de comando: [bold yellow]{question}[/bold yellow]"
        else:
            user_content = question
            title = f"[bold cyan]kored[/bold cyan] :: Consulta: [bold yellow]{question}[/bold yellow]"

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
            console.print(f"\n[red]Erro durante a geracao:[/red] {str(e)}")

        console.rule(style="dim")
        console.print()

    def run_diagnostics(self, service_name: Optional[str] = None, user_notes: str = "") -> None:
        """Executa sondas no sistema e aciona o motor de analise diagnostica da IA."""
        console.print()
        if service_name:
            target_desc = f"Servico '{service_name}'"
            title = f"[bold cyan]kored[/bold cyan] :: Diagnostico do servico: [bold yellow]{service_name}[/bold yellow]"
            with console.status(f"[bold cyan]Inspecionando {service_name}...[/bold cyan]", spinner="dots"):
                report = DiagnosticEngine.run_service_check(service_name)
        else:
            target_desc = "Saude Geral do Sistema"
            title = "[bold cyan]kored[/bold cyan] :: Diagnostico de Saude Geral do Sistema"
            with console.status("[bold cyan]Executando sondas do sistema (recursos, servicos, logs)...[/bold cyan]", spinner="dots"):
                report = DiagnosticEngine.run_health_check()

        console.rule(title)
        
        # Exibe resumo das evidencias coletadas
        summary_lines = [f"Alvo inspecionado: {target_desc}", f"Sondas executadas: {len(report.results)}"]
        for res in report.results:
            status_text = "[green]OK[/green]" if res.success else "[yellow]Aviso/Falha[/yellow]"
            summary_lines.append(f"- {res.name}: {status_text}")
        
        console.print(Panel("\n".join(summary_lines), title="Evidencias Coletadas", border_style="blue"))

        diag_prompt = PromptBuilder.build_diagnostic_prompt(
            evidences=report.to_prompt_context(),
            user_notes=user_notes,
        )

        self.conversation_history.append({"role": "user", "content": diag_prompt})
        self._trim_history_if_needed()

        generator = self.client.stream_chat(messages=self.conversation_history)
        first_token = ""

        try:
            with console.status("[bold cyan]kored correlacionando evidencias e elaborando diagnostico...[/bold cyan]", spinner="dots"):
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
                console.print("[yellow][Nenhum diagnostico gerado pelo modelo][/yellow]")

            if full_response and not full_response.startswith("\n[Erro"):
                self.conversation_history.append({"role": "assistant", "content": full_response})

        except KeyboardInterrupt:
            console.print("\n[yellow][Interrompido][/yellow]")
        except Exception as e:
            console.print(f"\n[red]Erro durante a analise diagnostica:[/red] {str(e)}")

        console.rule(style="dim")
        console.print()

    def run_interactive(self) -> None:
        """Executa a sessao interativa do kored."""
        self.print_banner()
        self.check_ollama_status()

        console.print(
            "[dim]Comandos: 'sair' | 'diag' (saude geral) | 'diag <servico>' | 'limpar' | 'info' | 'explain <cmd>'.[/dim]\n"
        )

        while True:
            try:
                user_input = Prompt.ask("[bold cyan]kored[/bold cyan]").strip()
            except (KeyboardInterrupt, EOFError):
                console.print("\n[cyan]Sessao kored encerrada.[/cyan]")
                break

            if not user_input:
                continue

            lower_cmd = user_input.lower()
            if lower_cmd in ["sair", "exit", "quit", "q"]:
                console.print("[cyan]Sessao kored encerrada.[/cyan]")
                break
            elif lower_cmd in ["limpar", "clear", "reset"]:
                self.reset_conversation()
                console.print("[cyan]Contexto da sessao reiniciado.[/cyan]\n")
                continue
            elif lower_cmd == "info":
                turns = (len(self.conversation_history) - 1) // 2
                ctx_summary = self.context.to_prompt_context() + f"\n- Turnos de contexto ativos: {max(0, turns)}"
                console.print(Panel(ctx_summary, title="kored :: Informacoes do Ambiente", border_style="green"))
                continue
            elif lower_cmd == "diag":
                self.run_diagnostics()
                continue
            elif lower_cmd.startswith("diag "):
                target_service = user_input[5:].strip()
                if target_service:
                    self.run_diagnostics(service_name=target_service)
                else:
                    self.run_diagnostics()
                continue
            elif lower_cmd.startswith("explain "):
                target_cmd = user_input[8:].strip()
                if target_cmd:
                    self.ask_streaming(target_cmd, is_explain_mode=True)
                else:
                    console.print("[yellow]Informe o comando para analise. Ex: explain ss -tulnp[/yellow]")
                continue
            elif lower_cmd in ["ajuda", "help", "?"]:
                console.print(
                    "[bold]Instrucoes de uso do kored:[/bold]\n"
                    "- Digite qualquer consulta tecnica de comandos ou administracao Linux\n"
                    "- Digite [italic]'diag'[/italic] para executar varredura diagnostica de saude do sistema\n"
                    "- Digite [italic]'diag <servico>'[/italic] para diagnosticar servico systemd (ex: diag nginx)\n"
                    "- Use [italic]'explain <comando>'[/italic] para dissecar parametros e mecanica\n"
                    "- Digite [italic]'limpar'[/italic] para reiniciar a memoria da conversa\n"
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
        help="Modelo Ollama a ser utilizado (padrao: qwen2.5:7b).",
    )
    parser.add_argument(
        "--explain",
        "-e",
        action="store_true",
        help="Modo de dissecacao e analise profunda de comando.",
    )
    parser.add_argument(
        "--diag",
        "-d",
        action="store_true",
        help="Executa varredura diagnostica e analise de saude do sistema.",
    )
    parser.add_argument(
        "--service",
        "-s",
        help="Executa diagnostico focado em um servico especifico (systemd).",
    )

    args = parser.parse_args()
    cli = KoredCLI(model=args.model)

    if args.diag or args.service:
        cli.print_banner()
        cli.check_ollama_status()
        cli.run_diagnostics(service_name=args.service)
    elif args.query:
        question = " ".join(args.query)
        cli.print_banner()
        cli.check_ollama_status()
        cli.ask_streaming(question, is_explain_mode=args.explain)
    else:
        cli.run_interactive()


if __name__ == "__main__":
    main()
