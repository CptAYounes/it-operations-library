#!/usr/bin/env bash
# Check filesystem use for one or more local paths.

set -uo pipefail

usage() {
    printf 'Usage: %s [-w PERCENT] [PATH ...]\n' "${0##*/}"
    printf 'Defaults: warning threshold 90%%; path /\n'
}

warning=90
paths=()

while (($#)); do
    case $1 in
        -w|--warning)
            shift
            if (($# == 0)) || [[ ! $1 =~ ^[0-9]+$ ]] || ((10#$1 < 1 || 10#$1 > 100)); then
                printf 'Error: warning threshold must be an integer from 1 to 100.\n' >&2
                usage >&2
                exit 2
            fi
            warning=$((10#$1))
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        --)
            shift
            paths+=("$@")
            break
            ;;
        -*)
            printf 'Error: unknown option: %s\n' "$1" >&2
            usage >&2
            exit 2
            ;;
        *) paths+=("$1") ;;
    esac
    shift
done

((${#paths[@]})) || paths=(/)

if ! command -v df >/dev/null 2>&1; then
    printf 'Error: df is required.\n' >&2
    exit 2
fi

result=0
printf 'Threshold: %d%%\n' "$warning"

for path in "${paths[@]}"; do
    if [[ ! -e $path ]]; then
        printf 'Path: %s | status: unavailable (not found)\n' "$path" >&2
        result=2
        continue
    fi

    row=$(LC_ALL=C df -P -- "$path" 2>/dev/null | awk 'NR == 2 {gsub(/%/, "", $5); print $2 "\t" $3 "\t" $4 "\t" $5}')
    if [[ -z $row ]]; then
        printf 'Path: %s | status: unavailable (df failed)\n' "$path" >&2
        result=2
        continue
    fi

    IFS=$'\t' read -r total_kib used_kib available_kib used_percent <<< "$row"
    if [[ ! $used_percent =~ ^[0-9]+$ ]]; then
        printf 'Path: %s | status: unavailable (unexpected df output)\n' "$path" >&2
        result=2
        continue
    fi

    state=healthy
    if ((used_percent >= warning)); then
        state=warning
        ((result < 1)) && result=1
    fi

    printf 'Path: %s | used: %s%% | available: %s KiB | total: %s KiB | status: %s\n' \
        "$path" "$used_percent" "$available_kib" "$total_kib" "$state"
done

exit "$result"
