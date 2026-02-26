aws ec2 create-vpc --cidr-block "10.0.0.0/16" --instance-tenancy "default" --tag-specifications '{"resourceType":"vpc","tags":[{"key":"Name","value":"EMR_Project-vpc"}]}' 
aws ec2 modify-vpc-attribute --vpc-id "preview-vpc-1234" --enable-dns-hostnames '{"value":true}' 
aws ec2 describe-vpcs --vpc-ids "preview-vpc-1234" 
aws ec2 create-vpc-endpoint --vpc-id "preview-vpc-1234" --service-name "com.amazonaws.me-central-1.s3" --tag-specifications '{"resourceType":"vpc-endpoint","tags":[{"key":"Name","value":"EMR_Project-vpce-s3"}]}' 
aws ec2 create-subnet --vpc-id "preview-vpc-1234" --cidr-block "10.0.0.0/20" --availability-zone "me-central-1a" --tag-specifications '{"resourceType":"subnet","tags":[{"key":"Name","value":"EMR_Project-subnet-public1-me-central-1a"}]}' 
aws ec2 create-subnet --vpc-id "preview-vpc-1234" --cidr-block "10.0.128.0/20" --availability-zone "me-central-1a" --tag-specifications '{"resourceType":"subnet","tags":[{"key":"Name","value":"EMR_Project-subnet-private1-me-central-1a"}]}' 
aws ec2 create-internet-gateway --tag-specifications '{"resourceType":"internet-gateway","tags":[{"key":"Name","value":"EMR_Project-igw"}]}' 
aws ec2 attach-internet-gateway --internet-gateway-id "preview-igw-1234" --vpc-id "preview-vpc-1234" 
aws ec2 create-route-table --vpc-id "preview-vpc-1234" --tag-specifications '{"resourceType":"route-table","tags":[{"key":"Name","value":"EMR_Project-rtb-public"}]}' 
aws ec2 create-route --route-table-id "preview-rtb-public-0" --destination-cidr-block "0.0.0.0/0" --gateway-id "preview-igw-1234" 
aws ec2 associate-route-table --route-table-id "preview-rtb-public-0" --subnet-id "preview-subnet-public-0" 
aws ec2 create-route-table --vpc-id "preview-vpc-1234" --tag-specifications '{"resourceType":"route-table","tags":[{"key":"Name","value":"EMR_Project-rtb-private1-me-central-1a"}]}' 
aws ec2 associate-route-table --route-table-id "preview-rtb-private-1" --subnet-id "preview-subnet-private-1" 
aws ec2 describe-route-tables --route-table-ids  "preview-rtb-private-1" 
aws ec2 modify-vpc-endpoint --vpc-endpoint-id "preview-vpce-1234" --add-route-table-ids "preview-rtb-private-1" 
