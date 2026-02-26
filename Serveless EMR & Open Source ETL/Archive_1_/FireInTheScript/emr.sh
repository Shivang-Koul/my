aws emr create-cluster \
 --name "My cluster" \
 --release-label "emr-7.8.0" \
 --service-role "arn:aws:iam::706769905020:role/EMR_DefaultRole" \
 --unhealthy-node-replacement \
 --ec2-attributes '{"InstanceProfile":"EMR_EC2_DefaultRole","EmrManagedMasterSecurityGroup":"sg-074f70543d282e3f1","EmrManagedSlaveSecurityGroup":"sg-074f70543d282e3f1","KeyName":"uae_key","AdditionalMasterSecurityGroups":["sg-074f70543d282e3f1"],"AdditionalSlaveSecurityGroups":["sg-074f70543d282e3f1"],"SubnetIds":["subnet-050ef08b474b39473"]}' \
 --applications Name=Hadoop Name=Hive Name=Hue \
 --instance-groups '[{"BidPrice":"0.075","InstanceCount":1,"InstanceGroupType":"TASK","Name":"Task - 1","InstanceType":"m5.xlarge","EbsConfiguration":{"EbsBlockDeviceConfigs":[{"VolumeSpecification":{"VolumeType":"gp2","SizeInGB":32},"VolumesPerInstance":2}]}},{"BidPrice":"0.075","InstanceCount":1,"InstanceGroupType":"CORE","Name":"Core","InstanceType":"m5.xlarge","EbsConfiguration":{"EbsBlockDeviceConfigs":[{"VolumeSpecification":{"VolumeType":"gp2","SizeInGB":32},"VolumesPerInstance":2}]}},{"InstanceCount":1,"InstanceGroupType":"MASTER","Name":"Primary","InstanceType":"m5d.xlarge","EbsConfiguration":{"EbsBlockDeviceConfigs":[],"EbsOptimized":true}}]' \
 --scale-down-behavior "TERMINATE_AT_TASK_COMPLETION" \
 --region "me-central-1"
