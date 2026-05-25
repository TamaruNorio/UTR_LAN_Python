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
    Invoke-Check "git status --short" {
        git status --short
    }

    Invoke-Check "py -m pytest tests" {
        py -m pytest tests
    }

    $scanScript = Join-Path $PSScriptRoot ("sec" + "ret_scan.ps1")
    Invoke-Check "blocked text scan" {
        & $scanScript
    }

    Write-Host ""
    Write-Host "== .gitignore check =="
    $gitignore = Join-Path $repoRoot ".gitignore"
    if (-not (Test-Path -LiteralPath $gitignore)) {
        Write-Host "ERROR: .gitignore was not found." -ForegroundColor Red
        $failed = $true
    }
    else {
        $ignored = Get-Content -LiteralPath $gitignore |
            ForEach-Object { $_.Trim() } |
            Where-Object { $_ -eq "logs/real_device/" }

        if ($ignored) {
            Write-Host "logs/real_device/ is ignored."
        }
        else {
            Write-Host "ERROR: logs/real_device/ is not listed in .gitignore." -ForegroundColor Red
            $failed = $true
        }
    }
}
finally {
    Pop-Location
}

if ($failed) {
    Write-Host "ERROR: dev_check failed." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "dev_check passed."
exit 0
