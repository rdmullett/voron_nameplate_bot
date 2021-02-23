#!/usr/bin/python3

import praw
import os
import re

clientID = os.environ["VORON_NAMEPLATE_ID"]
clientSecret = os.environ["VORON_NAMEPLATE_SECRET"]
clientPass = os.environ["VORON_NAMEPLATE_PASS"]
clientAgent = os.environ["VORON_NAMEPLATE_USER_AGENT"]
clientUser = os.environ["VORON_NAMEPLATE_USER"]
regexPattern = 'V.*[^!]'

reddit = praw.Reddit(client_id=clientID, client_secret=clientSecret, password=clientPass, user_agent=clientAgent, username=clientUser)

#subreddit = reddit.subreddit("voroncorexy")

#for submission in subreddit.new(limit=5):
#    print("Title: ", submission.title)
#    print("Score: ", submission.score)
#    print("--------------------------\n")

registryuser = reddit.redditor("voron_registry_bot")

for comment in registryuser.comments.new(limit=25):
    print("URL: ", comment.link_id)
    commentText = comment.body
    print("Comment: ", commentText)
    serialMatches = re.findall(regexPattern, commentText)
    serialNumber = serialMatches[0]
    print("SerialNumber: ", serialNumber)
    print("--------------------------\n")
