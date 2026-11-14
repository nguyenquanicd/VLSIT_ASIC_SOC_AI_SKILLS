#!/bin/sh
# ---------------------------------------------------------------------------
# File     : vlsit_find_python.sh
# Function : find a working Python 3 (3.8 or later) on Linux or macOS, or install one
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
# vlsit_find_python.sh - find a working Python 3 (3.8 or later) on Linux or macOS, or install one.
#
# Linux twin of vlsit_find_python.ps1, with the same behavior and the same exit codes.
# Written in plain POSIX sh (no bash-isms) so it runs under dash, ash/busybox, bash,
# zsh and ksh on Debian, Ubuntu, RHEL, Rocky, Alma, Fedora, SUSE, Alpine, Arch, macOS.
#
# Usage:
#   sh vlsit_find_python.sh              print the full path of a working Python 3, exit 0
#   sh vlsit_find_python.sh --install    install Python with the system package manager
#                                  when none is found (ask the user first)
#   sh vlsit_find_python.sh --options    print the install commands for each Linux family, exit 0
#
# Exit codes: 0 found, 3 not found, 4 install failed.
#
# A candidate is accepted only when it really runs and reports 3.8 or later, so a
# stub or a Python 2 interpreter named "python" is never returned.
# This file is ASCII-only and must keep Unix (LF) line endings.

MODE="find"
case "${1:-}" in
    --install) MODE="install" ;;
    --options) MODE="options" ;;
    "") ;;
    -h|--help)
        sed -n '9,24p' "$0" | sed 's/^# \{0,1\}//'
        exit 0
        ;;
    *)
        echo "unknown option: $1 (use --install, --options or --help)" >&2
        exit 1
        ;;
esac

# Print the real path of the candidate when it runs and is Python 3.8 or later.
# Uses only shell built-ins after the interpreter call, so a reduced PATH cannot break it.
test_python() {
    candidate="$1"
    [ -n "$candidate" ] || return 1
    out=$("$candidate" -c 'import sys; print(sys.executable + "|" + ("1" if sys.version_info >= (3, 8) else "0"))' 2>/dev/null) || return 1
    exe=${out%|*}
    ok=${out##*|}
    [ "$ok" = "1" ] || return 1
    [ -n "$exe" ] && [ -x "$exe" ] || return 1
    printf '%s
' "$exe"
    return 0
}

find_python() {
    # 1. names on PATH, newest first
    for name in python3 python python3.13 python3.12 python3.11 python3.10 python3.9 python3.8; do
        path=$(command -v "$name" 2>/dev/null) || continue
        found=$(test_python "$path") && { printf '%s\n' "$found"; return 0; }
    done
    # 2. usual install folders that are not always on PATH
    for path in /usr/bin/python3 /usr/local/bin/python3 /opt/homebrew/bin/python3 \
                /opt/local/bin/python3 /usr/pkg/bin/python3 "$HOME/.local/bin/python3" \
                "$HOME/.pyenv/shims/python3" /opt/python/bin/python3 /opt/rh/rh-python38/root/usr/bin/python3; do
        [ -x "$path" ] || continue
        found=$(test_python "$path") && { printf '%s\n' "$found"; return 0; }
    done
    # 3. versioned folders (for example /opt/python3.11/bin/python3, pyenv versions)
    for path in /opt/python*/bin/python3 "$HOME"/.pyenv/versions/3*/bin/python3 /usr/local/python3*/bin/python3; do
        [ -x "$path" ] || continue
        found=$(test_python "$path") && { printf '%s\n' "$found"; return 0; }
    done
    return 1
}

# Print "<manager>|<command>" for the package manager of this system (empty if none known).
detect_installer() {
    if command -v apt-get >/dev/null 2>&1; then
        echo "apt-get|apt-get update && apt-get install -y python3"
    elif command -v dnf >/dev/null 2>&1; then
        echo "dnf|dnf install -y python3"
    elif command -v yum >/dev/null 2>&1; then
        echo "yum|yum install -y python3"
    elif command -v zypper >/dev/null 2>&1; then
        echo "zypper|zypper --non-interactive install python3"
    elif command -v apk >/dev/null 2>&1; then
        echo "apk|apk add --no-cache python3"
    elif command -v pacman >/dev/null 2>&1; then
        echo "pacman|pacman -S --noconfirm python"
    elif command -v brew >/dev/null 2>&1; then
        echo "brew|brew install python"
    fi
}

print_options() {
    echo "Install Python 3.8 or later with the package manager of this system:"
    echo "  Debian, Ubuntu            sudo apt-get update && sudo apt-get install -y python3"
    echo "  Fedora                    sudo dnf install -y python3"
    echo "  RHEL, Rocky, Alma, CentOS sudo dnf install -y python3   (or: sudo yum install -y python3)"
    echo "  openSUSE, SLES            sudo zypper install python3"
    echo "  Alpine                    sudo apk add python3"
    echo "  Arch                      sudo pacman -S python"
    echo "  macOS (Homebrew)          brew install python"
    echo "  No root access            download from https://www.python.org/downloads/ or use pyenv"
}

if [ "$MODE" = "options" ]; then
    print_options
    exit 0
fi

python=$(find_python) && { printf '%s\n' "$python"; exit 0; }

if [ "$MODE" != "install" ]; then
    echo "NOT FOUND: no working Python 3.8 or later was found."
    echo "Ask the user to install it, or, if they agree, run this script again with --install."
    echo "Run with --options to see the install command for each Linux family."
    exit 3
fi

entry=$(detect_installer)
if [ -z "$entry" ]; then
    echo "NOT FOUND: no known package manager, so Python cannot be installed automatically."
    print_options
    exit 3
fi
manager=${entry%%|*}
command_line=${entry#*|}

if [ "$(id -u 2>/dev/null)" != "0" ]; then
    if command -v sudo >/dev/null 2>&1; then
        command_line="sudo sh -c '$command_line'"
    else
        echo "NOT FOUND: installing needs root and sudo is not available."
        echo "As root, run: $command_line"
        exit 3
    fi
fi

echo "Installing Python with $manager (it may ask for your password)..."
echo "  $command_line"
sh -c "$command_line"
install_code=$?

python=$(find_python) && { printf '%s\n' "$python"; exit 0; }
echo "INSTALL FAILED: the installer exit code was $install_code, and no working Python was found afterwards."
exit 4
