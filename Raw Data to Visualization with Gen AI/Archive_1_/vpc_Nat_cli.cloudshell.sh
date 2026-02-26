aws ec2 create-vpc --cidr-block "10.0.0.0/16" --instance-tenancy "default" --tag-specifications '{"resourceType":"vpc","tags":[{"key":"Name","value":"vpc-flow-logs-project-vpc"}]}' 
aws ec2 modify-vpc-attribute --vpc-id "preview-vpc-1234" --enable-dns-hostnames '{"value":true}' 
aws ec2 describe-vpcs --vpc-ids "preview-vpc-1234" 
aws ec2 create-vpc-endpoint --vpc-id "preview-vpc-1234" --service-name "com.amazonaws.ap-south-1.s3" --tag-specifications '{"resourceType":"vpc-endpoint","tags":[{"key":"Name","value":"vpc-flow-logs-project-vpce-s3"}]}' 
aws ec2 create-subnet --vpc-id "preview-vpc-1234" --cidr-block "10.0.0.0/20" --availability-zone "ap-south-1a" --tag-specifications '{"resourceType":"subnet","tags":[{"key":"Name","value":"vpc-flow-logs-project-subnet-public1-ap-south-1a"}]}' 
aws ec2 create-subnet --vpc-id "preview-vpc-1234" --cidr-block "10.0.16.0/20" --availability-zone "ap-south-1b" --tag-specifications '{"resourceType":"subnet","tags":[{"key":"Name","value":"vpc-flow-logs-project-subnet-public2-ap-south-1b"}]}' 
aws ec2 create-subnet --vpc-id "preview-vpc-1234" --cidr-block "10.0.128.0/20" --availability-zone "ap-south-1a" --tag-specifications '{"resourceType":"subnet","tags":[{"key":"Name","value":"vpc-flow-logs-project-subnet-private1-ap-south-1a"}]}' 
aws ec2 create-subnet --vpc-id "preview-vpc-1234" --cidr-block "10.0.144.0/20" --availability-zone "ap-south-1b" --tag-specifications '{"resourceType":"subnet","tags":[{"key":"Name","value":"vpc-flow-logs-project-subnet-private2-ap-south-1b"}]}' 
aws ec2 create-internet-gateway --tag-specifications '{"resourceType":"internet-gateway","tags":[{"key":"Name","value":"vpc-flow-logs-project-igw"}]}' 
aws ec2 attach-internet-gateway --internet-gateway-id "preview-igw-1234" --vpc-id "preview-vpc-1234" 
aws ec2 create-route-table --vpc-id "preview-vpc-1234" --tag-specifications '{"resourceType":"route-table","tags":[{"key":"Name","value":"vpc-flow-logs-project-rtb-public"}]}' 
aws ec2 create-route --route-table-id "preview-rtb-public-0" --destination-cidr-block "0.0.0.0/0" --gateway-id "preview-igw-1234" 
aws ec2 associate-route-table --route-table-id "preview-rtb-public-0" --subnet-id "preview-subnet-public-0" 
aws ec2 associate-route-table --route-table-id "preview-rtb-public-0" --subnet-id "preview-subnet-public-1" 
aws ec2 allocate-address --domain "vpc" --tag-specifications '{"resourceType":"elastic-ip","tags":[{"key":"Name","value":"vpc-flow-logs-project-eip-ap-south-1a"}]}' 
aws ec2 allocate-address --domain "vpc" --tag-specifications '{"resourceType":"elastic-ip","tags":[{"key":"Name","value":"vpc-flow-logs-project-eip-ap-south-1b"}]}' 
aws ec2 create-nat-gateway --subnet-id "preview-subnet-public-0" --allocation-id "preview-eipalloc-0" --tag-specifications '{"resourceType":"natgateway","tags":[{"key":"Name","value":"vpc-flow-logs-project-nat-public1-ap-south-1a"}]}' 
aws ec2 create-nat-gateway --subnet-id "preview-subnet-public-1" --allocation-id "preview-eipalloc-1" --tag-specifications '{"resourceType":"natgateway","tags":[{"key":"Name","value":"vpc-flow-logs-project-nat-public2-ap-south-1b"}]}' 
aws ec2 describe-nat-gateways --nat-gateway-ids "preview-nat-0" "preview-nat-1" --filter '{"Name":"state","Values":["available"]}' 
aws ec2 create-route-table --vpc-id "preview-vpc-1234" --tag-specifications '{"resourceType":"route-table","tags":[{"key":"Name","value":"vpc-flow-logs-project-rtb-private1-ap-south-1a"}]}' 
aws ec2 create-route --route-table-id "preview-rtb-private-1" --destination-cidr-block "0.0.0.0/0" --nat-gateway-id "preview-nat-0" 
aws ec2 associate-route-table --route-table-id "preview-rtb-private-1" --subnet-id "preview-subnet-private-2" 
aws ec2 create-route-table --vpc-id "preview-vpc-1234" --tag-specifications '{"resourceType":"route-table","tags":[{"key":"Name","value":"vpc-flow-logs-project-rtb-private2-ap-south-1b"}]}' 
aws ec2 create-route --route-table-id "preview-rtb-private-2" --destination-cidr-block "0.0.0.0/0" --nat-gateway-id "preview-nat-1" 
aws ec2 associate-route-table --route-table-id "preview-rtb-private-2" --subnet-id "preview-subnet-private-3" 
aws ec2 describe-route-tables --route-table-ids   "preview-rtb-private-1" "preview-rtb-private-2" 
aws ec2 modify-vpc-endpoint --vpc-endpoint-id "preview-vpce-1234" --add-route-table-ids "preview-rtb-private-1" "preview-rtb-private-2" 