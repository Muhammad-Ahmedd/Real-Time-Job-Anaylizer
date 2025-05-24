#!/usr/bin/env python3
"""
Real-Time Job Trend Analyzer - GUI Launcher
============================================

This script launches the complete job trend analyzer with GUI interface.
It will scrape real job data from LinkedIn, Glassdoor, and Indeed.

Requirements:
- Python 3.7+
- All packages from requirements.txt
- ChromeDriver for Selenium (optional but recommended)

Usage:
    python run_analyzer.py

Features:
- Real-time job scraping from multiple sources
- Interactive GUI with tabbed interface
- Comprehensive trend analysis
- Data export (TXT, CSV, Charts)
- Professional visualizations
"""

import sys
import os
import subprocess
import importlib.util

def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'tkinter', 'requests', 'beautifulsoup4', 'selenium', 
        'pandas', 'matplotlib', 'seaborn', 'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            elif package == 'beautifulsoup4':
                import bs4
            else:
                importlib.import_module(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_requirements():
    """Install missing requirements"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def check_chromedriver():
    """Check if ChromeDriver is available"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        driver.quit()
        return True
    except Exception:
        return False

def main():
    """Main launcher function"""
    print("🚀 Real-Time Job Trend Analyzer")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required!")
        print(f"   Current version: {sys.version}")
        return
    
    print(f"✅ Python version: {sys.version.split()[0]}")
    
    # Check required packages
    missing = check_requirements()
    if missing:
        print(f"⚠️  Missing packages: {', '.join(missing)}")
        
        if os.path.exists('requirements.txt'):
            install_choice = input("📦 Install missing packages? (y/n): ").lower().strip()
            if install_choice == 'y':
                if not install_requirements():
                    print("❌ Installation failed. Please install manually:")
                    print(f"   pip install {' '.join(missing)}")
                    return
            else:
                print("❌ Cannot proceed without required packages.")
                return
        else:
            print("❌ requirements.txt not found. Please install manually:")
            print(f"   pip install {' '.join(missing)}")
            return
    else:
        print("✅ All required packages are installed")
    
    # Check ChromeDriver
    if check_chromedriver():
        print("✅ ChromeDriver is available (full scraping functionality)")
    else:
        print("⚠️  ChromeDriver not found (will use fallback scraping)")
        print("   For full functionality, install ChromeDriver:")
        print("   https://chromedriver.chromium.org/")
    
    print("\n🔍 Starting Job Trend Analyzer GUI...")
    print("=" * 50)
    
    try:
        # Import and run the main GUI
        from main_gui import main
        main()
        
    except ImportError as e:
        print(f"❌ Failed to import GUI module: {e}")
        print("   Make sure all files are in the same directory:")
        print("   - main_gui.py")
        print("   - job_scraper.py") 
        print("   - data_analyzer.py")
        print("   - data_visualizer.py")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Application interrupted by user")
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("   Please check the error details and try again")

if __name__ == "__main__":
    main()