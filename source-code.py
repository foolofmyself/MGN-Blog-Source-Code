import boto3

# Enter your AWS credentials here.
# You can find these credentials in the AWS Management Console.


aws_access_key_id = input("Enter the aws access key id: ")
aws_secret_access_key = input("Enter the aws secret access key: ")
region_name = input("Enter the region name: ")
# Start the session with your AWS credentials
# and the region you want to work with.

session = boto3.Session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)

#Enter your EC2 instance id and subnet id here.
#You can find the instance id  and subnet id in the AWS Management Console.

instance_id = input("Enter the instance id: ")
subnet_id1 = 'subnet-000000000000000'

subnet_id2 = 'subnet-000000000000000'
ec2 = boto3.client("ec2")
sg_id = 'sg-04cadfeb375c5a30e'

# Allocate a public IP address for the instance.

eip = ec2.allocate_address(Domain="vpc")

ec2.associate_address(InstanceId=instance_id, PublicIp=eip["PublicIp"])

vpc_id = ec2.describe_instances (InstanceIds=[instance_id])["Reservations"][0]["Instances"][0]["VpcId"]

#Here we create a target group for the instance as well as a load balancer.
#The target group is used to route traffic to the instance.

elbv2 = boto3.client("elbv2")

target_group = elbv2.create_target_group(
    Name="target-group111",
    Protocol="HTTP",
    Port=80,
    VpcId=vpc_id,
    HealthCheckProtocol="HTTP",
    HealthCheckPort="80",
    HealthCheckPath="/",
    HealthCheckIntervalSeconds=30,
    HealthCheckTimeoutSeconds=5,
    HealthyThresholdCount=5,
    UnhealthyThresholdCount=2,
    Matcher={
        "HttpCode": "200"
        }
        )
response = elbv2.register_targets(
    TargetGroupArn=target_group["TargetGroups"][0]["TargetGroupArn"],
    Targets=[
        {
            "Id": instance_id
            }])
response = elbv2.create_load_balancer(
    Name="load-balancer-xxxxxx",
    Subnets=[subnet_id1,subnet_id2],
    SecurityGroups=[sg_id],
    Scheme="internet-facing",
    Tags=[
        {
            "Key": "Name",
            "Value": "load-balancer"
            }])
#Lastly we create a listener for the load balancer.
#The listener is used to route traffic to the target group.

elbv2.create_listener(
    LoadBalancerArn=response["LoadBalancers"][0]["LoadBalancerArn"],
    Protocol="HTTP",
    Port=80,
    DefaultActions=[
        {
            "Type": "forward",
            "TargetGroupArn": target_group["TargetGroups"][0]["TargetGroupArn"]
            }])
#You can view the output of your instance using the public IP address provided.
print(f'The public IP address of the instance is {eip["PublicIp"]}. You may now test the instance.')
