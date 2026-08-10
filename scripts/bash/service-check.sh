#!/usr/bin/env bash
# Report the load and runtime state of systemd services.

set -uo pipefail

usage() {
    printf 'Usage: %s SERVICE [SERVICE ...]\n' "${0##*/}"
    printf 'Example: %s ssh.service cron.service\n' "${0##*/}"
}

if (($# == 0)); then
    usage >&2
    exit 2
fi

if [[ $1 == -h || $1 == --help ]]; then
    usage
    exit 0
fi

if ! command -v systemctl >/dev/null 2>&1 || [[ ! -d /run/systemd/system ]]; then
    printf 'Error: an active systemd environment is required.\n' >&2
    exit 2
fi

result=0

for unit in "$@"; do
    if [[ $unit == -* || $unit == *[!A-Za-z0-9@_.:-]* ]]; then
        printf 'Service: %s | status: invalid name\n' "$unit" >&2
        result=2
        continue
    fi

    if ! properties=$(systemctl show "$unit" --no-pager \
        --property=LoadState --property=ActiveState --property=SubState 2>/dev/null); then
        printf 'Service: %s | status: unavailable (systemctl query failed)\n' "$unit" >&2
        result=2
        continue
    fi
    if [[ -z $properties ]]; then
        printf 'Service: %s | status: unavailable (empty systemctl response)\n' "$unit" >&2
        result=2
        continue
    fi

    load_state=''
    active_state=''
    sub_state=''
    while IFS='=' read -r key value; do
        case $key in
            LoadState) load_state=$value ;;
            ActiveState) active_state=$value ;;
            SubState) sub_state=$value ;;
        esac
    done <<< "$properties"

    if [[ -z $load_state || -z $active_state || -z $sub_state ]]; then
        printf 'Service: %s | status: unavailable (incomplete systemctl response)\n' "$unit" >&2
        result=2
        continue
    fi

    state=healthy
    if [[ $load_state != loaded || $active_state != active ]]; then
        state=warning
        ((result < 1)) && result=1
    fi

    printf 'Service: %s | load: %s | active: %s | sub: %s | status: %s\n' \
        "$unit" "$load_state" "$active_state" "$sub_state" "$state"
done

exit "$result"
