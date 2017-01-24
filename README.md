# MBusVoice
# Setup Alexa Lambda Instructions:
- Setup virtualenv for python2.7
- Update ssl and other dependencies for upcoming python packages: sudo apt-get install build-essential libssl-dev libffi-dev python-dev
- Clone Repo
- Activate your virtualenv
- Install requirements.txt from the repo
- Configure awscli: aws configure (ask Mike for a new credential set from aws account), region = us-east-1, output format = N/A
Setup thus far will allow you to push changes to the alexa application to the aws lambda endpoint of our application. This can be done by executing: zappa update dev
# Setup Development
- Discuss as team
- ngrok
