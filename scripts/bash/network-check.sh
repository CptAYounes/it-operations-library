#!/usr/bin/env bash
# Run route and name-resolution checks plus bounded ICMP for one target.

set -uo pipefail

usage() {
    printf 'Usage: %s [-t SECONDS] [TARGET]\n' "${0##*/}"
    printf 'With no target, the first IPv4 default gateway is checked.\n'
}

valid_ipv4() {
    local candidate=$1 octet
    local -a octets

    [[ $candidate =~ ^[0-9]{1,3}(\.[0-9]{1,3}){3}$ ]] || return 1
    IFS=. read -r -a octets <<< "$candidate"
    ((${#octets[@]} == 4)) || return 1
    for octet in "${octets[@]}"; do
        ((10#$octet <= 255)) || return 1
    done
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

for required in ip getent ping timeout; do
    if ! command -v "$required" >/dev/null 2>&1; then
        printf 'Error: required command not found: %s\n' "$required" >&2
        exit 2
    fi
done

timeout_arguments=(--signal=TERM --kill-after=1s "${timeout}s")

if [[ -z $target ]]; then
    default_routes=$(timeout "${timeout_arguments[@]}" ip -4 route show default 2>/dev/null)
    route_status=$?
    if ((route_status == 124 || route_status == 137)); then
        printf 'Error: IPv4 default-route query timed out after %ss (1s termination grace).\n' "$timeout" >&2
        exit 2
    elif ((route_status != 0)); then
        printf 'Error: IPv4 default-route query failed (status %d).\n' "$route_status" >&2
        exit 2
    fi
    target=$(awk '
        NF == 0 {next}
        $1 != "default" {invalid = 1; next}
        $1 == "default" {
            routes++
            for (field = 1; field < NF; field++) {
                if ($field == "via") {
                    gateways++
                    gateway = $(field + 1)
                }
            }
        }
        END {if (!invalid && routes == 1 && gateways == 1) print gateway}
    ' <<< "$default_routes")
    if [[ -z $target ]]; then
        printf 'Error: no target supplied and no single IPv4 default gateway was found.\n' >&2
        printf 'Supply an explicit target for on-link or multipath default routes.\n' >&2
        exit 2
    fi
    if ! valid_ipv4 "$target"; then
        printf 'Error: default-route query returned an invalid IPv4 gateway.\n' >&2
        exit 2
    fi
fi

printf 'Target: %s\n' "$target"
printf 'Interfaces administratively up:\n'
if ! link_output=$(timeout "${timeout_arguments[@]}" ip -brief link show up 2>/dev/null); then
    printf 'Interface query: unavailable\n'
    printf 'Status: incomplete\n'
    exit 2
fi
awk '{printf "  %s %s\n", $1, $2}' <<< "$link_output"

resolution_output=$(timeout "${timeout_arguments[@]}" getent ahostsv4 "$target" 2>/dev/null)
resolution_status=$?
if ((resolution_status == 124 || resolution_status == 137)); then
    printf 'Resolution: timed out after %ss (1s termination grace)\n' "$timeout"
    printf 'Status: warning\n'
    exit 1
elif ((resolution_status != 0)); then
    printf 'Resolution: failed (collector status %d)\n' "$resolution_status"
    printf 'Status: warning\n'
    exit 1
fi
resolved=$(awk 'NR == 1 {print $1}' <<< "$resolution_output")
if [[ -z $resolved ]] || ! valid_ipv4 "$resolved"; then
    printf 'Resolution: invalid IPv4 address from collector\n'
    printf 'Status: warning\n'
    exit 1
fi
printf 'Resolved IPv4: %s\n' "$resolved"

route_output=$(timeout "${timeout_arguments[@]}" ip -4 route get "$resolved" 2>/dev/null)
route_status=$?
if ((route_status == 124 || route_status == 137)); then
    printf 'Route: query timed out after %ss (1s termination grace)\n' "$timeout"
    printf 'Status: warning\n'
    exit 1
elif ((route_status != 0)); then
    printf 'Route: unavailable (collector status %d)\n' "$route_status"
    printf 'Status: warning\n'
    exit 1
fi
route=$(awk -v expected="$resolved" '
    NR == 1 {
        typed = ($1 == "local" || $1 == "broadcast" || $1 == "multicast" || $1 == "anycast" || $1 == "unicast")
        destination = ($1 == expected || (typed && $2 == expected))
        device = 0
        for (field = 1; field < NF; field++) {
            if ($field == "dev" && $(field + 1) != "") device = 1
        }
        if (destination && device) {
            $1 = $1
            print
        }
    }
' <<< "$route_output")
if [[ -z $route ]]; then
    printf 'Route: malformed collector output\n'
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
