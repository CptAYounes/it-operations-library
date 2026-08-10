#!/usr/bin/env bash
# Run bounded route, name-resolution and ICMP checks for one target.

set -uo pipefail

usage() {
    printf 'Usage: %s [-t SECONDS] [TARGET]\n' "${0##*/}"
    printf 'With no target, the first IPv4 default gateway is checked.\n'
}

timeout=2
target=''

while (($#)); do
    case $1 in
        -t|--timeout)
            shift
            if (($# == 0)) || [[ ! $1 =~ ^[0-9]+$ ]] || ((10#$1 < 1 || 10#$1 > 30)); then
                printf 'Error: timeout must be an integer from 1 to 30 seconds.\n' >&2
                usage >&2
                exit 2
            fi
            timeout=$((10#$1))
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        -*)
            printf 'Error: unknown option: %s\n' "$1" >&2
            usage >&2
            exit 2
            ;;
        *)
            if [[ -n $target ]]; then
                printf 'Error: provide only one target.\n' >&2
                usage >&2
                exit 2
            fi
            target=$1
            ;;
    esac
    shift
done

for required in ip getent ping; do
    if ! command -v "$required" >/dev/null 2>&1; then
        printf 'Error: required command not found: %s\n' "$required" >&2
        exit 2
    fi
done

if [[ -z $target ]]; then
    target=$(ip -4 route show default 2>/dev/null | awk 'NR == 1 {print $3}')
    if [[ -z $target ]]; then
        printf 'Error: no target supplied and no IPv4 default gateway found.\n' >&2
        exit 2
    fi
fi

printf 'Target: %s\n' "$target"
printf 'Interfaces administratively up:\n'
ip -brief link show up 2>/dev/null | awk '{printf "  %s %s\n", $1, $2}'

resolved=$(getent ahostsv4 "$target" 2>/dev/null | awk 'NR == 1 {print $1}')
if [[ -z $resolved ]]; then
    printf 'Resolution: failed\n'
    printf 'Status: warning\n'
    exit 1
fi
printf 'Resolved IPv4: %s\n' "$resolved"

route=$(ip -4 route get "$resolved" 2>/dev/null | awk 'NR == 1 {$1=$1; print}')
if [[ -z $route ]]; then
    printf 'Route: unavailable\n'
    printf 'Status: warning\n'
    exit 1
fi
printf 'Route: %s\n' "$route"

if ping -n -c 1 -W "$timeout" -- "$resolved" >/dev/null 2>&1; then
    printf 'ICMP: reply received\n'
    printf 'Status: healthy\n'
    exit 0
fi

printf 'ICMP: no reply within %ss\n' "$timeout"
printf 'Status: warning (ICMP may be filtered even when the host is available)\n'
exit 1
