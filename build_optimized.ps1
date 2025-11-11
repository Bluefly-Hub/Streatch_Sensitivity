# Optimized build script to reduce executable size
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Clean previous build
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue

# Build with exclusions for packages not used by your code
python -m PyInstaller `
    --onefile `
    --windowed `
    --name "Cerberus_Streatch_Sensitivity_Automation" `
    --strip `
    --exclude-module matplotlib `
    --exclude-module IPython `
    --exclude-module pytest `
    --exclude-module sphinx `
    --exclude-module jinja2 `
    --exclude-module pip `
    --exclude-module setuptools `
    --exclude-module wheel `
    --exclude-module pygments `
    --exclude-module docutils `
    --exclude-module tornado `
    --exclude-module jupyter `
    --exclude-module notebook `
    --exclude-module ipykernel `
    --exclude-module scipy `
    --exclude-module openpyxl `
    --exclude-module xlrd `
    --exclude-module xlwt `
    --exclude-module sqlalchemy `
    --exclude-module lxml `
    --exclude-module numexpr `
    --exclude-module bottleneck `
    main.py

Write-Host "`nBuild complete! Check the dist folder for your optimized executable." -ForegroundColor Green
