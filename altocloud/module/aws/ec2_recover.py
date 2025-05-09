import os
import boto3
from botocore.exceptions import ClientError

os.umask(0)

gargs = {
    'service_name': 'ec2',
    'region_name': 'ap-south-1'
}

ec2_client = boto3.client(**gargs)
ec2_resource = boto3.resource(**gargs)


class Ec2:
    def __init__(self, instance_id=None):
        self._instance_id = instance_id
        self.client = ec2_client
        self.resource = ec2_resource
        self.state = None
        self.obj = None
        self._temp_key_name = "temp_key"
        self._public_key_data = ""

    def _get_public_key(self, key_name=None, key_id=None):
        _args = {'IncludePublicKey': True}
        if key_id:
            _args['KeyPairIds'] = [key_id]
        if key_name:
            _args['KeyNames'] = [key_name]

        response = self.client.describe_key_pairs(**_args)
        return response['KeyPairs']

    def generate_key(self):
        _keys = self._get_public_key(key_name=self._temp_key_name)
        if _keys:
            print("++Key already exists")
            self._public_key_data = _keys[0]['PublicKey']
            return self._temp_key_name
        response = ec2_client.create_key_pair(
            KeyName=self._temp_key_name,
            KeyType='rsa',
            KeyFormat='pem',
        )
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            save_file(response['KeyMaterial'], f"./{self._temp_key_name}.pem")
            print(f"++File saved to {self._temp_key_name}.pem")
            return self._temp_key_name
        return None

    @staticmethod
    def create_instance(key):
        _ec2_args = dict(
            ImageId='ami-0e35ddab05955cf57',
            InstanceType='t2.micro',
            MinCount=1,
            MaxCount=1,
            KeyName=key,
            SecurityGroupIds=['sg-0506265e40d70fea3'],
            SubnetId='subnet-0e6bb65b9988e5a67'
        )
        response = ec2_client.run_instances(**_ec2_args)
        print(f"{response=}")
        instance_id = response['Instances'][0]['InstanceId']
        print(f"Launching instance: {instance_id}")
        instance = ec2_resource.Instance(instance_id)
        print("Waiting for instance to enter 'running' state...")
        instance.wait_until_running()
        instance.load()
        print(f"Instance is running. Public IP: {instance.public_ip_address}")
        # return instance

    def eval(self):
        self.obj = self.resource.Instance(self._instance_id)

    def find(self):
        try:
            responses = self.client.describe_instances(InstanceIds=[self._instance_id])
            reservations = responses['Reservations']
            if not reservations:
                raise Exception(f"Instance {self._instance_id} not found.")
            instance = reservations[0]['Instances'][0]
            self.state = instance['State']['Name']
            print(f"Instance {self._instance_id} is in '{self.state}' state.")

        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidInstanceID.NotFound':
                raise Exception(f"Instance {self._instance_id} does not exist.")
            else:
                raise Exception(f"Invalid Error: {e}")
        except Exception as e:
            raise Exception(f"Invalid Error: {e}")

    def stop(self):
        print(f"++Stopping the instance {self._instance_id}. . ")
        self.obj.stop(Force=True)
        self.obj.wait_until_stopped()
        print("++Instance is stopped")

    @property
    def volumes(self) -> list:
        return self.obj.volumes.all()


def save_file(data, name):
    descriptor = os.open(path=name, flags=(
        os.O_WRONLY  # access mode: write only
        | os.O_CREAT  # create if not exists
        | os.O_TRUNC  # truncate the file to zero
        ),
    mode=0o600)
    with open(descriptor, 'w') as f:
        f.write(data)


def main():
    lost_instance_id = "i-0e2c8c4a218b2fd58"
    if not lost_instance_id:
        raise Exception("Recovery instance is not provided.")
    lost_ec2 = Ec2(lost_instance_id)
    lost_ec2.find()
    lost_ec2.eval()
    key = lost_ec2.generate_key()

    if lost_ec2.state != "stopped":
        lost_ec2.stop()
        for vol in lost_ec2.volumes:
            print(vol)

    temp_ec2 = Ec2()
    temp_ec2.create_instance(key)


if __name__ == '__main__':
    main()
