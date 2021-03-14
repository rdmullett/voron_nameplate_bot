#!/usr/bin/python3

import praw
import os
import re
import sys
import time
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
    redditURLS = {}
    for comment in registryuser.comments.new(limit=1):
        if comment.submission.id not in posts_replied_to:
            posts_replied_to.append(comment.submission.id)
            print("URL: ", comment.submission.url)
            print("ID: ", comment.id)
            commentText = comment.body
            print("Comment: ", commentText)
            serialMatches = re.findall(regexPattern, commentText)
            serialNumber = serialMatches[0]
            print("SerialNumber: ", serialNumber)
            print("--------------------------\n")
            serials.append(serialNumber)
            redditURLS[serialNumber] = [comment.submission.id]
        else:
            continue
    with open("/nameplates/logs/post_logs.txt", "w") as f:
        for post_id in posts_replied_to:
            f.write(post_id + "\n")
    return serials, redditURLS

def scad_create(serialList):
    for serial in serialList:
        #For some reason calling the openscad directly from python makes openscad very unhappy. Calling from bash script for now
        if not os.path.isfile("/nameplates/" + serial + ".stl"):
            subprocess.run(["scadcall.sh", serial])
        else:
            continue

def comment_create(googDict, redDict):
    for key, value in googDict.items():
        reddit_post = redDict[key][0]
        googleURL = googDict[key][0]
        comment = "Congratulations on your serial! I generated a nameplate for your build that you can download here:\n" + googleURL + "\nIf there are issues with this bot please contact /u/iDuumb."
        print(comment)
        submission = reddit.submission(url="https://www.reddit.com/comments/" + reddit_post)
        submission.reply(comment)
        time.sleep(610)

def main():
    serials, redditURLS = serial_grab_reddit()
    scad_create(serials)
    service = googledrive.service()
    googledrive.serial_folder_create(service, serials)
    googURLS = googledrive.serial_stl_upload(service, serials)
    comment_create(googURLS, redditURLS) 

if __name__ == '__main__':
    main()

#TODO:
#comment on post with resulting google drive link
