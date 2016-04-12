__author__ = 'bret'
import subprocess
import boto3
import pycurl
from datetime import datetime, date, time
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

#Variables section
instanceID = StringIO()
c = pycurl.Curl()
c.setopt(c.URL, 'http://169.254.169.254/latest/meta-data/instance-id/')
c.setopt(c.IPRESOLVE, c.IPRESOLVE_V4)
c.setopt(c.WRITEFUNCTION, instanceID.write)
c.perform()
c.close()
instanceID = instanceID.getvalue()

region = StringIO()
r = pycurl.Curl()
r.setopt(r.URL, 'http://169.254.169.254/latest/meta-data/placement/availability-zone/')
r.setopt(r.WRITEFUNCTION, region.write)
r.perform()
r.close()
region = region.getvalue()
aws_region = region[:-1]

amiDescription = 'Daily Snapshot for instance ' + 'instanceID'
client = boto3.client('ec2', region_name=aws_region)

#get the list of drives that need to have their filesystems frozen
listdrives=subprocess.Popen('df' + ' -h', shell=True, stdout=subprocess.PIPE)
listdrives=subprocess.Popen('grep' + ' /dev/', shell=True, stdin=listdrives.stdout, stdout=subprocess.PIPE)
listdrives=subprocess.Popen('grep -v tmpfs', shell=True, stdin=listdrives.stdout, stdout=subprocess.PIPE)
listdrives=subprocess.check_output("awk '{print $6}'", shell=True, stdin=listdrives.stdout)

#sync the filesystem to disk before continuing:
subprocess.call('sync')

#freeze the filesystems
for i,mount in enumerate(listdrives.split()):
    try:
      subprocess.check_output('sudo fsfreeze --freeze ' + mount, shell=True)
    except OSError as e:
      print("mountpoint already frozen.")
      subprocess.check_output('sudo fsfreeze --unfreeze' + mount, shell=True)
      subprocess.check_output('sudo fsfreeze --freeze' + mount, shell=True)
      pass

#timestamp=subprocess.check_output(['/bin/date', '+"%F"'])
timestamp=datetime.utcnow().strftime("%d %b %Y %I.%M%p")
imageName=instanceID+'-'+timestamp
print imageName

#section to create the AMI
try:
  response = client.create_image(
      DryRun=False,
      InstanceId=instanceID,
      Name=imageName,
      Description=amiDescription,
      NoReboot=True)
except botocore.exceptions.ClientError as e:
  if e.response['ResponseMetadata']['HTTPStatusCode'] >= 400 :
      print "error initiating snapshot. Response code= " + e.response['ResponseMetadata']['HTTPStatusCode'] \
            + ".\nRequestId: " + e.response['ResponseMetadata']['RequestId']
  pass

print response

#unfreeze the filesystems
for i,mount in enumerate(listdrives.split()):
  try:
    subprocess.check_output('sudo fsfreeze --unfreeze ' + mount, shell=True)
  except OSError as e:
    print("Error unfreezing mountpoint: " + mount + ". Appears to already be unfrozen. Snapshot dirty. DELETE: "
          + response['ImageId'])
