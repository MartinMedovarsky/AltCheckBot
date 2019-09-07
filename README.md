# AltCheckBot
AltCheckBot is a Reddit bot used to identify if someone might be using an alternate account

## Instructions for using the bot within Reddit:
Reply `!altcheck` to the comment of a user you suspect to be an alternate account of the original thread's author.

Or

Reply `!altcheck username` to the suspected alt with "username" being the username of the suspected owner. This can be just their username or with a /u/ prefix.

I will then reply to you with the following information:

- The total comments of the alt account I was able to retrieve
- The total amount of comments posted by the alt in posts created by the main account
- The amount of replies made by the alt account to the main account's comments
- The amount of replies made by the alt account to the main account's comments in the main account's threads
- The average time after creation of the main account's posts that it takes the alt to comment
- The amount of comments posted by the alt in the main account's thread within 15 minutes of the post being created
- A judgement giving the likelihood of the account being an alt

**Deleting replies:**

If required, down vote the bot and it will delete its comment after -1 votes

## Guide:

### How to install:

* `git clone` the project
* `pip3 install -r requirements.txt` to install dependencies
* Create a [Reddit app](http://reddit.com/prefs/apps) as script
* Set a valid `username`, `password`, `client_id`, `client_secret` and `user_agent` in the `altCheckBot.py` file or set it through environment variables

### Misc Information:
* The alt judgement function is currently a bit inaccurate as I require more data to set some accurate standards. I'm also quite new to this. 

MIT License


