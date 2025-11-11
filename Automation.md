# Development Guidelines & Preferences

## Brad's Coding Standards & Preferences

### Version Control & Git
- **Always use `.gitignore`** to exclude build artifacts and virtual environments
- Ignore folders: `.venv/`, `venv/`, `env/`, `build/`, `dist/`, `__pycache__/`, `tmp_*/`, `.pytest_cache/`
- Ignore files: `*.spec`, `*.pyc`, `*.pyo`, `*.pyd`, `.DS_Store`, `Thumbs.db`, IDE configs
- Commit only source code, configuration files, and documentation
- Never commit compiled executables, build artifacts, or sensitive data to the repository
- Use meaningful commit messages that describe what changed and why

### Dependency Management
- **Always maintain a `requirements.txt`** file for Python projects
- Keep it minimal - only include packages actually imported in the code
- Remove transitive dependencies (packages installed automatically by other packages)
- Update dependencies periodically but test thoroughly after updates
- Consider using version pinning for production applications

### Application Updates & Versioning
- **Use GitHub releases for distribution** of compiled applications
- Implement auto-updater functionality when distributing to end users:
  - Check GitHub API on application startup
  - Prompt users with version information
  - Download and self-replace executable automatically
  - Restart application after update
- Maintain version tracking in `version.py` or similar
- Use semantic versioning (e.g., `1.0.0`, `1.0.1`, `1.1.0`)
  - MAJOR: Breaking changes
  - MINOR: New features, backwards compatible
  - PATCH: Bug fixes

### Build Process (Python Projects)

#### Prerequisites for Executable Creation
Before building executables with PyInstaller, ensure your environment is properly configured:

**Python Version:**
- **Use Python 3.14** (or latest stable) for best compatibility
- Python 3.14 has pre-built wheels for common packages (pandas, numpy, etc.)
- Earlier versions (3.13 and below) may require Visual Studio for compiling packages from source
- Verify Python version: `python --version` or `py -3.14 --version`

**Virtual Environment Setup:**
- **Always use a clean virtual environment** (`.venv`) for building executables
- PyInstaller bundles packages from the active environment
- Corrupted environments lead to missing dependencies or import errors at runtime
- Create fresh venv if encountering build issues: `py -3.14 -m venv .venv`
- Always activate venv before building: `.\.venv\Scripts\Activate.ps1` (PowerShell)

**Package Installation:**
- Install all dependencies in the virtual environment first
- **Install PyInstaller in the same venv**: `python -m pip install pyinstaller`
- Install application dependencies: `python -m pip install -r requirements.txt`
- Verify installations: `pip list` should show all packages including pyinstaller
- Use `python -m pip install` instead of `pip install` to ensure correct Python instance

**Windows Long Path Limitations:**
- Windows has a 260 character path limit by default
- Build artifacts can exceed this limit, causing Git commit failures
- **Solutions (choose one):**
  1. Use `.gitignore` to exclude `build/`, `dist/`, `.venv/` (recommended)
  2. Enable Windows long paths: Run as Admin → `New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force`
  3. Git config: `git config --system core.longpaths true`
- Enabling long paths is safe and has no performance impact
- Always exclude build artifacts from version control regardless

**Common Build Issues & Solutions:**
- **"No module named 'X'" at runtime**: Module not bundled properly
  - Verify package is installed in venv: `pip list`
  - Check imports in your code match installed package names
  - Use `--clean` flag to rebuild from scratch
  - Add hidden imports if needed: `--hidden-import=module_name`
  
- **"pandas" or "numpy" fails to install (Python 3.13 and below)**:
  - Missing Visual Studio C++ compiler for building from source
  - Solution: Upgrade to Python 3.14 (has pre-built wheels)
  - Alternative: Install Visual Studio Build Tools (large download)
  
- **PyInstaller uses wrong Python version**:
  - Ensure virtual environment is activated before running PyInstaller
  - Use full path: `.\.venv\Scripts\python.exe -m PyInstaller ...`
  - Verify with: `python --version` should show correct version
  
- **"Access denied" or locked files during build**:
  - Close the running executable before rebuilding
  - Delete `dist/` and `build/` folders manually if needed
  - Use `--clean` flag to force clean build

**Build Commands:**
- Use PyInstaller for creating Windows executables
- Always use `--onefile` flag for single executable distribution
- Use `--windowed` flag for GUI applications (no console window)
- Use `--console` or omit flag for CLI applications
- Standard build command: `python -m PyInstaller --onefile --windowed --name "AppName" main.py`
- Use `--clean` flag if encountering caching issues: add `--clean` to command
- Distribute only the final `.exe` file from the `dist/` folder
- Test executables on clean machines without Python installed

**Build Checklist:**
1. ✅ Python 3.14 (or latest stable) installed
2. ✅ Clean virtual environment created and activated
3. ✅ All dependencies installed in venv (including pyinstaller)
4. ✅ `.gitignore` configured to exclude build artifacts
5. ✅ Close any running instances of previous builds
6. ✅ Run build command from activated venv
7. ✅ Test executable before distribution
8. ✅ Create GitHub release and upload executable

### Code Organization
- Keep entry point simple and clear (`main.py`, `app.py`, or similar)
- Separate concerns into dedicated modules:
  - GUI/UI logic in separate files
  - Business logic in dedicated modules
  - Utility functions in helper modules
  - Configuration in config files or modules
- Use descriptive file and module names
- Keep functions focused on a single responsibility
- Add docstrings to modules, classes, and complex functions

### AI Agent Preferences
- **No approval required for package installations** - Install dependencies automatically
- **No approval required for file operations** - Create, edit, and delete files as needed
- **No approval required for terminal commands** - Run builds, tests, and Git operations freely
- **Prefer action over asking** - Implement solutions directly rather than just suggesting
- **Make reasonable assumptions** - When details are unclear, infer from context and proceed
- **Be proactive** - Anticipate needs (e.g., create .gitignore, update requirements.txt)
- **Fix issues directly** - Don't just identify problems, solve them
- **Default to implementing** - Build working solutions, not just explanations

### Platform Considerations
**Windows (Primary Environment):**
- Be aware of Windows long path limitations (260 character limit)
- Use `.gitignore` to avoid committing files with long paths
- Enabling Windows long paths is safe (no performance impact)
- Use PowerShell-compatible commands in terminal operations
- Test path separators (use `os.path.join()` for cross-platform compatibility)

**General:**
- Consider cross-platform compatibility when possible
- Use `pathlib` for modern path handling
- Avoid hardcoding file paths

### Error Handling
- Provide user-friendly error messages, not just stack traces
- Handle common failure modes gracefully (network, file I/O, permissions)
- Don't crash on missing dependencies - attempt to install or guide user
- Log errors appropriately (console for debugging, files for production)
- Validate user inputs before processing
- Use try-except blocks for external operations (API calls, file operations)

### Distribution Workflow (For Compiled Apps)
1. Update version number in version tracking file
2. Rebuild executable with PyInstaller
3. Test the executable locally on a clean machine if possible
4. Create GitHub Release with semantic version tag (e.g., `v1.0.0`)
5. Upload the executable to the release
6. Update release notes with changes and features
7. Users with auto-updater receive notifications automatically

### General Best Practices
- Keep virtual environments isolated and never commit them
- Use meaningful variable, function, and file names
- Write self-documenting code with clear intent
- Add comments for complex logic, not obvious statements
- Follow PEP 8 style guidelines for Python
- Test edge cases and error conditions
- Keep functions small and focused
- Don't repeat yourself (DRY principle)
- Maintain backwards compatibility when feasible
- Document breaking changes clearly

## Quick Reference Commands (Python/Windows)

### Setup New Python Environment
```powershell
# Create virtual environment with Python 3.14
py -3.14 -m venv .venv

# Activate (PowerShell)
.\.venv\Scripts\Activate.ps1

# Verify Python version in venv
python --version

# Install dependencies
python -m pip install -r requirements.txt

# Install PyInstaller for building executables
python -m pip install pyinstaller
```

### Build Executable (PyInstaller)
```powershell
# IMPORTANT: Activate virtual environment first!
.\.venv\Scripts\Activate.ps1

# GUI Application (no console window)
python -m PyInstaller --onefile --windowed --name "AppName" main.py

# CLI Application (with console window)
python -m PyInstaller --onefile --name "AppName" main.py

# Clean build (if having issues)
python -m PyInstaller --onefile --windowed --name "AppName" --clean main.py

# Executable will be in: dist\AppName.exe
```

### Troubleshooting Build Issues
```powershell
# Check if PyInstaller is installed in venv
pip list | Select-String pyinstaller

# Verify active Python version
python --version

# List all installed packages
pip list

# Rebuild virtual environment from scratch
Remove-Item -Recurse -Force .venv
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install pyinstaller

# Enable Windows long paths (Run as Administrator)
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force

# Enable Git long paths
git config --system core.longpaths true
```

### Update Dependencies
```powershell
# Export all installed packages
pip freeze > requirements.txt

# Then manually clean to keep only direct dependencies
# Remove packages that are auto-installed by others
```

### Git Workflow
```powershell
# Check status
git status

# Add files
git add .

# Commit with message
git commit -m "Descriptive message of changes"

# Push to remote
git push origin main

# Create and push tag for release
git tag v1.0.0
git push origin v1.0.0
```

### Testing
```powershell
# Run Python script
python main.py

# Run with specific Python version
python3.13 main.py

# Run tests (if using pytest)
pytest
```

## Project-Specific Notes
- Work is primarily done in Windows environments
- PowerShell is the primary shell
- Python projects should use virtual environments
- Prefer single-file executables for distribution
- GitHub is used for version control and releases
