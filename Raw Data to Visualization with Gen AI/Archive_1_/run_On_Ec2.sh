#!/bin/bash

set -e  # Exit on error
set -u  # Treat unset variables as error

# Step 1: Update the system
echo "Updating system..."
sudo dnf -y update

# Step 2: Ensure AWS CLI is installed
if ! command -v aws &> /dev/null; then
  echo "Installing AWS CLI..."
  sudo dnf -y install awscli
fi

# Step 3: Fail-safe AWS CLI configuration
if [ ! -f ~/.aws/credentials ] || [ ! -f ~/.aws/config ]; then
  echo "Configuring AWS CLI with fallback values..."

  export AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-your-access-key}"
  export AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-your-secret-key}"
  export AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-ap-south-1}"

  mkdir -p ~/.aws

  cat > ~/.aws/credentials <<EOF
[default]
aws_access_key_id = ${AWS_ACCESS_KEY_ID}
aws_secret_access_key = ${AWS_SECRET_ACCESS_KEY}
EOF

  cat > ~/.aws/config <<EOF
[default]
region = ${AWS_DEFAULT_REGION}
output = json
EOF
fi

# Step 4: Install Python3 and pip3
if ! command -v python3 &> /dev/null; then
  echo "Installing Python3..."
  sudo dnf -y install python3
fi

if ! command -v pip3 &> /dev/null; then
  echo "Installing pip3..."
  sudo dnf -y install python3-pip
fi

# Step 5: Install ec2-metadata and dependencies
echo "Installing ec2-metadata module..."
pip3 install --upgrade pip
pip3 install ec2-metadata

# Step 6: Download the Python server script
echo "Downloading server.py from S3..."
aws s3 cp s3://cloudagedatabucket/server.py /home/ec2-user/server.py

# Step 7: Run the script
echo "Starting the server..."
sudo python3 /home/ec2-user/server.py -p 80 -r ap-south-1
