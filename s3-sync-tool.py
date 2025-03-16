#!/usr/bin/env python3
import os
import sys
import platform
import subprocess
import getpass
import tempfile
import shutil
import zipfile
from pathlib import Path
import stat
import urllib.request

def check_rclone_installed():
    """Check if rclone is installed and available in the PATH."""
    try:
        result = subprocess.run(['rclone', '--version'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_rclone():
    """Install rclone based on the operating system."""
    system = platform.system().lower()
    
    print(f"Rclone not found. Installing rclone for {system}...")
    
    if system == "windows":
        install_rclone_windows()
    elif system == "darwin":  # macOS
        install_rclone_macos()
    elif system == "linux":
        install_rclone_linux()
    else:
        print(f"Unsupported operating system: {system}")
        print("Please install rclone manually from https://rclone.org/downloads/")
        sys.exit(1)
        
    # Verify installation
    if check_rclone_installed():
        print("Rclone installed successfully!")
    else:
        print("Failed to install rclone. Please install manually from https://rclone.org/downloads/")
        sys.exit(1)

def install_rclone_windows():
    """Install rclone on Windows."""
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    try:
        # Download rclone
        zip_path = os.path.join(temp_dir, "rclone.zip")
        print("Downloading rclone...")
        urllib.request.urlretrieve("https://downloads.rclone.org/rclone-current-windows-amd64.zip", zip_path)
        
        # Extract zip
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find the extracted directory (should be something like rclone-vX.XX.X-windows-amd64)
        extracted_dirs = [d for d in os.listdir(temp_dir) if d.startswith('rclone-') and os.path.isdir(os.path.join(temp_dir, d))]
        if not extracted_dirs:
            print("Failed to find extracted rclone directory")
            return False
            
        rclone_dir = os.path.join(temp_dir, extracted_dirs[0])
        rclone_exe = os.path.join(rclone_dir, "rclone.exe")
        
        # Create rclone directory in Program Files
        program_files = os.environ.get('PROGRAMFILES', 'C:\\Program Files')
        install_dir = os.path.join(program_files, "rclone")
        
        # Ask for admin permission to copy to Program Files
        print("Attempting to install rclone to", install_dir)
        print("This may require administrator privileges.")
        
        # Try to create the directory and copy rclone
        try:
            os.makedirs(install_dir, exist_ok=True)
            shutil.copy2(rclone_exe, os.path.join(install_dir, "rclone.exe"))
            
            # Add to PATH using setx (requires Command Prompt with admin privileges)
            subprocess.run(['setx', '/M', 'PATH', f"%PATH%;{install_dir}"], 
                          shell=True, 
                          check=True)
            
            print(f"Rclone installed to {install_dir} and added to PATH.")
            print("You may need to restart your terminal for PATH changes to take effect.")
            
        except (PermissionError, subprocess.CalledProcessError):
            # Fall back to user directory installation
            print("Could not install to Program Files. Installing to user directory...")
            user_dir = os.path.join(os.path.expanduser("~"), "rclone")
            os.makedirs(user_dir, exist_ok=True)
            shutil.copy2(rclone_exe, os.path.join(user_dir, "rclone.exe"))
            
            # Add to user PATH
            user_path = os.environ.get('PATH', '')
            if user_dir not in user_path:
                subprocess.run(['setx', 'PATH', f"{user_path};{user_dir}"], 
                              shell=True, 
                              check=True)
                
            print(f"Rclone installed to {user_dir} and added to user PATH.")
            print("You may need to restart your terminal for PATH changes to take effect.")
            print(f"For this session, we'll use the full path to rclone: {os.path.join(user_dir, 'rclone.exe')}")
            
            # Set a global variable for the full path to use in this session
            global RCLONE_PATH
            RCLONE_PATH = os.path.join(user_dir, "rclone.exe")
                
    finally:
        # Clean up
        shutil.rmtree(temp_dir, ignore_errors=True)

def install_rclone_macos():
    """Install rclone on macOS."""
    # Try to use Homebrew first
    try:
        print("Checking if Homebrew is installed...")
        subprocess.run(['brew', '--version'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE, 
                      check=True)
        
        print("Installing rclone with Homebrew...")
        subprocess.run(['brew', 'install', 'rclone'], 
                      check=True)
        return
        
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("Homebrew not available. Installing manually...")
    
    # Manual installation
    temp_dir = tempfile.mkdtemp()
    try:
        # Download rclone
        tar_path = os.path.join(temp_dir, "rclone.zip")
        print("Downloading rclone...")
        urllib.request.urlretrieve("https://downloads.rclone.org/rclone-current-osx-amd64.zip", tar_path)
        
        # Extract zip
        with zipfile.ZipFile(tar_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find the extracted directory
        extracted_dirs = [d for d in os.listdir(temp_dir) if d.startswith('rclone-') and os.path.isdir(os.path.join(temp_dir, d))]
        if not extracted_dirs:
            print("Failed to find extracted rclone directory")
            return False
            
        rclone_dir = os.path.join(temp_dir, extracted_dirs[0])
        rclone_bin = os.path.join(rclone_dir, "rclone")
        
        # Make executable
        os.chmod(rclone_bin, os.stat(rclone_bin).st_mode | stat.S_IEXEC)
        
        # Install to /usr/local/bin (may require sudo)
        try:
            subprocess.run(['sudo', 'mkdir', '-p', '/usr/local/bin'], check=True)
            subprocess.run(['sudo', 'cp', rclone_bin, '/usr/local/bin/'], check=True)
            print("Rclone installed to /usr/local/bin/")
        except subprocess.CalledProcessError:
            # Fall back to user directory
            print("Could not install to /usr/local/bin. Installing to user directory...")
            user_bin = os.path.join(os.path.expanduser("~"), "bin")
            os.makedirs(user_bin, exist_ok=True)
            shutil.copy2(rclone_bin, os.path.join(user_bin, "rclone"))
            
            # Add to PATH if not already there
            shell_profile = os.path.join(os.path.expanduser("~"), ".bash_profile")
            if os.path.isfile(os.path.join(os.path.expanduser("~"), ".zshrc")):
                shell_profile = os.path.join(os.path.expanduser("~"), ".zshrc")
                
            with open(shell_profile, 'a') as f:
                f.write(f'\n# Added by S3 sync script\nexport PATH="$PATH:{user_bin}"\n')
                
            print(f"Rclone installed to {user_bin}")
            print(f"Added {user_bin} to PATH in {shell_profile}")
            print("Please restart your terminal or run 'source ~/.bash_profile' to update your PATH")
            print(f"For this session, we'll use the full path to rclone: {os.path.join(user_bin, 'rclone')}")
            
            # Set a global variable for the full path to use in this session
            global RCLONE_PATH
            RCLONE_PATH = os.path.join(user_bin, "rclone")
                
    finally:
        # Clean up
        shutil.rmtree(temp_dir, ignore_errors=True)

def install_rclone_linux():
    """Install rclone on Linux."""
    # Try using package managers first
    package_managers = [
        ('apt-get', ['sudo', 'apt-get', 'update'], ['sudo', 'apt-get', 'install', '-y', 'rclone']),
        ('yum', None, ['sudo', 'yum', 'install', '-y', 'rclone']),
        ('dnf', None, ['sudo', 'dnf', 'install', '-y', 'rclone']),
        ('zypper', None, ['sudo', 'zypper', 'install', '-y', 'rclone']),
    ]
    
    for pm, update_cmd, install_cmd in package_managers:
        try:
            # Check if the package manager exists
            subprocess.run(['which', pm], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE, 
                          check=True)
            
            # Run update command if provided
            if update_cmd:
                subprocess.run(update_cmd, check=True)
            
            # Install rclone
            print(f"Installing rclone with {pm}...")
            subprocess.run(install_cmd, check=True)
            return
            
        except subprocess.CalledProcessError:
            continue
    
    # Manual installation as fallback
    print("No supported package manager found. Installing manually...")
    temp_dir = tempfile.mkdtemp()
    try:
        # Download rclone
        tar_path = os.path.join(temp_dir, "rclone.zip")
        print("Downloading rclone...")
        urllib.request.urlretrieve("https://downloads.rclone.org/rclone-current-linux-amd64.zip", tar_path)
        
        # Extract zip
        with zipfile.ZipFile(tar_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find the extracted directory
        extracted_dirs = [d for d in os.listdir(temp_dir) if d.startswith('rclone-') and os.path.isdir(os.path.join(temp_dir, d))]
        if not extracted_dirs:
            print("Failed to find extracted rclone directory")
            return False
            
        rclone_dir = os.path.join(temp_dir, extracted_dirs[0])
        rclone_bin = os.path.join(rclone_dir, "rclone")
        
        # Make executable
        os.chmod(rclone_bin, os.stat(rclone_bin).st_mode | stat.S_IEXEC)
        
        # Try to install to /usr/local/bin (requires sudo)
        try:
            subprocess.run(['sudo', 'mkdir', '-p', '/usr/local/bin'], check=True)
            subprocess.run(['sudo', 'cp', rclone_bin, '/usr/local/bin/'], check=True)
            print("Rclone installed to /usr/local/bin/")
        except subprocess.CalledProcessError:
            # Fall back to user directory
            print("Could not install to /usr/local/bin. Installing to user directory...")
            user_bin = os.path.join(os.path.expanduser("~"), "bin")
            os.makedirs(user_bin, exist_ok=True)
            shutil.copy2(rclone_bin, os.path.join(user_bin, "rclone"))
            
            # Add to PATH if not already there
            bashrc = os.path.join(os.path.expanduser("~"), ".bashrc")
            with open(bashrc, 'a') as f:
                f.write(f'\n# Added by S3 sync script\nexport PATH="$PATH:{user_bin}"\n')
                
            print(f"Rclone installed to {user_bin}")
            print(f"Added {user_bin} to PATH in ~/.bashrc")
            print("Please restart your terminal or run 'source ~/.bashrc' to update your PATH")
            print(f"For this session, we'll use the full path to rclone: {os.path.join(user_bin, 'rclone')}")
            
            # Set a global variable for the full path to use in this session
            global RCLONE_PATH
            RCLONE_PATH = os.path.join(user_bin, "rclone")
                
    finally:
        # Clean up
        shutil.rmtree(temp_dir, ignore_errors=True)

def get_source_directory():
    """Prompt for and validate source directory."""
    while True:
        source_dir = input("Enter the source directory to sync: ").strip()
        
        # Expand user directory if needed
        source_dir = os.path.expanduser(source_dir)
        
        if os.path.isdir(source_dir):
            return source_dir
        else:
            print(f"Directory not found: {source_dir}")
            print("Please enter a valid directory path.")

def get_s3_config():
    """Prompt for S3 configuration and credentials."""
    print("\n--- AWS S3 Configuration ---")
    
    bucket_name = input("Enter S3 bucket name (just the bucket name, not the ARN): ").strip()
    
    # Extract bucket name from ARN if provided
    if bucket_name.startswith('arn:aws:s3:::'):
        print("It looks like you entered an ARN instead of just the bucket name.")
        extracted_name = bucket_name.replace('arn:aws:s3:::', '')
        proceed = input(f"Should I use '{extracted_name}' as the bucket name? (yes/no): ").strip().lower()
        if proceed == 'yes':
            bucket_name = extracted_name
        else:
            bucket_name = input("Please enter just the bucket name: ").strip()
    
    # Get region with default
    region = input("Enter AWS region (default: us-east-1): ").strip()
    if not region:
        region = "us-east-1"
    
    # Get optional destination path
    destination_path = input("Enter destination path within bucket (optional, press Enter to use bucket root): ").strip()
    
    print("\n--- AWS Credentials ---")
    print("Note: Credentials will be used only for this sync operation and won't be stored.")
    
    access_key = input("Enter AWS Access Key ID: ").strip()
    
    # Use standard input instead of getpass for better paste compatibility
    print("WARNING: The following input will display your secret key on screen for better paste compatibility")
    secret_key = input("Enter AWS Secret Access Key: ").strip()
    
    # Validate minimal input
    if not bucket_name or not access_key or not secret_key:
        print("Error: Bucket name, Access Key ID, and Secret Access Key are required!")
        return get_s3_config()  # Recursively ask again
    
    # Construct the full S3 path
    s3_path = f"s3:{bucket_name}"
    if destination_path:
        # Ensure no leading slash in the destination path
        destination_path = destination_path.lstrip('/')
        s3_path = f"s3:{bucket_name}/{destination_path}"
    
    return {
        "bucket_name": bucket_name,
        "region": region,
        "s3_path": s3_path,
        "access_key": access_key,
        "secret_key": secret_key
    }

def verify_aws_credentials(s3_config):
    """Verify AWS credentials before attempting the sync."""
    print("\nVerifying AWS credentials...")
    
    # Set environment variables for AWS CLI
    env = os.environ.copy()
    env['AWS_ACCESS_KEY_ID'] = s3_config['access_key']
    env['AWS_SECRET_ACCESS_KEY'] = s3_config['secret_key']
    env['AWS_REGION'] = s3_config['region']
    
    # Try a simple AWS command to list the bucket
    try:
        print(f"Testing access to bucket: {s3_config['bucket_name']}")
        result = subprocess.run(
            ['aws', 's3', 'ls', f"s3://{s3_config['bucket_name']}"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ AWS credentials verified successfully!")
            return True
        else:
            print(f"❌ AWS credential verification failed: {result.stderr}")
            print("\nPossible issues:")
            print("1. The access key or secret key may be incorrect")
            print("2. The specified bucket may not exist or you don't have access to it")
            print("3. The region may be incorrect")
            print("4. There may be network connectivity issues")
            
            # Offer to continue anyway
            retry = input("\nWould you like to continue with the sync anyway? (yes/no): ").strip().lower()
            return retry == 'yes'
    except FileNotFoundError:
        print("Note: AWS CLI not found. Skipping credential verification.")
        return True

def get_sync_options():
    """Prompt for additional sync options."""
    print("\n--- Sync Options ---")
    
    options = {}
    
    # Ask about dry run
    dry_run = input("Perform a dry run first? (yes/no, default: yes): ").strip().lower()
    options["dry_run"] = dry_run != "no"
    
    # Ask about delete
    delete = input("Delete files in destination that don't exist in source? (yes/no, default: no): ").strip().lower()
    options["delete"] = delete == "yes"
    
    # Ask about excluding patterns
    exclude = input("Enter patterns to exclude (comma-separated, e.g., '*.tmp,*.temp,temp/'): ").strip()
    if exclude:
        options["exclude"] = [pattern.strip() for pattern in exclude.split(',')]
    else:
        options["exclude"] = []
    
    return options

def run_rclone_sync(source_dir, s3_config, options):
    """Run the rclone sync command with the given configuration."""
    # Get the rclone executable path
    rclone_executable = RCLONE_PATH if 'RCLONE_PATH' in globals() and RCLONE_PATH else 'rclone'
    
    # Print rclone version for debugging
    try:
        version_result = subprocess.run([rclone_executable, '--version'], 
                                       stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE, 
                                       text=True, 
                                       check=True)
        print(f"Using rclone: {version_result.stdout.splitlines()[0] if version_result.stdout else 'unknown version'}")
    except Exception as e:
        print(f"Warning: Could not verify rclone version: {str(e)}")
    
    # Create a temporary rclone config file
    import tempfile
    temp_config_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
    try:
        # Write a minimal config file
        config_content = f"""[s3]
type = s3
provider = AWS
env_auth = true
region = {s3_config['region']}
access_key_id = {s3_config['access_key']}
secret_access_key = {s3_config['secret_key']}
"""
        temp_config_file.write(config_content)
        temp_config_file.close()
        
        # Standard S3 path format with remote name
        s3_dest = f"s3:{s3_config['bucket_name']}"
        if '/' in s3_config["s3_path"].split(':', 1)[1]:
            # Extract path after bucket name
            path_part = s3_config["s3_path"].split(':', 1)[1].split('/', 1)[1]
            s3_dest = f"s3:{s3_config['bucket_name']}/{path_part}"
        
        # Build the rclone command with the config file
        cmd = [
            rclone_executable,
            '--config', temp_config_file.name,
            'sync',
            source_dir,
            s3_dest,
            '--progress',
            '--verbose'
        ]
        
        # Add exclude patterns if any
        for pattern in options.get("exclude", []):
            cmd.append(f'--exclude={pattern}')
        
        # Add delete flag if requested
        if options.get("delete", False):
            cmd.append('--delete-after')
        
        # Add dry-run flag if requested
        if options.get("dry_run", True):
            cmd.append('--dry-run')
            print("\nPerforming a dry run first (no files will be modified)...")
        
        # Print the command for debugging (hide the config file path)
        debug_cmd = cmd.copy()
        for i, arg in enumerate(debug_cmd):
            if i > 0 and debug_cmd[i-1] == '--config':
                debug_cmd[i] = '[temp_config_file]'
        
        print(f"Running command: {' '.join(debug_cmd)}")
        print("Using explicit rclone config file with AWS credentials")
        
        try:
            # Run the command with proper output capturing
            result = subprocess.run(cmd, 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE, 
                                    text=True)
            
            # Always print the output for visibility
            if result.stdout:
                print(result.stdout)
            
            if result.returncode != 0:
                print(f"Rclone command failed with exit code {result.returncode}")
                if result.stderr:
                    print(f"Error details: {result.stderr}")
                return False
            
            # If this was a dry run, ask if they want to proceed with the actual sync
            if options.get("dry_run", True):
                proceed = input("\nDo you want to proceed with the actual sync? (yes/no): ").strip().lower()
                if proceed == "yes":
                    # Remove dry-run flag and run again
                    cmd.remove('--dry-run')
                    print("\nPerforming actual sync...")
                    
                    print(f"Running command: {' '.join(debug_cmd)}")
                    print("Using explicit rclone config file with AWS credentials")
                    
                    result = subprocess.run(cmd, 
                                            stdout=subprocess.PIPE, 
                                            stderr=subprocess.PIPE, 
                                            text=True)
                    
                    if result.stdout:
                        print(result.stdout)
                    
                    if result.returncode != 0:
                        print(f"Rclone command failed with exit code {result.returncode}")
                        if result.stderr:
                            print(f"Error details: {result.stderr}")
                        return False
                else:
                    print("Sync operation cancelled.")
                    return False
            
            return True
        
        except Exception as e:
            print(f"Error running rclone command: {str(e)}")
            print(f"Command attempted: {' '.join(debug_cmd)}")
            return False
            
    finally:
        # Clean up the temporary config file
        try:
            os.unlink(temp_config_file.name)
        except:
            pass

def main():
    print("=" * 60)
    print("AWS S3 Directory Sync Tool (using rclone)")
    print("=" * 60)
    
    # Check if rclone is installed, install if needed
    if not check_rclone_installed():
        install_rclone()
    
    # Get source directory
    source_dir = get_source_directory()
    
    # Get S3 configuration
    s3_config = get_s3_config()
    
    # Verify AWS credentials before proceeding
    if not verify_aws_credentials(s3_config):
        print("AWS credential verification failed. Please check your credentials and try again.")
        corrected = input("Would you like to re-enter your AWS credentials? (yes/no): ").strip().lower()
        if corrected == "yes":
            s3_config = get_s3_config()
        else:
            print("Operation cancelled.")
            return
    
    # Get sync options
    options = get_sync_options()
    
    # Confirm the settings
    print("\n--- Sync Configuration Summary ---")
    print(f"Source directory: {source_dir}")
    print(f"Destination: {s3_config['s3_path']}")
    print(f"AWS Region: {s3_config['region']}")
    print(f"Delete in destination: {'Yes' if options.get('delete', False) else 'No'}")
    if options.get("exclude", []):
        print(f"Excluding: {', '.join(options['exclude'])}")
    
    # Ask for confirmation
    confirm = input("\nProceed with this configuration? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Operation cancelled.")
        return
    
    # Run the sync
    success = run_rclone_sync(source_dir, s3_config, options)
    
    if success:
        print("\nSync operation completed successfully!")
    else:
        print("\nSync operation encountered issues.")
        
        # Provide troubleshooting advice
        print("\n--- Troubleshooting ---")
        print("1. Verify your AWS credentials are correct")
        print("2. Check if the bucket name is correct and accessible to you")
        print("3. Try using the AWS CLI directly: aws s3 ls s3://your-bucket")
        print("4. Check if your IAM user has sufficient permissions for S3 operations")
        print("5. Check for any special characters in your credentials that might need escaping")
        
    print("\nThank you for using the AWS S3 Directory Sync Tool!")

if __name__ == "__main__":
    # Global variable for rclone path, may be set during installation
    RCLONE_PATH = None
    
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        sys.exit(1)