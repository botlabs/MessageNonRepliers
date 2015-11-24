import sys
import praw
import requests

# Account settings (private)
USERNAME = ''
PASSWORD = ''

# OAuth settings (private)
CLIENT_ID = ''
CLIENT_SECRET = ''
REDIRECT_URI = 'http://127.0.0.1:65010/authorize_callback'

# Configuration Settings
REDDITORS_FILE = "redditors.txt"
USER_AGENT = "Thread comment reminder"
AUTH_TOKENS = ["identity", "read", "privatemessages"]
SUBJECT = "You haven't yet replied!"
MESSAGE_TEMPLATE = """
This is a reminder that you haven't yet commented on the following thread:

[{title}]({link})
"""

def get_access_token():
    response = requests.post("https://www.reddit.com/api/v1/access_token",
      # client id and client secret are obtained via your reddit account
      auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
      # provide your reddit user id and password
      data = {"grant_type": "password", "username": USERNAME, "password": PASSWORD},
      # you MUST provide custom User-Agent header in the request to play nicely with Reddit API guidelines
      headers = {"User-Agent": USER_AGENT})
    response = dict(response.json())
    return response["access_token"]

def get_praw():
    r = praw.Reddit(USER_AGENT)
    r.set_oauth_app_info(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
    r.set_access_credentials(set(AUTH_TOKENS), get_access_token())
    return r

def main(r, url):
    try:
        # Load redditors
        with open(REDDITORS_FILE) as f:
            redditors = [i.strip() for i in f.read().split("\n") if i is not ""]

        post = r.get_submission(url=url, comment_limit=None)
        repliers = [c.author for c in post.comments]
        repliers = [c.name for c in repliers if c is not None]
        nonrepliers = list(set(redditors) - set(repliers))
        for user in nonrepliers:
            r.send_message(user, SUBJECT, MESSAGE_TEMPLATE.format(user=user, title=post.title, link=post.permalink))

    except praw.errors.OAuthInvalidToken:
        print("Error: OAuth token expired.")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        exit("Usage: " + sys.argv[0] + " <url>")
    else:
        main(get_praw(), sys.argv[1])
