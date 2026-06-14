$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir

Write-Host "Building project..."
dotnet build -c Debug
if ($LASTEXITCODE -ne 0) {
    Write-Error "dotnet build failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

$sourceDir = Join-Path $scriptDir 'bin\Debug\mods\mod'
$zipFile = Join-Path $scriptDir 'kemonoanimpatch.zip'

if (-Not (Test-Path $sourceDir)) {
    Write-Error "Source directory '$sourceDir' not found."
    exit 1
}

if (Test-Path $zipFile) {
    Remove-Item $zipFile -Force
}

Write-Host "Creating zip file '$zipFile' from '$sourceDir'..."
Compress-Archive -Path (Join-Path $sourceDir '*') -DestinationPath $zipFile -Force
Write-Host "Done."
