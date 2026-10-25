# ---------------------------------------------------------------------------
# File     : vlsit_find_python.ps1
# Function : find a working Python 3 on Windows or install one with the user's agreement
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
<#
.SYNOPSIS
    Find a working Python 3 (3.8 or later) on this machine, or install one.

.DESCRIPTION
    Prints the full path of a working python.exe and exits 0. When none is found
    it prints "NOT FOUND" and exits 3.

    A plain "python --version" is not a reliable test on Windows: the "python"
    on PATH is often the Microsoft Store shortcut, which prints an error instead
    of running Python, and a python.org install is often not on PATH at all. So
    this script tries, in order:
      1. the py launcher (py -3)
      2. python and python3 on PATH
      3. the default install folders (per user, Program Files)
    and accepts a candidate only when it really runs and reports 3.8 or later.

    -Install runs winget to install Python for the user. Use it only after the
    user has agreed. It does nothing when a working Python already exists. After
    an install it searches again, so the new Python is found even though the
    PATH of the running session has not been refreshed.

    Exit codes: 0 found, 3 not found, 4 install failed.

    This file is intentionally ASCII-only so that Windows PowerShell 5.1 parses
    it the same way on every machine. It is the one script that is not Python,
    because it must work before Python exists.

.EXAMPLE
    .\vlsit_find_python.ps1
    .\vlsit_find_python.ps1 -Install
#>
[CmdletBinding()]
param(
    # install Python with winget when none is found (ask the user first)
    [switch]$Install,

    # winget package to install
    [string]$WingetId = 'Python.Python.3.13'
)

$ErrorActionPreference = 'Continue'

function Test-Python {
    param([string]$Exe, [string[]]$ExtraArgs)
    try {
        $code = "import sys; print(sys.executable + '|' + str(sys.version_info[0]) + '.' + str(sys.version_info[1]))"
        $out = & $Exe @ExtraArgs -c $code 2>$null
        if ($LASTEXITCODE -ne 0 -or -not $out) { return $null }
        $parts = ($out | Select-Object -First 1).ToString().Trim().Split('|')
        if ($parts.Count -ne 2) { return $null }
        $version = [version]$parts[1]
        if ($version.Major -ne 3 -or $version.Minor -lt 8) { return $null }
        if (-not (Test-Path -LiteralPath $parts[0])) { return $null }
        return $parts[0]
    }
    catch { return $null }
}

function Find-Python {
    $found = Test-Python 'py' @('-3')
    if ($found) { return $found }
    foreach ($name in @('python', 'python3')) {
        $found = Test-Python $name @()
        if ($found) { return $found }
    }
    $bases = @("$env:LOCALAPPDATA\Programs\Python", $env:ProgramFiles, ${env:ProgramFiles(x86)})
    foreach ($base in $bases) {
        if (-not $base -or -not (Test-Path -LiteralPath $base)) { continue }
        $launcher = Join-Path $base 'Launcher\py.exe'
        if (Test-Path -LiteralPath $launcher) {
            $found = Test-Python $launcher @('-3')
            if ($found) { return $found }
        }
        foreach ($dir in (Get-ChildItem -LiteralPath $base -Directory -Filter 'Python3*' -ErrorAction SilentlyContinue | Sort-Object Name -Descending)) {
            $exe = Join-Path $dir.FullName 'python.exe'
            if (Test-Path -LiteralPath $exe) {
                $found = Test-Python $exe @()
                if ($found) { return $found }
            }
        }
    }
    return $null
}

$python = Find-Python
if ($python) { Write-Output $python; exit 0 }

if (-not $Install) {
    Write-Output 'NOT FOUND: no working Python 3.8 or later was found.'
    Write-Output 'Ask the user to install it from https://www.python.org/downloads/ or, if they agree, run this script again with -Install.'
    exit 3
}

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Output 'NOT FOUND: winget is not available, so Python cannot be installed automatically.'
    Write-Output 'Ask the user to install Python 3 from https://www.python.org/downloads/ and run this script again.'
    exit 3
}

Write-Output "Installing $WingetId with winget (the installer may ask for approval)..."
& winget install --id $WingetId --exact --accept-source-agreements --accept-package-agreements
$installCode = $LASTEXITCODE

$python = Find-Python
if ($python) { Write-Output $python; exit 0 }
Write-Output "INSTALL FAILED: winget exit code $installCode, and no working Python was found afterwards."
exit 4
