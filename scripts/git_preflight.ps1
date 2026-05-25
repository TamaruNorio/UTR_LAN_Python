Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$failed = $false

function Invoke-Check {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Title,

        [Parameter(Mandatory = $true)]
        [scriptblock]$Command
    )

    Write-Host ""
    Write-Host "== $Title =="

    try {
        $global:LASTEXITCODE = 0
        & $Command
        if ($LASTEXITCODE -ne 0) {
            throw "Exit code $LASTEXITCODE"
        }
    }
    catch {
        Write-Host "ERROR: $Title failed: $_" -ForegroundColor Red
        $script:failed = $true
    }
}

Push-Location $repoRoot
try {
    Invoke-Check "current branch" {
        git branch --show-current
    }

    Invoke-Check "git status --short" {
        git status --short
    }

    Invoke-Check "git diff --stat" {
        git diff --stat
    }

    Invoke-Check "git log --oneline --decorate -5" {
        git log --oneline --decorate -5
    }

    $devCheckScript = Join-Path $PSScriptRoot "dev_check.ps1"
    Invoke-Check "dev_check.ps1" {
        & $devCheckScript
    }
}
finally {
    Pop-Location
}

if ($failed) {
    Write-Host "ERROR: git_preflight failed." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "git_preflight passed."
exit 0
