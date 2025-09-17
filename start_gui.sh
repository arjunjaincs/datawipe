#!/bin/bash

# DataWipe Pro - Quick Start Script
# This script sets up the environment and launches the GUI with proper permissions

echo "=================================================="
echo "DataWipe Pro - Quick Start"
echo "Team: Tejasway"
echo "=================================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "This script requires root privileges to access storage devices."
    echo "Please run with sudo:"
    echo "sudo ./start_gui.sh"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
    echo "Virtual environment created."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install system dependencies if needed
echo "Checking system dependencies..."
apt-get update -qq
apt-get install -y python3-tk fonts-ubuntu fonts-dejavu-core

# Launch GUI
echo "Launching DataWipe Pro GUI..."
echo "=================================================="
python3 src/main.py --gui

echo "DataWipe Pro session ended."
