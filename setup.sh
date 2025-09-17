#!/bin/bash

# DataWipe Pro - Automated Setup Script
# Team: Tejasway
# This script automates the installation of DataWipe Pro on Ubuntu/Debian systems

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Ubuntu/Debian
check_system() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        if [[ "$ID" == "ubuntu" ]] || [[ "$ID" == "debian" ]] || [[ "$ID_LIKE" == *"ubuntu"* ]] || [[ "$ID_LIKE" == *"debian"* ]]; then
            print_success "Detected compatible system: $PRETTY_NAME"
            return 0
        fi
    fi
    print_error "This script is designed for Ubuntu/Debian systems"
    print_warning "You may need to manually install dependencies"
    return 1
}

# Function to update system packages
update_system() {
    print_status "Updating system packages..."
    sudo apt update
    print_success "System packages updated"
}

# Function to install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    local packages=(
        "python3"
        "python3-pip"
        "python3-tk"
        "python3-dev"
        "fonts-ubuntu"
        "fonts-dejavu-core"
        "fonts-liberation"
        "smartmontools"
        "hdparm"
        "nvme-cli"
        "util-linux"
    )
    
    for package in "${packages[@]}"; do
        if dpkg -l | grep -q "^ii  $package "; then
            print_success "$package is already installed"
        else
            print_status "Installing $package..."
            sudo apt install -y "$package"
        fi
    done
    
    print_success "System dependencies installed"
}

# Function to check Python version
check_python() {
    print_status "Checking Python version..."
    
    if command_exists python3; then
        local python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        local required_version="3.8"
        
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_success "Python $python_version is compatible (>= $required_version required)"
        else
            print_error "Python $python_version is too old (>= $required_version required)"
            return 1
        fi
    else
        print_error "Python 3 is not installed"
        return 1
    fi
}

# Function to install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    if [[ -f "requirements.txt" ]]; then
        # Try to install with --user first
        if pip3 install --user -r requirements.txt; then
            print_success "Python dependencies installed successfully"
        else
            print_warning "User installation failed, trying system-wide installation..."
            if sudo pip3 install -r requirements.txt; then
                print_success "Python dependencies installed system-wide"
            else
                print_error "Failed to install Python dependencies"
                return 1
            fi
        fi
    else
        print_error "requirements.txt not found"
        return 1
    fi
}

# Function to test installation
test_installation() {
    print_status "Testing installation..."
    
    # Test Python imports
    if python3 -c "import tkinter, reportlab, qrcode, psutil, cryptography; print('All imports successful')" 2>/dev/null; then
        print_success "Python dependencies test passed"
    else
        print_error "Python dependencies test failed"
        return 1
    fi
    
    # Test GUI launch (dry run)
    if python3 -c "
import sys
sys.path.append('src')
try:
    from gui import DataWipeProGUI
    print('GUI import successful')
except Exception as e:
    print(f'GUI import failed: {e}')
    sys.exit(1)
" 2>/dev/null; then
        print_success "GUI components test passed"
    else
        print_error "GUI components test failed"
        return 1
    fi
    
    # Test drive detection
    if python3 src/main.py --help >/dev/null 2>&1; then
        print_success "Main application test passed"
    else
        print_error "Main application test failed"
        return 1
    fi
}

# Function to create desktop entry
create_desktop_entry() {
    print_status "Creating desktop entry..."
    
    local desktop_dir="$HOME/.local/share/applications"
    local desktop_file="$desktop_dir/datawipe-pro.desktop"
    local current_dir=$(pwd)
    
    mkdir -p "$desktop_dir"
    
    cat > "$desktop_file" << EOF
[Desktop Entry]
Name=DataWipe Pro
Comment=Secure Data Erasure Tool
Exec=python3 $current_dir/src/main.py --gui
Path=$current_dir
Icon=drive-harddisk
Terminal=false
Type=Application
Categories=System;Security;Utility;
Keywords=wipe;secure;erase;data;drive;disk;
StartupNotify=true
EOF
    
    chmod +x "$desktop_file"
    
    # Update desktop database
    if command_exists update-desktop-database; then
        update-desktop-database "$desktop_dir" 2>/dev/null || true
    fi
    
    print_success "Desktop entry created"
}

# Function to create symbolic link
create_symlink() {
    print_status "Creating system-wide command link..."
    
    local current_dir=$(pwd)
    local link_target="/usr/local/bin/datawipe-pro"
    
    if [[ -L "$link_target" ]]; then
        print_warning "Symbolic link already exists, removing old link"
        sudo rm "$link_target"
    fi
    
    # Create wrapper script
    local wrapper_script="/tmp/datawipe-pro-wrapper"
    cat > "$wrapper_script" << EOF
#!/bin/bash
cd "$current_dir"
python3 src/main.py "\$@"
EOF
    
    chmod +x "$wrapper_script"
    sudo mv "$wrapper_script" "$link_target"
    
    print_success "Command 'datawipe-pro' is now available system-wide"
}

# Function to setup directories
setup_directories() {
    print_status "Setting up directories..."
    
    # Create certificates directory
    mkdir -p certificates
    chmod 755 certificates
    
    # Create logs directory
    mkdir -p logs
    chmod 755 logs
    
    print_success "Directories created"
}

# Function to display final instructions
show_final_instructions() {
    echo
    echo "=============================================="
    print_success "DataWipe Pro installation completed!"
    echo "=============================================="
    echo
    echo "You can now run DataWipe Pro in several ways:"
    echo
    echo "1. GUI Application:"
    echo "   python3 src/main.py --gui"
    echo "   OR"
    echo "   datawipe-pro --gui"
    echo
    echo "2. Command Line:"
    echo "   python3 src/main.py --detect"
    echo "   python3 src/main.py --sample-cert"
    echo
    echo "3. Desktop Application:"
    echo "   Look for 'DataWipe Pro' in your applications menu"
    echo
    echo "Important Notes:"
    echo "- Run with 'sudo' for full drive detection capabilities"
    echo "- Certificates will be saved in the 'certificates/' directory"
    echo "- Check README.md for detailed usage instructions"
    echo
    print_warning "Remember: Data wiping is irreversible. Always backup important data!"
    echo
}

# Main installation function
main() {
    echo "=============================================="
    echo "DataWipe Pro - Automated Setup"
    echo "Team: Tejasway"
    echo "=============================================="
    echo
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        print_error "Please do not run this script as root"
        print_status "Run as regular user - sudo will be used when needed"
        exit 1
    fi
    
    # Check system compatibility
    if ! check_system; then
        print_warning "Continuing with manual installation..."
    fi
    
    # Update system
    update_system
    
    # Install system dependencies
    install_system_deps
    
    # Check Python
    check_python
    
    # Install Python dependencies
    install_python_deps
    
    # Setup directories
    setup_directories
    
    # Test installation
    test_installation
    
    # Create desktop entry
    create_desktop_entry
    
    # Create symbolic link
    create_symlink
    
    # Show final instructions
    show_final_instructions
}

# Run main function
main "$@"
