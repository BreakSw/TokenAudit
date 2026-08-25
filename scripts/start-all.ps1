param(
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$envFile = Join-Path $projectRoot ".env"
if (-not (Test-Path -LiteralPath $envFile -PathType Leaf)) {
    throw "Missing $envFile. Copy .env.example to .env and configure it first."
}

$runtimePython = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $runtimePython -PathType Leaf)) {
    $configuredPython = Get-Content -LiteralPath $envFile |
        Where-Object { $_ -match '^\s*PYTHON_EXECUTABLE\s*=' } |
        Select-Object -Last 1
    if ($configuredPython) {
        $runtimePython = ($configuredPython -split '=', 2)[1].Trim().Trim('"').Trim("'")
    } else {
        $runtimePython = (Get-Command "python.exe" -ErrorAction Stop).Source
    }
}
$mavenCommand = (Get-Command "mvn.cmd" -ErrorAction Stop).Source
$npmCommand = (Get-Command "npm.cmd" -ErrorAction Stop).Source

$knowledgeArgs = @(
    "-m", "tokenaudit_knowledge.server",
    "--env-file", $envFile,
    "--host", "127.0.0.1",
    "--port", "8091"
)
$knowledge = Start-Process -FilePath $runtimePython -ArgumentList $knowledgeArgs -WorkingDirectory (Join-Path $projectRoot "knowledge-service") -WindowStyle Hidden -PassThru
$backend = Start-Process -FilePath $mavenCommand -ArgumentList @("spring-boot:run") -WorkingDirectory (Join-Path $projectRoot "back-end") -WindowStyle Hidden -PassThru
$frontend = Start-Process -FilePath $npmCommand -ArgumentList @("run", "dev", "--", "--host", "127.0.0.1") -WorkingDirectory (Join-Path $projectRoot "front-end") -WindowStyle Hidden -PassThru

[PSCustomObject]@{
    KnowledgePid = $knowledge.Id
    BackendPid = $backend.Id
    FrontendPid = $frontend.Id
    FrontendUrl = "http://127.0.0.1:5173"
    BackendUrl = "http://127.0.0.1:8086"
    KnowledgeUrl = "http://127.0.0.1:8091/health"
}

if (-not $NoBrowser) {
    Start-Process "http://127.0.0.1:5173"
}
