# Virtual Environment Activation Checker
# Ensures virtual environment is always active before running Django commands

import sys
import os
import subprocess
from pathlib import Path

def check_virtual_env():
    """Check if virtual environment is active"""
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    return in_venv

def activate_virtual_env():
    """Activate virtual environment if not already active"""
    if check_virtual_env():
        print("✅ Virtual environment is already active")
        return True
    
    # Try to find and activate virtual environment
    project_root = Path(__file__).parent
    venv_paths = [
        project_root / "venv" / "Scripts" / "activate.bat",  # Windows
        project_root / "venv" / "Scripts" / "Activate.ps1",  # PowerShell
        project_root / "venv" / "bin" / "activate",  # Linux/Mac
        project_root / ".venv" / "Scripts" / "activate.bat",  # Alternative Windows
        project_root / ".venv" / "bin" / "activate",  # Alternative Linux/Mac
    ]
    
    for venv_path in venv_paths:
        if venv_path.exists():
            print(f"🔄 Activating virtual environment: {venv_path}")
            try:
                # For Windows batch files
                if venv_path.suffix == ".bat":
                    subprocess.run([str(venv_path)], shell=True, check=True)
                # For PowerShell scripts
                elif venv_path.suffix == ".ps1":
                    subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(venv_path)], check=True)
                # For Unix-like systems
                else:
                    subprocess.run(["source", str(venv_path)], shell=True, check=True)
                print("✅ Virtual environment activated successfully")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to activate virtual environment: {e}")
                continue
    
    print("❌ No virtual environment found. Please create one using:")
    print("   python -m venv venv")
    print("   # Then activate it manually")
    return False

def ensure_django_setup():
    """Ensure Django is properly configured"""
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
        import django
        django.setup()
        print("✅ Django setup completed successfully")
        return True
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return False

def run_django_command(command_args):
    """Run Django management command with virtual environment active"""
    if not check_virtual_env():
        print("❌ Virtual environment is not active!")
        print("Please activate it first:")
        print("   .\\venv\\Scripts\\Activate.ps1  # PowerShell")
        print("   .\\venv\\Scripts\\activate.bat   # Command Prompt")
        return False
    
    if not ensure_django_setup():
        return False
    
    try:
        # Run the Django command
        import subprocess
        result = subprocess.run(
            ["python", "manage.py"] + command_args,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        if result.returncode == 0:
            print("✅ Django command executed successfully")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print("❌ Django command failed")
            if result.stderr:
                print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running Django command: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Virtual Environment Status Check")
    print("=" * 40)
    
    # Check current status
    if check_virtual_env():
        print("✅ Virtual environment is ACTIVE")
        print(f"   Python path: {sys.executable}")
        
        # Test Django
        if ensure_django_setup():
            print("✅ Django is working properly")
        else:
            print("❌ Django setup issues detected")
    else:
        print("❌ Virtual environment is NOT active")
        print(f"   Current Python: {sys.executable}")
        print("\n🔧 To activate virtual environment:")
        print("   .\\venv\\Scripts\\Activate.ps1  # PowerShell")
        print("   .\\venv\\Scripts\\activate.bat   # Command Prompt")
