#!/bin/bash

#Since this will only be installed on a single PC, this script is quite basic, but is a good reference for the steps that need to be done. In the future ideally this can be converted to be properly packaged, but for now this works. Intended only to be run on RHEL/Fedora based machines (again, this is only for a single bot). The only thing that this does not handle is the required environment variables. The following are the required env variables:

#VORON_NAMEPLATE_ID
#VORON_NAMEPLATE_SECRET
#VORON_NAMEPLATE_PASS
#VORON_NAMEPLATE_USER_AGENT
#VORON_NAMEPLATE_USER

mkdir -p /nameplates/logs
cd /
git clone https://github.com/rdmullett/voron_serial_plate/
yum -y install git python3-pip openscad
pip install praw apiclient google-api-python-client google-auth-httplib2 google-auth-oauthlib

