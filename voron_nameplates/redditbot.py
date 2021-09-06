#!/usr/bin/python3

import praw
import os
import re
import sys
import time
#from voron_nameplates import googledrive
import googledrive
import subprocess
import argparse

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

def parse_args():
    parser = argparse.ArgumentParser("This is a reddit bot that generates a nameplate for every new Voron serial number on /r/voroncorexy and provide it via a comment.")
    parser.add_argument("-d", "--dry", help='Dry run to test functionality and avoid uploading to Google or making a comment on Reddit.', action='store_true')
    parser.add_argument("-p", "--prod", help='Dry run to test functionality and avoid uploading to Google or making a comment on Reddit.', action='store_true')
    args = parser.parse_args()
    return args

def serial_grab_reddit(runpath):
    if not os.path.isfile(runpath + "logs/post_logs.txt"):
        postsRepliedTo=[]
    else:
        with open(runpath + "logs/post_logs.txt", "r") as f:
            postsRepliedTo = f.read()
            postsRepliedTo = postsRepliedTo.split("\n")
            postsRepliedTo = list(filter(None, postsRepliedTo))
            f.close()
    serials = []
    redditURLS = {}
    for comment in registryuser.comments.new(limit=150):
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

def scad_create(serialList, runpath):
    for serial in serialList:
        #For some reason calling the openscad directly from python makes openscad very unhappy. Calling from bash script for now
        if not os.path.isfile(runpath + serial + ".stl"):
            subprocess.run(["scadcall.sh", serial, runpath])
        else:
            continue

def comment_create(googDict, redDict):
    for key, value in googDict.items():
        reddit_post = redDict[key][0]
        googleURL = googDict[key][0]
        comment = "Congratulations on your serial! I generated a nameplate for your build that you can download here:\n\n" + googleURL + "\n\nIf there are issues with this bot please contact /u/iDuumb."
        print(comment)
        with open("/nameplates/logs/post_logs.txt", "a") as f:
            f.write(reddit_post + "\n")
            f.close()
        submission = reddit.submission(url="https://www.reddit.com/comments/" + reddit_post)
        submission.reply(comment)
        time.sleep(610)

def dry_run():
    runpath = "/dry-run/"
    serials, redditURLS = serial_grab_reddit(runpath)
    scad_create(serials, runpath)
    
def production_run():
    runpath = "/nameplates/"
    serials, redditURLS = serial_grab_reddit(runpath)
    scad_create(serials, runpath)
    googledrive.serial_folder_create(service, serials)
    googURLS = googledrive.serial_stl_upload(service, serials)
    comment_create(googURLS, redditURLS)

def main():
    options = parse_args()
    if options.dry:
        dry_run()
    elif options.prod:
        production_run()
    else:
        exit()

if __name__ == '__main__':
    main()
