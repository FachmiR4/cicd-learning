param(
    [Parameter(Mandatory=$true)][string]$Image,
    [Parameter(Mandatory=$true)][string]$ExpectedVersion,
    [string]$PythonCommand = 'python'
)
$ErrorActionPreference = 'Stop'
$savedImage = $env:APP_IMAGE
$savedFault = $env:FAIL_READY
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    $previousContainer = docker compose ps -q api
    if ($LASTEXITCODE -ne 0) { throw 'Tidak dapat membaca status Compose' }
    $previousImage = $null
    if ($previousContainer) {
        # ID lokal bersifat immutable; tag lama dapat saja telah dipindahkan.
        $previousImage = docker inspect --format '{{.Image}}' $previousContainer
        if ($LASTEXITCODE -ne 0) { throw 'Tidak dapat membaca image sebelumnya' }
    }
    $env:APP_IMAGE = $Image
    try {
        docker compose up -d --wait --wait-timeout 45
        if ($LASTEXITCODE -ne 0) { throw 'Deployment tidak healthy' }
        & $PythonCommand scripts/smoke.py http://127.0.0.1:8080 --expect-version $ExpectedVersion
        if ($LASTEXITCODE -ne 0) { throw 'Smoke test gagal' }
        Write-Host "RELEASE OK: $Image"
    } catch {
        $releaseError = $_
        docker compose logs --tail 30 api
        if ($previousImage) {
            $env:APP_IMAGE = $previousImage
            $env:FAIL_READY = '0'
            docker compose up -d --wait --wait-timeout 45
            if ($LASTEXITCODE -ne 0) { throw 'ROLLBACK FAILED: periksa Compose dan database' }
            & $PythonCommand scripts/smoke.py http://127.0.0.1:8080
            if ($LASTEXITCODE -ne 0) { throw 'ROLLBACK FAILED: verifikasi layanan gagal' }
            Write-Host "ROLLBACK OK: $previousImage"
        } else {
            Write-Warning 'Belum ada rilis sebelumnya; inspeksi rilis pertama yang gagal.'
        }
        throw $releaseError
    }
} finally {
    $env:APP_IMAGE = $savedImage
    $env:FAIL_READY = $savedFault
    Pop-Location
}
