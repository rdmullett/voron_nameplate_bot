#!/usr/bin/python3

import praw
import os
import re
import sys
#from voron_nameplates import googledrive
import googledrive
import subprocess

clientID = os.environ["VORON_NAMEPLATE_ID"]
clientSecret = os.environ["VORON_NAMEPLATE_SECRET"]
clientPass = os.environ["VORON_NAMEPLATE_PASS"]
clientAgent = os.environ["VORON_NAMEPLATE_USER_AGENT"]
clientUser = os.environ["VORON_NAMEPLATE_USER"]
regexPattern = 'V.*[^!]'

workingDir = os.getcwd()
sys.path.append(workingDir)

reddit = praw.Reddit(client_id=clientID, client_secret=clientSecret, password=clientPass, user_agent=clientAgent, username=clientUser)

#subreddit = reddit.subreddit("voroncorexy")

#for submission in subreddit.new(limit=5):
#    print("Title: ", submission.title)
#    print("Score: ", submission.score)
#    print("--------------------------\n")

registryuser = reddit.redditor("voron_registry_bot")

def serial_grab_reddit():
    if not os.path.isfile("/nameplates/logs/post_logs.txt"):
        posts_replied_to=[]
    else:
        with open("/nameplates/logs/post_logs.txt", "r") as f:
            posts_replied_to = f.read()
            posts_replied_to = posts_replied_to.split("\n")
            posts_replied_to = list(filter(None, posts_replied_to))
    serials = []
    for comment in registryuser.comments.new(limit=5):
        if comment.submission.id not in posts_replied_to:
            posts_replied_to.append(comment.submission.id)
            print("URL: ", comment.submission.url)
            commentText = comment.body
            print("Comment: ", commentText)
            serialMatches = re.findall(regexPattern, commentText)
            serialNumber = serialMatches[0]
            print("SerialNumber: ", serialNumber)
            print("--------------------------\n")
            serials.append(serialNumber)
        else:
            continue
    with open("/nameplates/logs/post_logs.txt", "w") as f:
        for post_id in posts_replied_to:
            f.write(post_id + "\n")
    return serials

def scad_create(serialList):
    for serial in serialList:
        #For some reason calling the openscad directly from python makes openscad very unhappy. Calling from bash script for now
        if not os.path.isfile("/nameplates/" + serial + ".stl"):
            #TODO: resolve absolute path issue
            subprocess.run(["/home/username/voron_nameplate_bot/voron_nameplates/scadcall.sh", i])
        else:
            continue

def main():
    serials = serial_grab_reddit()
    scad_create(serials)
    service = googledrive.service()
    googledrive.serial_folder_create(service, serials)
    googledrive.serial_stl_upload(service, serials)

if __name__ == '__main__':
    main()

#TODO:
#upload resulting files to google drive

#TODO:
#comment on post with resulting google drive link
