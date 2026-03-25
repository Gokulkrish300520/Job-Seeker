import os
import sys
import json
import importlib.util
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.9 or higher."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        return True, f"Python {version.major}.{version.minor}.{version.micro} ✅"
    return False, f"Python {version.major}.{version.minor}.{version.micro} ❌ (requires 3.9+)"

def check_env_file():
    """Check if .env file exists."""
    if os.path.exists('.env'):
        return True, ".env file exists "
    return False, "Neither .env  found "

def check_dependencies():
    """Check if all required Python packages are installed."""
    required = ['requests', 'feedparser', 'apscheduler', 'dotenv']
    missing = []
    
    for package in required:
        try:
            if package == 'dotenv':
                importlib.import_module('dotenv')
            else:
                importlib.import_module(package)
        except ImportError:
            missing.append(package)
    
    if not missing:
        return True, f"All dependencies installed "
    return False, f"Missing packages: {', '.join(missing)} (run: pip install -r requirements.txt)"

def check_config_file():
    """Check if config.py is valid and can be imported."""
    try:
        spec = importlib.util.spec_from_file_location("config", "config.py")
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        
        # Check for required attributes
        required_attrs = ['JSEARCH_API_KEY', 'ADZUNA_APP_ID', 'ADZUNA_APP_KEY', 'QUERIES', 'LINKEDIN_RSS_FEEDS']
        missing_attrs = [attr for attr in required_attrs if not hasattr(config, attr)]
        
        if missing_attrs:
            return False, f"config.py missing: {', '.join(missing_attrs)} "
        return True, "config.py valid "
    except Exception as e:
        return False, f"Error loading config.py: {str(e)} "

def check_api_credentials():
    """Check if API credentials are configured."""
    try:
        spec = importlib.util.spec_from_file_location("config", "config.py")
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        
        issues = []
        
        # Check for placeholder/default values
        if config.JSEARCH_API_KEY.startswith("ad780d51"):
            issues.append("JSEARCH_API_KEY appears to be default")
        if config.ADZUNA_APP_ID == "d5cccb0a":
            issues.append("ADZUNA_APP_ID appears to be default")
        if config.ADZUNA_APP_KEY == "82fd07c6c040c9a4145ef1efa3e2d738":
            issues.append("ADZUNA_APP_KEY appears to be default")
        
        if issues:
            return False, f"⚠️ Check credentials: {', '.join(issues)}"
        return True, "API credentials configured "
    except Exception as e:
        return False, f"Error checking credentials: {str(e)} "

def check_main_file():
    """Check if main.py is valid and can be imported."""
    try:
        spec = importlib.util.spec_from_file_location("main", "main.py")
        main = importlib.util.module_from_spec(spec)
        
        # Check for required functions before executing
        with open('main.py', 'r') as f:
            content = f.read()
            required_functions = ['load_seen_jobs', 'save_seen_jobs', 'is_relevant', 'get_all_jobs', 'print_jobs']
            missing = [func for func in required_functions if f'def {func}(' not in content]
            
            if missing:
                return False, f"main.py missing functions: {', '.join(missing)} "
            
            if '--scheduler' in content and 'BackgroundScheduler' in content:
                return True, "main.py has scheduler support "
            else:
                return False, "main.py missing scheduler support "
    except Exception as e:
        return False, f"Error checking main.py: {str(e)} "

def check_scheduler_file():
    """Check if scheduler.py exists and is valid."""
    if not os.path.exists('scheduler.py'):
        return False, "scheduler.py not found "
    
    try:
        with open('scheduler.py', 'r') as f:
            content = f.read()
            if 'BackgroundScheduler' in content and 'start_scheduler' in content:
                return True, "scheduler.py valid "
            else:
                return False, "scheduler.py incomplete "
    except Exception as e:
        return False, f"Error reading scheduler.py: {str(e)} "

def check_docker_files():
    """Check if Docker files exist."""
    dockerfile = os.path.exists('Dockerfile')
    compose = os.path.exists('docker-compose.yml')
    
    if dockerfile and compose:
        return True, "Docker files present (Dockerfile + docker-compose.yml) "
    elif dockerfile:
        return False, "Missing docker-compose.yml "
    elif compose:
        return False, "Missing Dockerfile "
    else:
        return False, "Docker files not configured "

def check_systemd_file():
    """Check if systemd service file exists."""
    if os.path.exists('job-fetcher.service'):
        return True, "systemd service file present "
    return False, "systemd service file not configured "

def check_documentation():
    """Check if documentation files exist."""
    docs = ['README.md', 'QUICKSTART.md', 'DEPLOYMENT.md']
    missing = [doc for doc in docs if not os.path.exists(doc)]
    
    if not missing:
        return True, "All documentation files present "
    return False, f"Missing documentation: {', '.join(missing)}"

def check_gitignore():
    """Check if .gitignore is configured properly."""
    if not os.path.exists('.gitignore'):
        return False, ".gitignore not configured "
    
    with open('.gitignore', 'r') as f:
        content = f.read()
        if '.env' in content and '*.log' in content:
            return True, ".gitignore properly configured "
        return False, ".gitignore missing important entries "

def check_seen_json():
    """Check if seen.json exists and is valid."""
    if not os.path.exists('seen.json'):
        return True, "seen.json not created yet (will be created on first run) ✅"
    
    try:
        with open('seen.json', 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                return True, f"seen.json valid ({len(data)} jobs tracked) "
            return False, "seen.json format invalid "
    except json.JSONDecodeError:
        return False, "seen.json corrupted "
    except Exception as e:
        return False, f"Error reading seen.json: {str(e)} "

def main():
    """Run all checks and display results."""
    print("="*70)
    print(" JOB FETCHER - PRODUCTION READINESS CHECK")
    print("="*70)
    print()
    
    checks = [
        ("Environment", [
            ("Python Version", check_python_version),
            (".env Configuration", check_env_file),
            ("Dependencies", check_dependencies),
            ("API Credentials", check_api_credentials),
        ]),
        ("Application Code", [
            ("config.py", check_config_file),
            ("main.py", check_main_file),
            ("scheduler.py", check_scheduler_file),
        ]),
        ("Deployment", [
            ("Docker Files", check_docker_files),
            ("Systemd Service", check_systemd_file),
            ("Documentation", check_documentation),
            (".gitignore", check_gitignore),
        ]),
        ("Data & Logs", [
            ("seen.json", check_seen_json),
        ]),
    ]
    
    total_checks = 0
    passed_checks = 0
    warnings = 0
    
    for section_name, section_checks in checks:
        print(f"\n📋 {section_name}")
        print("-" * 70)
        
        for check_name, check_func in section_checks:
            try:
                passed, message = check_func()
                total_checks += 1
                
                if passed:
                    passed_checks += 1
                elif "⚠️" in message:
                    warnings += 1
                
                print(f"  {check_name:<30} {message}")
            except Exception as e:
                total_checks += 1
                print(f"  {check_name:<30} Error: {str(e)} ")
    
    # Summary
    print()
    print("="*70)
    print(" SUMMARY")
    print("="*70)
    
    status = "READY FOR PRODUCTION" if (passed_checks == total_checks) else \
            " MOSTLY READY (Review Warnings)" if (warnings == total_checks - passed_checks) else \
            " NOT READY (Fix Issues)"
    
    print(f"Status: {status}")
    print(f"Passed: {passed_checks}/{total_checks}")
    print()
    
    if passed_checks < total_checks:
        print("Next Steps:")
        print("1. Review items marked with  or ")
        print("2. Follow instructions in QUICKSTART.md or README.md")
        print("3. Re-run this script to verify fixes")
        print()
    
    if passed_checks == total_checks:
        print("✅ All checks passed! You're ready to deploy.")
        print()
        print("Quick start:")
        print("  • Development: python main.py")
        print("  • Production:  python main.py --scheduler")
        print("  • Docker:      docker-compose up -d")
        print()
    
    return 0 if passed_checks == total_checks else 1

if __name__ == "__main__":
    sys.exit(main())
