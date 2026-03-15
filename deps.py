import sys
import subprocess

def check_and_install(package):
    """Checks if a package is installed and installs it if not."""
    try:
        __import__(package)
    except ImportError:
        print(f"Required package '{package}' not found. Attempting to install...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"Successfully installed '{package}'.")
        except subprocess.CalledProcessError:
            print(f"Standard install failed (likely an externally managed environment). Trying with --break-system-packages...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--break-system-packages"])
                print(f"Successfully installed '{package}'.")
            except subprocess.CalledProcessError:
                print(f"ERROR: Failed to install '{package}'.")
                print(f"Please install it manually and run the script again.")
                sys.exit(1)