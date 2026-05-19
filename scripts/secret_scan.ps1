Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$allowedExtensions = @(
    ".md",
    ".py",
    ".ps1",
    ".txt",
    ".yml",
    ".yaml",
    ".json",
    ".toml"
)
$allowedNames = @(
    ".gitignore",
    ".gitattributes"
)
$excludedDirs = @(
    ".git",
    "logs",
    "__pycache__",
    ".pytest_cache"
)
$terms = @(
    ("10" + "." + "26" + "."),
    ("Client" + "Socket"),
    ("pass" + "word"),
    ("sec" + "ret"),
    ("to" + "ken"),
    ("api" + "key"),
    ("api" + "_key")
)
$pattern = ($terms | ForEach-Object { [regex]::Escape($_) }) -join "|"
$found = $false

function Get-RepoRelativePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $rootPath = $repoRoot.ProviderPath.TrimEnd("\", "/") + [System.IO.Path]::DirectorySeparatorChar
    $rootUri = [System.Uri]::new($rootPath)
    $pathUri = [System.Uri]::new($Path)
    return [System.Uri]::UnescapeDataString($rootUri.MakeRelativeUri($pathUri).ToString()).Replace("/", [System.IO.Path]::DirectorySeparatorChar)
}

Get-ChildItem -LiteralPath $repoRoot -Recurse -File -Force -ErrorAction SilentlyContinue |
    Where-Object {
        $file = $_
        $relative = Get-RepoRelativePath -Path $file.FullName
        $parts = $relative -split "[\\/]+"

        foreach ($dir in $excludedDirs) {
            if ($parts -contains $dir) {
                return $false
            }
        }

        $extension = $file.Extension.ToLowerInvariant()
        return ($allowedExtensions -contains $extension) -or ($allowedNames -contains $file.Name)
    } |
    ForEach-Object {
        $file = $_
        $matches = Select-String -LiteralPath $file.FullName -Pattern $pattern
        foreach ($match in $matches) {
            $found = $true
            $relative = Get-RepoRelativePath -Path $file.FullName
            Write-Host ("{0}:{1}: {2}" -f $relative, $match.LineNumber, $match.Line.Trim())
        }
    }

if ($found) {
    Write-Error "Blocked text was found."
    exit 1
}

Write-Host "No blocked text found."
exit 0
