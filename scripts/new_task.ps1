param(
    [Parameter(Mandatory = $true)]
    [string]$Branch
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Title,

        [Parameter(Mandatory = $true)]
        [scriptblock]$Command
    )

    Write-Host ""
    Write-Host "== $Title =="
    $global:LASTEXITCODE = 0
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Title failed with exit code $LASTEXITCODE"
    }
}

Push-Location $repoRoot
try {
    $changes = git status --porcelain
    if ($changes) {
        Write-Host "ERROR: Uncommitted changes exist. Commit or stash them before creating a new task branch." -ForegroundColor Red
        git status --short
        exit 1
    }

    git show-ref --verify --quiet "refs/heads/$Branch"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "ERROR: Branch already exists: $Branch" -ForegroundColor Red
        exit 1
    }

    Invoke-Step "checkout main" {
        git checkout main
    }

    Invoke-Step "git pull" {
        git pull
    }

    Invoke-Step "create branch $Branch" {
        git checkout -b $Branch
    }

    Write-Host ""
    Write-Host "Created and switched to branch: $Branch"
}
finally {
    Pop-Location
}
