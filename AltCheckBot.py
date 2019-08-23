import praw
from praw.exceptions import APIException
import time
from threading import Thread
import json

with open('secret.json', 'r') as f:
    secret = json.load(f)

r = praw.Reddit(client_id=secret["client_id"],
                client_secret=secret["client_secret"],
                username=secret["username"],
                password=secret["password"],
                user_agent=secret["user_agent"])

subreddit = r.subreddit('RoomDecoration')

keyphrase = '!altcheck'

# Function to convert seconds into something legible
intervals = (
    ('weeks', 604800),
    ('days', 86400),
    ('hours', 3600),
    ('minutes', 60),
    ('seconds', 1),)


def display_time(seconds, granularity=2):
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])


# Checks what posts of the owner's account the alt has commented on
def sharedComments(alt, owner, requestComment):
    rawComments = r.redditor(alt).comments.new(limit=100)
    print("RAW COMMENTS RETRIEVED")

    totalCommentsFound = 0  # The total comments the suspected user has posted
    totalMatchingComments = 0  # The total comments that suspected user has posted on the owner's submissions
    totalReplysToComments = 0  # The total comments that suspected user has replyed to an owner's comment
    ReplysToCommentsInOwnerThread = 0  # Replies posted by suspected user to owner's comment in owner's thread
    totalMatchingCommentResponse = 0  # Total time taken to post a response
    avgMatchingCommentResponse = 0  # Average time to post a response
    responseUnder15 = 0  # Responses created in under 10 minutes of the original post

    # Loops through the comments posted by the suspected user
    # print("Checkpoint2")
    for comment in rawComments:
        print("LOOP ITERATION")
        totalCommentsFound += 1
        if comment.submission.author == owner:
            totalMatchingComments += 1

            # Adds the response time to total in seconds
            totalMatchingCommentResponse += (comment.created - comment.submission.created)
            if (comment.created - comment.submission.created) < 900:
                responseUnder15 += 1

        # Checks that the parent attribute is present (if its a reply or parent comment)
        if hasattr(comment.parent().author, "name"):
            # Checks to see if the suspected alt has replied to a comment made by the owner
            if comment.parent().author.name == owner and comment.parent_id != comment.link_id:
                totalReplysToComments += 1
                # Check if the reply to the owner was also in the owner's thread
                if comment.submission.author == owner:
                    ReplysToCommentsInOwnerThread += 1

    avgMatchingCommentResponse = int((totalMatchingCommentResponse / totalMatchingComments))
    print("Findings: Total Comments: " + str(totalCommentsFound))
    print("Matching Comments: " + str(totalMatchingComments))
    print("Average time to post response: " + str(avgMatchingCommentResponse) + "seconds")
    print("Responses under 15 minutes: " + str(responseUnder15))

    # Bot's reply to the summoning comment
    botReply = ("##Findings about " + str(alt) + ":"
                "\n\n**Total comments** retrieved from " + str(alt) + ": " + str(totalCommentsFound) +
                "\n\n**Comments** posted by " + str(alt) + " in " + str(owner) + "\'s threads: " + str(totalMatchingComments) +
                "\n\n**Replies** made by " + str(alt) + " to comments made by " + str(owner) + ": " + str(totalReplysToComments) +
                "\n\n**Replies** made by " + str(alt) + " to comments made by " + str(owner) + " in " + str(owner) + "'s threads: " + str(ReplysToCommentsInOwnerThread) +
                "\n\n**Average time taken** by " + str(alt) + " to reply to " + str(owner) + "\'s threads after their creation: " + str(display_time(avgMatchingCommentResponse)) +
                "\n\n**Comments posted** by " + str(alt) + " in " + str(owner) + "\'s threads **less then 15 minutes** after their creation: " + str(responseUnder15) +
                "\n\n  ***  \n\n"
                "^(Find out more about this bot [here](https://www.reddit.com/user/AltCheckBot/comments/csg0z1/bot_information/) | Please downvote me if i\'m wrong)")

    # print("Checkpoint3")
    requestComment.reply(botReply)


# look for phrase and reply appropriately
def main():
    for comment in subreddit.stream.comments(skip_existing=True):
        if keyphrase in comment.body:
            owner = comment.body.split(" ")
            print(owner)

            # Checks that the summon is a reply and not a parent comment
            if hasattr(comment.parent().author, "name"):

                # Checks if the bot has been called with a specified owner
                if len(owner) == 1:
                    print("No suggested user")
                    alt = comment.parent().author.name
                    owner = comment.submission.author
                    requestComment = comment
                    sharedComments(alt, owner, requestComment)

                # Ensures that the suggested owner is an existing account
                else:
                    owner[1] = owner[1].replace("/u/", "")
                    try:
                        # If account is suspended
                        if getattr(r.redditor(owner[1]), 'is_suspended', False):
                            continue
                    except:
                        print("error caught, broke out")
                        continue

                print(owner)
                alt = comment.parent().author.name
                requestComment = comment
                sharedComments(alt, owner[1], requestComment)


# Function used to check and delete the bot's comments under -2 votes
def deleteBadComment():
    while True:
        print("DELETECOMMENTFUNCTIONWORKING")
        AltCheckComments = r.redditor("AltCheckBot").comments.new(limit=100)
        for comment in AltCheckComments:
            if comment.score < 0:
                comment.delete()
                print("comment Deleted")
        time.sleep(30)

# Starts running the two functions
if __name__ == '__main__':
    print("THEPROGRAMISWORKING")
    Thread(target=main).start()
    Thread(target=deleteBadComment).start()
