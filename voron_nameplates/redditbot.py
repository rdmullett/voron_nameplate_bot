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
        postsRepliedTo=[]
    else:
        with open("/nameplates/logs/post_logs.txt", "r") as f:
            postsRepliedTo = f.read()
            postsRepliedTo = postsRepliedTo.split("\n")
            postsRepliedTo = list(filter(None, postsRepliedTo))
            f.close()
    serials = []
    redditURLS = {}
    for comment in registryuser.comments.new(limit=100):
        if comment.submission.id not in postsRepliedTo:
            postsRepliedTo.append(comment.submission.id)
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
#TODO: remove the following comments when ready to post again
        comment = "Congratulations on your serial! I generated a nameplate for your build that you can download here:\n\n" + googleURL + "\n\nIf there are issues with this bot please contact /u/iDuumb."
        print(comment)
        with open("/nameplates/logs/post_logs.txt", "a") as f:
            f.write(reddit_post + "\n")
            f.close()
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
