# Build.ps1 for clean FSGithubPNG

# Default option is to run build, like a Makefile
param(
    [string]$Task = "build"
)

$buildFSGithubPNG = {
    Write-Host "正在打包FSGithubPNG..."
    python -m nuitka --show-progress --assume-yes-for-downloads app.py
}

$cleanFSGithubPNG = {
    Write-Host "Cleaning..."
    Remove-Item -Recurse -Force app.exe, ./app.build/, ./app.dist/, ./app.onefile-build/ ,/build/ ,/dist/ ,FSGithubPNG.spec
}

switch ($Task.ToLower()) {
    "build" {
        & $buildFSGithubPNG
        break
    }
    "clean" {
        & $cleanFSGithubPNG
        break
    }
    default {
        Write-Host "Unknown task: $Task" -ForegroundColor Red
        Write-Host "Available tasks: build, clean"
        break
    }
}