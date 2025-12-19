# ============================================================================
#  Audio Translator - Docker Quick Start (PowerShell)
# One-command deployment script for Windows
# ============================================================================

Write-Host "🚀  Military Audio Translator - Docker Deployment" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
try {
    docker --version | Out-Null
    Write-Host "✅ Docker is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed!" -ForegroundColor Red
    Write-Host "📥 Install Docker Desktop: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    exit 1
}

# Check if Docker Compose is installed
try {
    docker-compose --version | Out-Null
    Write-Host "✅ Docker Compose is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose is not installed!" -ForegroundColor Red
    Write-Host "📥 Usually included with Docker Desktop" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Check if .env exists, if not create from example
if (-not (Test-Path .env)) {
    Write-Host "📝 Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✅ .env file created" -ForegroundColor Green
} else {
    Write-Host "✅ .env file exists" -ForegroundColor Green
}
Write-Host ""

# Stop any existing containers
Write-Host "🛑 Stopping existing containers (if any)..." -ForegroundColor Yellow
docker-compose down
Write-Host ""

# Build and start containers
Write-Host "🔨 Building Docker images..." -ForegroundColor Yellow
docker-compose build
Write-Host ""

Write-Host "🚀 Starting services..." -ForegroundColor Yellow
docker-compose up -d
Write-Host ""

# Wait for services to start
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check if containers are running
$running = docker-compose ps | Select-String "Up"
if ($running) {
    Write-Host ""
    Write-Host "✅ Deployment successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor White
    Write-Host "🔧 Backend API: http://localhost:8000" -ForegroundColor White
    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📊 View logs: docker-compose logs -f" -ForegroundColor Yellow
    Write-Host "🛑 Stop: docker-compose down" -ForegroundColor Yellow
    Write-Host "📖 Full guide: See DOCKER.md" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "⚠️  Note: First run will download AI models (~3-4GB)" -ForegroundColor Magenta
    Write-Host "   This may take 10-15 minutes depending on your connection." -ForegroundColor Magenta
} else {
    Write-Host ""
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    Write-Host "📋 Check logs: docker-compose logs" -ForegroundColor Yellow
    exit 1
}
