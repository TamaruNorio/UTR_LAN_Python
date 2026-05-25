param(
    [string]$OutputPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$body = @'
## Summary

-

## Test

- [ ] `.\scripts\dev_check.ps1`
- [ ] pytest completed
- [ ] blocked text scan completed
- [ ] `logs/real_device/` ignore check completed

## Safety

- [ ] No real device communication
- [ ] `real_device_check.py` not executed
- [ ] `logs/real_device/` is excluded from Git
- [ ] `git push` not executed
- [ ] PR creation and merge are manual

## Notes

-
'@

if ($OutputPath) {
    $parent = Split-Path -Parent $OutputPath
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        Write-Error "Output directory does not exist: $parent"
        exit 1
    }

    Set-Content -LiteralPath $OutputPath -Value $body -Encoding UTF8
    Write-Host "PR body template written to: $OutputPath"
    exit 0
}

Write-Output $body
exit 0
