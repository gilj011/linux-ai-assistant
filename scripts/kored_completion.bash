#!/usr/bin/env bash
# Autocompletar Bash para o utilitario kored

_kored_completions() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    opts="--help -h --model -m --mode -M --assisted -a --continue -c --session --sessions --config --fix -f --explain -e --diag -d --service -s --audit"
    subcmds="fix"

    case "${prev}" in
        --mode|-M)
            COMPREPLY=( $(compgen -W "readonly assisted" -- "${cur}") )
            return 0
            ;;
        --service|-s)
            local services
            services=$(systemctl list-unit-files --type=service --no-legend 2>/dev/null | awk '{print $1}')
            COMPREPLY=( $(compgen -W "${services}" -- "${cur}") )
            return 0
            ;;
        --model|-m)
            local models
            models=$(ollama list 2>/dev/null | awk 'NR>1 {print $1}')
            COMPREPLY=( $(compgen -W "${models}" -- "${cur}") )
            return 0
            ;;
        *)
            ;;
    esac

    if [[ "${cur}" == -* ]]; then
        COMPREPLY=( $(compgen -W "${opts}" -- "${cur}") )
        return 0
    fi
}

complete -F _kored_completions kored
