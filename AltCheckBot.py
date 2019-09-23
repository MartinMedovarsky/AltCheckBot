import praw
from praw.exceptions import APIException
from psaw import PushshiftAPI
import time
from threading import Thread
import json
import os

r = praw.Reddit(client_id=os.environ["client_id"],
                client_secret=os.environ["client_secret"],
                username=os.environ["bot_username"],
                password=os.environ["password"],
                user_agent=os.environ["user_agent"])

#short hand for psaw
api = PushshiftAPI(r)

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
    totalRepliesToComments = 0  # The total comments that suspected user has replied to an owner's comment
    RepliesToCommentsInOwnerThread = 0  # Replies posted by suspected user to owner's comment in owner's thread
    totalMatchingCommentResponse = 0  # Total time taken to post a response
    avgMatchingCommentResponse = 0  # Average time to post a response
    responseUnder15 = 0  # Responses created in under 15 minutes of the original post

    # Loops through the comments posted by the suspected user
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
                totalRepliesToComments += 1
                # Check if the reply to the owner was also in the owner's thread
                if comment.submission.author == owner:
                    RepliesToCommentsInOwnerThread += 1

    avgMatchingCommentResponse = int((totalMatchingCommentResponse / totalMatchingComments))
    print("Findings: Total Comments: " + str(totalCommentsFound))
    print("Matching Comments: " + str(totalMatchingComments))
    print("Average time to post response: " + str(avgMatchingCommentResponse) + "seconds")
    print("Responses under 15 minutes: " + str(responseUnder15))

    # Calculation of likelihood of user being an alt
    altJudgement = ""  # Variable determining how likely its an alt

    judgmentArray = ["Very high chance of " + str(alt) + " being an alt",
                     "High chance of " + str(alt) + " being an alt",
                     "Moderate chance of " + str(alt) + " being an alt",
                     "Low chance of " + str(alt) + " being an alt"]

    criteria = [totalCommentsFound,
                totalMatchingComments,
                totalRepliesToComments,
                RepliesToCommentsInOwnerThread,
                totalMatchingCommentResponse,
                avgMatchingCommentResponse,
                responseUnder15]

    # If statements that try to determine the likelihood of the account being an alt

    if totalCommentsFound < 10:
        altJudgement = "Less than 10 user comments retrieved, not enough data to make a judgement"
    else:
        valA = 0.75
        valB = 0.6
        valC = 0.5

        for i in range(0,2):
            print("FOR LOOP WORKING" + str(i))

            if criteria[1] > (criteria[0] * valA) or criteria[2] > (criteria[0] * valA) or criteria[6] > (criteria[0] * valB):
                altJudgement = judgmentArray[i]
                print("selection made: Iteration 1," + str(i))
                break
            elif criteria[1] > (criteria[0] * valB) and criteria[2] > (criteria[0] * valB):
                altJudgement = judgmentArray[i]
                print("selection made: Iteration 2," + str(i))
                break
            elif criteria[1] > (criteria[0] * valB) and criteria[6] > (criteria[0] * valC):
                altJudgement = judgmentArray[i]
                print("selection made: Iteration 3," + str(i))
                break
            elif criteria[1] > (criteria[0] * valB) and criteria[3] > (criteria[0] * valC):
                altJudgement = judgmentArray[i]
                print("selection made: Iteration 4," + str(i))
                break

            valA -= 0.1
            valB -= 0.1
            valC -= 0.1

        if altJudgement == "":
            print(altJudgement)
            altJudgement = judgmentArray[3]
            print("NOT AN ALT")

    # Bot's reply to the summoning comment
    botReply = ("##Findings about " + str(alt) + ":"
                "\n\n**Total comments** retrieved from " + str(alt) + ": " + str(totalCommentsFound) +
                "\n\n**Comments** posted by " + str(alt) + " in " + str(owner) + "\'s threads: " + str(totalMatchingComments) +
                "\n\n**Replies** made by " + str(alt) + " to comments made by " + str(owner) + ": " + str(totalRepliesToComments) +
                "\n\n**Replies** made by " + str(alt) + " to comments made by " + str(owner) + " in " + str(owner) + "'s threads: " + str(RepliesToCommentsInOwnerThread) +
                "\n\n**Average time taken** by " + str(alt) + " to reply to " + str(owner) + "\'s threads after their creation: " + str(display_time(avgMatchingCommentResponse)) +
                "\n\n**Comments posted** by " + str(alt) + " in " + str(owner) + "\'s threads **less then 15 minutes** after their creation: " + str(responseUnder15) +
                "\n\n**" + altJudgement + "**" +
                "\n\n  ***  \n\n"
                "^(Find out more on my pinned post | Please downvote me if i\'m wrong)")

    # print("Checkpoint3")
    try:
        requestComment.reply(botReply)
    except:
        main()


# look for phrase and reply appropriately

keyphrase = '!altcheck'

def main():
    search_time = time.time()
    while True:
        gen = api.search_comments(after=int(search_time), q=keyphrase)
        newComment = True

        for comment in gen:
            
            #checks that the comment retrieved hasn't already been responded to by bot
            if newComment:
                    search_time = comment.created_utc
                    print (search_time)
                    newComment = False

            owner = comment.body.split(" ")
            print(owner)

            print(comment.submission.author, comment.parent().author.name)

            # Checks that the summon is a reply and not a parent comment
            if comment.submission.author != comment.parent().author.name:

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

                    alt = comment.parent().author.name
                    if owner[1] != alt:
                        print(owner)
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
