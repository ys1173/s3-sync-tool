# AWS S3 Directory Sync Tool

A cross-platform Python utility that automates the process of syncing directories to AWS S3 buckets using rclone.

## Features

- **Auto-installation**: Automatically detects and installs rclone if not present
- **Cross-platform support**: Works on Windows, macOS, and Linux
- **User-friendly prompts**: Guides you through all configuration options
- **AWS credential verification**: Verifies AWS credentials before starting the sync
- **Temporary credentials**: Credentials are used only for the current operation and not stored
- **Advanced sync options**: Supports dry runs, file exclusion patterns, and deletion options
- **Error handling**: Clear error messages and troubleshooting guidance

## Prerequisites

- Python 3.6 or higher
- Internet connection for downloading rclone if not installed
- AWS S3 bucket with appropriate permissions
- AWS Access Key ID and Secret Access Key with S3 permissions

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/ys1173/s3-sync-tool.git
   cd s3-sync-tool
   ```

2. No additional installation steps are required! The script will install rclone automatically if needed.

## Usage

Run the script with Python:

```
python s3-sync-tool.py
```

Follow the interactive prompts to:
1. Specify your source directory
2. Enter AWS S3 bucket information and credentials
3. Configure sync options (dry run, exclusion patterns, etc.)
4. Review and confirm the configuration
5. Monitor the sync process

## Example

```
============================================================
AWS S3 Directory Sync Tool (using rclone)
============================================================
Enter the source directory to sync: /path/to/your/files

--- AWS S3 Configuration ---
Enter S3 bucket name (just the bucket name, not the ARN): my-bucket
Enter AWS region (default: us-east-1): 
Enter destination path within bucket (optional, press Enter to use bucket root): my-folder

--- AWS Credentials ---
Note: Credentials will be used only for this sync operation and won't be stored.
Enter AWS Access Key ID: AKIAXXXXXXXXXXXXXXXX
Enter AWS Secret Access Key: ****************************************

--- Sync Options ---
Perform a dry run first? (yes/no, default: yes): yes
Delete files in destination that don't exist in source? (yes/no, default: no): no
Enter patterns to exclude (comma-separated, e.g., '*.tmp,*.temp,temp/'): .DS_Store,*.tmp

--- Sync Configuration Summary ---
Source directory: /path/to/your/files
Destination: s3:my-bucket/my-folder
AWS Region: us-east-1
Delete in destination: No
Excluding: .DS_Store, *.tmp

Proceed with this configuration? (yes/no): yes
```

## Security Notes

- AWS credentials are not stored permanently
- Credentials are only used for the current sync operation
- The script creates temporary configuration files that are deleted after use

## Troubleshooting

If you encounter issues with the sync:

1. Verify your AWS credentials are correct
2. Ensure the bucket name is correct and you have access to it
3. Try using the AWS CLI directly: `aws s3 ls s3://your-bucket`
4. Check your IAM user permissions for S3 operations
5. Look for special characters in credentials that might need escaping

## License

MIT License

## Credits

Created by [Your Name]

Powered by [rclone](https://rclone.org/)