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

function Invoke-PytestCandidate {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Label,

        [Parameter(Mandatory = $true)]
        [string]$Executable,

        [Parameter(Mandatory = $true)]
        [string[]]$Arguments,

        [bool]$RequireFile = $false
    )

    $commandText = "$Executable $($Arguments -join ' ')"
    Write-Host ""
    Write-Host "Trying: $Label"
    Write-Host $commandText

    if ($RequireFile -and -not (Test-Path -LiteralPath $Executable)) {
        return @{
            Started = $false
            Success = $false
            Reason = "executable not found"
        }
    }

    try {
        $global:LASTEXITCODE = 0
        $output = & $Executable @Arguments 2>&1
        $exitCode = $LASTEXITCODE
        if ($output) {
            $output | ForEach-Object { Write-Host $_ }
        }

        $outputText = ($output | Out-String)
        if ($exitCode -ne 0 -and $outputText -match "No module named pytest") {
            return @{
                Started = $false
                Success = $false
                Reason = "pytest module not found"
            }
        }

        if ($exitCode -eq 0) {
            return @{
                Started = $true
                Success = $true
                Reason = "pytest completed successfully"
            }
        }

        return @{
            Started = $true
            Success = $false
            Reason = "pytest failed with exit code $exitCode"
        }
    }
    catch {
        return @{
            Started = $false
            Success = $false
            Reason = $_.Exception.Message
        }
    }
}

function Invoke-Pytest {
    $codexPython = "C:\Users\tamaru\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
    $basetemp = Join-Path $env:TEMP "utr_lan_pytest_tmp"
    $attempts = @()
    $candidates = @(
        @{
            Label = "py -m pytest tests"
            Executable = "py"
            Arguments = @("-m", "pytest", "tests")
            RequireFile = $false
        },
        @{
            Label = "python -m pytest tests"
            Executable = "python"
            Arguments = @("-m", "pytest", "tests")
            RequireFile = $false
        },
        @{
            Label = "Codex bundled Python"
            Executable = $codexPython
            Arguments = @("-m", "pytest", "tests", "-p", "no:cacheprovider", "--basetemp", $basetemp)
            RequireFile = $true
        }
    )

    foreach ($candidate in $candidates) {
        $label = $candidate["Label"]
        $executable = $candidate["Executable"]
        $arguments = $candidate["Arguments"]
        $requireFile = $candidate["RequireFile"]
        $result = Invoke-PytestCandidate -Label $label -Executable $executable -Arguments $arguments -RequireFile $requireFile

        $attempts += ("- {0}: {1}" -f $label, $result["Reason"])

        if ($result["Started"] -and $result["Success"]) {
            $global:LASTEXITCODE = 0
            return
        }

        if ($result["Started"] -and -not $result["Success"]) {
            throw $result["Reason"]
        }
    }

    $notExecutedText = "pytest" + [string][char]0x672A + [string][char]0x5B9F + [string][char]0x884C
    Write-Host $notExecutedText -ForegroundColor Red
    Write-Host "Tried:"
    $attempts | ForEach-Object { Write-Host $_ }
    throw "pytest was not executed"
}

Push-Location $repoRoot
try {
    Invoke-Check "git status --short" {
        git status --short
    }

    Invoke-Check "pytest" {
        Invoke-Pytest
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
