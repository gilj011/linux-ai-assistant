"""
Interface de Linha de Comando (CLI) do kored — Linux Systems Intelligence.
Suporta modos Somente Leitura e Assistido com autorizacao explicita de acoes, auditoria e sessoes persistentes.
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
from rich.table import Table
from rich.text import Text

from src.action_parser import ActionParser, ProposedAction
from src.config import KoredConfig
from src.diagnostics import DiagnosticEngine, DiagnosticReport
from src.executor import ControlledExecutor, ExecutionMode
from src.ollama_client import OllamaClient
from src.os_inspector import OSInspector, SystemContext
from src.prompt_builder import PromptBuilder
from src.session_manager import SessionData, SessionManager

console = Console()


class KoredCLI:
    """Controlador da interface de terminal do kored com chave seletora, auditoria e sessoes."""

    def __init__(
        self,
        model: Optional[str] = None,
        mode: Optional[ExecutionMode] = None,
        base_url: Optional[str] = None,
        audit_dir: Optional[Path] = None,
        sessions_dir: Optional[Path] = None,
        config: Optional[KoredConfig] = None,
        session_id: Optional[str] = None,
        resume_latest: bool = False,
    ):
        self.config = config or KoredConfig.load()
        self.context: SystemContext = OSInspector.get_system_context()

        # Determina o modelo ativo (prioridade: argumento explicito > config > default)
        active_model = model or self.config.model

        # Determina o modo ativo
        if mode is not None:
            self.mode = mode
        else:
            self.mode = ExecutionMode.ASSISTED if self.config.default_mode == "assisted" else ExecutionMode.READONLY

        active_base_url = base_url or self.config.ollama_host

        self.client = OllamaClient(base_url=active_base_url, model=active_model, timeout=self.config.timeout)
        self.executor = ControlledExecutor(audit_dir=audit_dir)
        self.session_manager = SessionManager(sessions_dir=sessions_dir)
        self.system_prompt = PromptBuilder.build_system_prompt(self.context, mode=self.mode)

        self.current_session: Optional[SessionData] = None
        self.conversation_history: List[Dict[str, str]] = []

        if resume_latest:
            latest = self.session_manager.get_latest_session()
            if latest:
                self._load_existing_session(latest)
            else:
                self.reset_conversation()
        elif session_id:
            target = self.session_manager.load_session(session_id)
            if target:
                self._load_existing_session(target)
            else:
                self.reset_conversation()
        else:
            self.reset_conversation()

    def _load_existing_session(self, session: SessionData) -> None:
        """Carrega dados e historico de uma sessao salva."""
        self.current_session = session
        self.conversation_history = list(session.messages)

        # Garante que o prompt de sistema esteja atualizado com o contexto e modo atual
        if self.conversation_history and self.conversation_history[0]["role"] == "system":
            self.conversation_history[0]["content"] = self.system_prompt
        else:
            self.conversation_history.insert(0, {"role": "system", "content": self.system_prompt})

    def _sync_session(self) -> None:
        """Sincroniza o estado atual da conversa no arquivo da sessao."""
        if self.current_session:
            self.current_session.messages = list(self.conversation_history)
            self.current_session.mode = self.mode.value
            self.current_session.model = self.client.model
            self.session_manager.save_session(self.current_session)

    def set_mode(self, new_mode: ExecutionMode) -> None:
        """Altera a chave seletora de modo e atualiza o prompt do sistema."""
        self.mode = new_mode
        self.system_prompt = PromptBuilder.build_system_prompt(self.context, mode=self.mode)
        if self.conversation_history and self.conversation_history[0]["role"] == "system":
            self.conversation_history[0]["content"] = self.system_prompt

        self._sync_session()
        mode_name = "ASSISTIDO (Aprovacao Explicita)" if self.mode == ExecutionMode.ASSISTED else "SEGURO (Somente Leitura)"
        console.print(f"[bold cyan]Chave Seletora alterada para:[/bold cyan] [bold yellow]{mode_name}[/bold yellow]\n")

    def reset_conversation(self, title: str = "Nova sessao", save_now: bool = False) -> None:
        """Reinicia o historico da conversa e prepara uma nova sessao."""
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]
        self.current_session = self.session_manager.create_session(
            mode=self.mode.value,
            model=self.client.model,
            system_prompt=self.system_prompt,
            title=title,
            save_now=save_now,
        )

    def _trim_history_if_needed(self) -> None:
        """Mantem o historico dentro de limites saudaveis de contexto."""
        limit = self.config.history_limit
        if len(self.conversation_history) > limit:
            system_msg = self.conversation_history[0]
            slice_size = max(4, limit - 5)
            self.conversation_history = [system_msg] + self.conversation_history[-slice_size:]

    def print_banner(self) -> None:
        """Exibe o cabecalho tecnico do kored com as informacoes do sistema, modo e sessao."""
        mode_label = "ASSISTIDO [Aprovacao Humana]" if self.mode == ExecutionMode.ASSISTED else "SEGURO [Somente Leitura]"
        mode_style = "bold yellow" if self.mode == ExecutionMode.ASSISTED else "bold green"

        session_label = self.current_session.id if self.current_session else "ativa"

        header_text = Text()
        header_text.append("kored ", style="bold cyan")
        header_text.append("— Linux Systems Intelligence & Assistant\n", style="bold white")
        header_text.append(f"Host: {self.context.distro_name} {self.context.distro_version} ", style="green")
        header_text.append(f"(Kernel {self.context.kernel} / {self.context.arch})\n", style="dim")
        header_text.append("Modo: ", style="dim")
        header_text.append(mode_label, style=mode_style)
        header_text.append(" | Modelo: ", style="dim")
        header_text.append(f"{self.client.model}", style="yellow")
        header_text.append(" | Sessao: ", style="dim")
        header_text.append(session_label, style="cyan")

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

    def show_audit_history(self, limit: int = 15) -> None:
        """Exibe o registro tabular das acoes de auditoria realizadas."""
        actions = self.executor.audit_logger.get_recent_actions(limit=limit)
        if not actions:
            console.print(Panel("Nenhum registro de auditoria encontrado ate o momento.", title="Auditoria kored", border_style="cyan"))
            return

        table = Table(title="Historico de Auditoria e Acoes", border_style="cyan", header_style="bold cyan")
        table.add_column("Data/Hora", style="dim", no_wrap=True)
        table.add_column("Tipo", style="white")
        table.add_column("Alvo / Comando", style="yellow")
        table.add_column("Aprovado", style="magenta")
        table.add_column("Status", style="green")

        for act in actions:
            approved_text = "Sim" if act.get("user_approved") else "Nao"
            status = act.get("status", "")
            status_style = "green" if "SUCESSO" in status else "red" if "FALHA" in status or "BLOQUEADO" in status else "yellow"
            
            target = act.get("target", "")
            if len(target) > 40:
                target = target[:37] + "..."

            table.add_row(
                act.get("timestamp", ""),
                act.get("action_type", ""),
                target,
                approved_text,
                f"[{status_style}]{status}[/{status_style}]",
            )

        console.print(table)
        console.print(f"[dim]Arquivo de auditoria: {self.executor.audit_logger.audit_file}[/dim]\n")

    def show_sessions(self, limit: int = 10) -> None:
        """Exibe tabela com as sessoes gravadas recentemente."""
        sessions = self.session_manager.list_sessions(limit=limit)
        if not sessions:
            console.print(Panel("Nenhuma sessao gravada encontrada ate o momento.", title="Sessoes kored", border_style="cyan"))
            return

        table = Table(title="Historico de Sessoes do kored", border_style="cyan", header_style="bold cyan")
        table.add_column("ID da Sessao", style="yellow", no_wrap=True)
        table.add_column("Ultima Atividade", style="dim")
        table.add_column("Modo", style="magenta")
        table.add_column("Turnos", justify="right", style="green")
        table.add_column("Titulo / Resumo", style="white")

        for s in sessions:
            updated_display = s["updated_at"][:19].replace("T", " ") if s.get("updated_at") else ""
            table.add_row(
                s["id"],
                updated_display,
                s["mode"].upper(),
                str(s["turns"]),
                s["title"],
            )

        console.print(table)
        console.print(f"[dim]Diretorio de sessoes: {self.session_manager.sessions_dir}[/dim]")
        console.print("[dim]Para retomar uma sessao: kored --session <ID> ou kored -c (para a mais recente)[/dim]\n")

    def show_config(self) -> None:
        """Exibe as configuracoes ativas e o caminho do arquivo."""
        cfg_dict = self.config.to_dict()
        table = Table(
            title="kored :: Parametros de Configuracao Ativos",
            border_style="cyan",
            header_style="bold cyan",
        )
        table.add_column("Parametro", style="bold yellow")
        table.add_column("Valor Ativo", style="green")

        for k, v in cfg_dict.items():
            table.add_row(k, str(v))

        console.print(table)
        console.print(f"[dim]Arquivo de configuracao: {self.config.default_config_path()}[/dim]\n")

    def _handle_proposed_actions(self, full_response: str) -> None:
        """Analisa respostas em busca de acoes propostas e gerencia a autorizacao do usuario."""
        actions = ActionParser.extract_actions(full_response)
        if not actions:
            return

        if self.mode == ExecutionMode.READONLY:
            console.print(
                Panel(
                    "O kored sugeriu uma acao de sistema, mas o modo ativo e 'SEGURO (Somente Leitura)'.\n"
                    "Nenhuma alteracao sera realizada. Para autorizar acoes sob aprovacao, mude para 'modo assistido'.",
                    title="Acao Nao Executada [Modo Somente Leitura]",
                    border_style="yellow",
                )
            )
            return

        for action in actions:
            console.print(
                Panel(
                    action.summary(),
                    title="[AUTORIZACAO EXPLICITA REQUERIDA] Proposta de Acao do kored",
                    border_style="bold yellow",
                )
            )

            try:
                confirmation = Prompt.ask(
                    "[bold yellow]Deseja que o kored execute esta acao no sistema? [s/N][/bold yellow]"
                ).strip().lower()
            except (KeyboardInterrupt, EOFError):
                confirmation = "n"

            target_desc = action.path if action.action_type == "write_file" else (action.command or "")

            if confirmation in ["s", "sim", "y", "yes"]:
                if action.action_type == "write_file" and action.path:
                    ok, msg = self.executor.write_file(action.path, action.content or "")
                    if ok:
                        console.print(f"[bold green][SUCESSO][/bold green] {msg}\n")
                        self.conversation_history.append({"role": "system", "content": f"[Acao executada com sucesso]: {msg}"})
                    else:
                        console.print(f"[bold red][FALHA][/bold red] {msg}\n")
                elif action.action_type == "run_command" and action.command:
                    console.print(f"[dim]Executando: {action.command}...[/dim]")
                    ok, msg = self.executor.execute_command(action.command)
                    if ok:
                        console.print(Panel(msg, title=f"Saida: {action.command}", border_style="green"))
                        self.conversation_history.append({"role": "system", "content": f"[Comando executado]: {msg}"})
                    else:
                        console.print(Panel(msg, title="Erro na execucao do comando", border_style="red"))
            else:
                self.executor.audit_logger.log_action(action.action_type, target_desc, "CANCELADO_PELO_USUARIO", user_approved=False)
                console.print("[dim]Acao cancelada pelo usuario. Nada foi alterado no sistema.[/dim]\n")
                self.conversation_history.append({"role": "system", "content": "[Acao cancelada pelo usuario]"})

        self._sync_session()

    def ask_streaming(self, question: str, is_explain_mode: bool = False) -> None:
        """Processa a consulta com streaming, memoria de contexto e deteccao de acoes."""
        if is_explain_mode:
            user_content = PromptBuilder.build_explain_command_prompt(question)
            title = f"[bold cyan]kored[/bold cyan] :: Inspecao de comando: [bold yellow]{question}[/bold yellow]"
        else:
            user_content = question
            title = f"[bold cyan]kored[/bold cyan] :: Interacao: [bold yellow]{question}[/bold yellow]"

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
                with Live(Markdown(ActionParser.strip_action_blocks(full_response)), console=console, refresh_per_second=10) as live:
                    for token in generator:
                        full_response += token
                        clean_text = ActionParser.strip_action_blocks(full_response)
                        live.update(Markdown(clean_text or full_response))
            else:
                console.print("[yellow][Nenhuma resposta gerada pelo modelo][/yellow]")

            if full_response and not full_response.startswith("\n[Erro"):
                self.conversation_history.append({"role": "assistant", "content": full_response})
                self._handle_proposed_actions(full_response)
                self._sync_session()

        except KeyboardInterrupt:
            console.print("\n[yellow][Interrompido][/yellow]")
        except Exception as e:
            console.print(f"\n[red]Erro durante a geracao:[/red] {str(e)}")

        console.rule(style="dim")
        console.print()

    def run_diagnostics(self, service_name: Optional[str] = None, user_notes: str = "") -> None:
        """Executa sondas no sistema, persiste evidencias e aciona o motor analitico."""
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
        
        # Salva copia do relatorio no historico de auditoria
        saved_file = self.executor.audit_logger.save_diagnostic_report(report.target, report.to_prompt_context())

        summary_lines = [
            f"Alvo inspecionado: {target_desc}",
            f"Sondas executadas: {len(report.results)}"
        ]
        if saved_file:
            summary_lines.append(f"Relatorio persistido em: {saved_file}")

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
                with Live(Markdown(ActionParser.strip_action_blocks(full_response)), console=console, refresh_per_second=10) as live:
                    for token in generator:
                        full_response += token
                        live.update(Markdown(ActionParser.strip_action_blocks(full_response)))
            else:
                console.print("[yellow][Nenhum diagnostico gerado pelo modelo][/yellow]")

            if full_response and not full_response.startswith("\n[Erro"):
                self.conversation_history.append({"role": "assistant", "content": full_response})
                self._handle_proposed_actions(full_response)
                self._sync_session()

        except KeyboardInterrupt:
            console.print("\n[yellow][Interrompido][/yellow]")
        except Exception as e:
            console.print(f"\n[red]Erro durante a analise diagnostica:[/red] {str(e)}")

        console.rule(style="dim")
        console.print()

    def run_interactive(self) -> None:
        """Executa a sessao interativa do kored."""
        if self.config.clear_on_start:
            console.clear()

        self.print_banner()
        self.check_ollama_status()

        console.print(
            "[dim]Comandos: 'sair' | 'modo [seguro|assistido]' | 'sessoes' | 'nova' | 'diag' | 'historico' | 'limpar' | 'info' | 'config'.[/dim]\n"
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
                if self.config.clear_on_start:
                    console.clear()
                self.print_banner()
                console.print("[cyan]Contexto e tela reiniciados (nova sessao criada).[/cyan]\n")
                continue
            elif lower_cmd in ["nova", "new"]:
                self.reset_conversation()
                console.print(f"[cyan]Nova sessao iniciada: [bold yellow]{self.current_session.id}[/bold yellow][/cyan]\n")
                continue
            elif lower_cmd in ["sessoes", "sessions"]:
                self.show_sessions()
                continue
            elif lower_cmd.startswith("retomar ") or lower_cmd.startswith("resume "):
                target_id = user_input.split(maxsplit=1)[1].strip()
                target_sess = self.session_manager.load_session(target_id)
                if target_sess:
                    self._load_existing_session(target_sess)
                    console.print(f"[cyan]Sessao retomada com sucesso: [bold yellow]{target_id}[/bold yellow][/cyan]\n")
                else:
                    console.print(f"[red]Sessao '{target_id}' nao encontrada.[/red]\n")
                continue
            elif lower_cmd in ["config", "configuracao"]:
                self.show_config()
                continue
            elif lower_cmd in ["modo", "mode"]:
                new_mode = ExecutionMode.ASSISTED if self.mode == ExecutionMode.READONLY else ExecutionMode.READONLY
                self.set_mode(new_mode)
                continue
            elif lower_cmd in ["modo seguro", "modo readonly", "safe"]:
                self.set_mode(ExecutionMode.READONLY)
                continue
            elif lower_cmd in ["modo assistido", "modo exec", "assist"]:
                self.set_mode(ExecutionMode.ASSISTED)
                continue
            elif lower_cmd in ["historico", "audit", "logs"]:
                self.show_audit_history()
                continue
            elif lower_cmd == "info":
                turns = (len(self.conversation_history) - 1) // 2
                sess_id = self.current_session.id if self.current_session else "nenhuma"
                ctx_summary = (
                    self.context.to_prompt_context() +
                    f"\n- Modo Operacional: {self.mode.value.upper()}" +
                    f"\n- Sessao Ativa: {sess_id}" +
                    f"\n- Turnos de contexto ativos: {max(0, turns)}" +
                    f"\n- Auditoria: {self.executor.audit_logger.audit_file}" +
                    f"\n- Configuracao: {self.config.default_config_path()}"
                )
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
                    "- Digite consultas sobre comandos, diagnosticos ou administracao Linux\n"
                    "- [italic]'modo seguro'[/italic] / [italic]'modo assistido'[/italic]: altera chave seletora\n"
                    "- [italic]'sessoes'[/italic]: lista o historico de sessoes anteriores\n"
                    "- [italic]'retomar <id>'[/italic]: alterna para uma sessao anterior\n"
                    "- [italic]'nova'[/italic]: cria uma nova sessao de conversa zerada\n"
                    "- [italic]'diag'[/italic]: varredura diagnostica de saude do sistema\n"
                    "- [italic]'diag <servico>'[/italic]: diagnostica servico systemd (ex: diag nginx)\n"
                    "- [italic]'historico'[/italic]: exibe tabela de auditoria de acoes executadas\n"
                    "- [italic]'config'[/italic]: visualiza os parametros de configuracao ativos\n"
                    "- [italic]'limpar'[/italic]: limpa a tela e reinicia o contexto\n"
                    "- [italic]'info'[/italic]: dados da distro, kernel, sessao e caminhos locais\n"
                    "- [italic]'sair'[/italic]: encerra o programa."
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
        help="Modelo Ollama a ser utilizado (padrao: definido em config.yaml ou qwen2.5:7b).",
    )
    parser.add_argument(
        "--mode",
        "-M",
        choices=["readonly", "assisted"],
        help="Chave seletora de modo: 'readonly' (modo seguro) ou 'assisted' (permite acoes com aprovacao).",
    )
    parser.add_argument(
        "--assisted",
        "-a",
        action="store_true",
        help="Atalho para iniciar diretamente em modo assistido com aprovacao humana.",
    )
    parser.add_argument(
        "--continue",
        "-c",
        dest="resume_latest",
        action="store_true",
        help="Retoma a sessao de conversa mais recente gravada em disco.",
    )
    parser.add_argument(
        "--session",
        help="Retoma uma sessao especifica pelo seu ID.",
    )
    parser.add_argument(
        "--sessions",
        action="store_true",
        help="Lista as sessoes de conversa gravadas recentemente e sai.",
    )
    parser.add_argument(
        "--config",
        action="store_true",
        help="Exibe os parametros de configuracao ativos e sai.",
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
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Exibe os registros recentes de auditoria de operacoes e sai.",
    )

    args = parser.parse_args()

    # Carrega configuracao persistente
    cfg = KoredConfig.load()

    # Modo selecionado
    selected_mode = None
    if args.assisted:
        selected_mode = ExecutionMode.ASSISTED
    elif args.mode:
        selected_mode = ExecutionMode.ASSISTED if args.mode == "assisted" else ExecutionMode.READONLY

    cli = KoredCLI(
        model=args.model,
        mode=selected_mode,
        config=cfg,
        session_id=args.session,
        resume_latest=args.resume_latest,
    )

    if args.config:
        cli.show_config()
    elif args.sessions:
        cli.show_sessions()
    elif args.audit:
        cli.show_audit_history()
    elif args.diag or args.service:
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
