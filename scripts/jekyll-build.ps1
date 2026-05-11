<# .SYNOPSIS
    Jekyll site build — replaces jekyll-docker.yml.

    Prerequisites: Docker.
    Usage:
      pwsh -File scripts/jekyll-build.ps1
#>
$ErrorActionPreference = "Stop"
Set-Location C:\Users\hgeec\github\symphonix-health-docs

Write-Host "[INFO] Building Jekyll site in Docker..."
docker run --rm `
    -v "${PWD}:/srv/jekyll" `
    -v "${PWD}/_site:/srv/jekyll/_site" `
    jekyll/builder:latest `
    jekyll build --future

if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] Jekyll build failed"
    exit 1
}

Write-Host "[OK] Jekyll build complete. Output in: _site/"
