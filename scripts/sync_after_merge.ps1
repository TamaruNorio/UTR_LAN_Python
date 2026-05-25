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

if ($Branch -eq "main") {
    Write-Host "ERROR: Refusing to delete main." -ForegroundColor Red
    exit 1
}

Push-Location $repoRoot
try {
    Write-Host "Branch to delete locally: $Branch"
    Write-Host "This uses git branch -d only. It will not delete the branch on GitHub."
    $answer = Read-Host "Type YES to checkout main, pull, delete the local branch, and run dev_check"
    if ($answer -ne "YES") {
        Write-Host "Canceled."
        exit 1
    }

    Invoke-Step "checkout main" {
        git checkout main
    }

    Invoke-Step "git pull" {
        git pull
    }

    git show-ref --verify --quiet "refs/heads/$Branch"
    if ($LASTEXITCODE -eq 0) {
        Invoke-Step "delete local branch $Branch" {
            git branch -d $Branch
        }
    }
    else {
        Write-Host ""
        Write-Host "== delete local branch $Branch =="
        Write-Host "Local branch already deleted. Skipping branch delete."
    }

    $devCheckScript = Join-Path $PSScriptRoot "dev_check.ps1"
    Invoke-Step "dev_check.ps1" {
        & $devCheckScript
    }
}
finally {
    Pop-Location
}
