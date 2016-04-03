# Brief overview

The purpose of this tool is to allow you to create an AMI of your ec2 instance without needing to restart the server. 
Additionally, this ensures data integrity as it freezes the filesystem of each server when it executes. 
You can set this up in a cron job, which will be described later, but this can also be executed on an as-needed basis.
Currently, this needs to be run on the local server in which you are attempting to back up. However, in a future release,
this will hopefully be converted into a lambda function, which will ease the effort in backing everything up.

# Restrictions/Warnings

Use at your own risk. This software comes with no guarantee or support and is not endorsed by AWS or Amazon.
The current iteration of this software will fail if there is no proper response from the API. In the case of an error
returned by the API, you will need to issue a reboot of the instance.

Also, this tool will utilize S3 (via creating snapshots of your attached volumes). You are responsible for the costs 
incurred by using this tool. It will be billed under ebs snapshot usage in each region on your bill.

This tool will also currently only use/read the "default" profile in the credentials and config files. If you have a 
different account configured as the default, this tool will fail to call the API properly if you are not using STS 
credentials.

Additional warning: you must have sudo privileges (ie. ec2-user, ubuntu, centos, or root) to be able to execute the
freeze and unfreeze portion of the code. As such, you need to ensure that you grab the package using the user with sudo
privileges.

# Requirements

Python 2.7
  Modules needed:
    pycurl
    StringIO
    boto3
      
AWS Credentials file OR server needs a role with a profile that can do the following:
  createImage
  createSnapshot

Boto3 reads from environment variables first, then reads from ~/.aws/credentials and ~/.aws/config, then it looks within
the actual program in case settings are declared there. You only need to have the awscli installed and configured OR you
need STS credentials via IAM role to use this program.

Additionally, This needs to be executed by a user that has passwordless sudo privileges (or root privileges) as this
tool needs to execute a filesystem freeze, otherwise, the calls will fail and the program will exit.

# Basic instructions

You can create a cron file that looks something like this (I'm running my cron at 3am every day): 

```cron
* 3 * * * /usr/bin/python2 ~/github/AWS_EC2_BACKUP/ec2_backup.py
```

Make sure the file is executable:

```
chmod +x ~/github/AWS_EC2_BACKUP/ec2_backup.py
```

You can manually run the program like this:

```
python2 ~/github/AWS_EC2_BACKUP/ec2_backup.py
```

Depending on the system, this may have different syntax:

```
python2.7 ~/github/AWS_EC2_BACKUP/ec2_backup.py
```
OR
```
python27 ~/github/AWS_EC2_BACKUP/ec2_backup.py
```

Make sure you have a credentials file (if you are not using an IAM role) in the following location:
```~/.aws/credentials```