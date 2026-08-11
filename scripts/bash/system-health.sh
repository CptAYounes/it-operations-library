#!/usr/bin/env bash
# Summarise local Linux health without changing system state.

set -uo pipefail

usage() {
    printf 'Usage: %s [--disk-warning PERCENT] [--memory-warning PERCENT]\n' "${0##*/}"
}

is_percent() {
    [[ $1 =~ ^[0-9]+$ ]] && ((1 <= 10#$1 && 10#$1 <= 100))
}

disk_warning=90
memory_warning=90

while (($#)); do
    case $1 in
        --disk-warning|--memory-warning)
            option=$1
            shift
            if (($# == 0)) || ! is_percent "$1"; then
                printf 'Error: %s requires an integer from 1 to 100.\n' "$option" >&2
                usage >&2
                exit 2
            fi
            if [[ $option == --disk-warning ]]; then
                disk_warning=$((10#$1))
            else
                memory_warning=$((10#$1))
            fi
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            printf 'Error: unknown argument: %s\n' "$1" >&2
            usage >&2
            exit 2
            ;;
    esac
    shift
done

status=healthy
incomplete=0

printf 'Host: %s\n' "$(hostname 2>/dev/null || printf 'unknown')"

if [[ -r /proc/uptime ]]; then
    read -r uptime_seconds _ < /proc/uptime
    uptime_seconds=${uptime_seconds%%.*}
    printf 'Uptime: %dd %02dh %02dm\n' \
        "$((uptime_seconds / 86400))" \
        "$(((uptime_seconds % 86400) / 3600))" \
        "$(((uptime_seconds % 3600) / 60))"
else
    printf 'Uptime: unavailable\n'
    incomplete=1
fi

if [[ -r /proc/loadavg ]]; then
    read -r load_1 load_5 load_15 _ < /proc/loadavg
    printf 'Load average (1/5/15m): %s %s %s\n' "$load_1" "$load_5" "$load_15"
else
    printf 'Load average: unavailable\n'
    incomplete=1
fi

memory_total_kib=''
memory_available_kib=''
if [[ -r /proc/meminfo ]]; then
    while read -r key value _; do
        case $key in
            MemTotal:) memory_total_kib=$value ;;
            MemAvailable:) memory_available_kib=$value ;;
        esac
    done < /proc/meminfo
fi

if [[ $memory_total_kib =~ ^[0-9]+$ && $memory_available_kib =~ ^[0-9]+$ && $memory_total_kib -gt 0 ]]; then
    memory_used_percent=$(((memory_total_kib - memory_available_kib) * 100 / memory_total_kib))
    printf 'Memory used: %d%% (warning at %d%%)\n' "$memory_used_percent" "$memory_warning"
    if ((memory_used_percent >= memory_warning)); then
        status=warning
    fi
else
    printf 'Memory used: unavailable\n'
    incomplete=1
fi

if command -v df >/dev/null 2>&1; then
    if ! disk_percent=$(LC_ALL=C df -P / 2>/dev/null | awk 'NR == 2 {gsub(/%/, "", $5); print $5}'); then
        printf 'Disk / used: unavailable (df query failed)\n'
        incomplete=1
    elif [[ $disk_percent =~ ^[0-9]+$ ]] && ((10#$disk_percent <= 100)); then
        disk_percent_value=$((10#$disk_percent))
        printf 'Disk / used: %d%% (warning at %d%%)\n' "$disk_percent_value" "$disk_warning"
        if ((disk_percent_value >= disk_warning)); then
            status=warning
        fi
    else
        printf 'Disk / used: unavailable\n'
        incomplete=1
    fi
else
    printf 'Disk / used: unavailable (df not found)\n'
    incomplete=1
fi

if command -v systemctl >/dev/null 2>&1 && [[ -d /run/systemd/system ]]; then
    if failed_services=$(systemctl --failed --type=service --no-legend --plain --no-pager 2>/dev/null); then
        if [[ -n $failed_services ]]; then
            failed_count=$(printf '%s\n' "$failed_services" | wc -l)
            printf 'Failed systemd services: %d\n' "$failed_count"
            status=warning
        else
            printf 'Failed systemd services: 0\n'
        fi
    else
        printf 'Failed systemd services: unavailable (systemctl query failed)\n'
        incomplete=1
    fi
else
    printf 'Failed systemd services: unavailable (systemd is not active)\n'
    incomplete=1
fi

if command -v ip >/dev/null 2>&1; then
    if link_output=$(ip -brief link show up 2>/dev/null); then
        up_interfaces=$(awk '$1 != "lo" {count++} END {print count + 0}' <<< "$link_output")
        printf 'Non-loopback interfaces administratively up: %d (inventory only; carrier state not evaluated)\n' "$up_interfaces"
    else
        printf 'Non-loopback interfaces administratively up: unavailable (ip query failed)\n'
        incomplete=1
    fi
else
    printf 'Non-loopback interfaces administratively up: unavailable (ip not found)\n'
    incomplete=1
fi

if ((incomplete)); then
    printf 'Status: %s (one or more checks unavailable)\n' "$status"
    exit 2
fi

printf 'Status: %s\n' "$status"
[[ $status == healthy ]]
