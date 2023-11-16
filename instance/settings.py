import os
import json
from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


# Flask Mail
MAIL_PORT = int(os.environ.get("MAIL_PORT"))
MAIL_USE_TLS = bool(int(os.environ.get("MAIL_USE_TLS")))
MAIL_USE_SSL = bool(int(os.environ.get("MAIL_USE_SSL")))
MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
MAIL_SERVER = os.environ.get("MAIL_SERVER")
MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")

# User
ADMIN_MAIL = os.environ.get("ADMIN_MAIL")
ADMINS = [os.environ.get("ADMIN_MAIL")]
ADMIN_IP = os.environ.get("ADMIN_IP")

# Site Name
SITE_NAME = os.environ.get("SITE_NAME") or "Flask APP"


# Date & Time Format String
DATE_FORMAT = "%d-%m-%Y, %A %I:%M %p"


base_dir = os.path.dirname(os.path.dirname(__file__))
file = os.path.join(base_dir, "app/cricket/limits.json")


with open(file) as f:
    limits = json.load(f)

# Game Limits
MIN_WICKET_KEEPERS = limits["wicket_keepers"]["min"] or 1
MAX_WICKET_KEEPERS = limits["wicket_keepers"]["max"] or 4

MIN_BATSMENS = limits["batsmens"]["min"] or 3
MAX_BATSMENS = limits["batsmens"]["max"] or 6

MIN_ALL_ROUNDERS = limits["all_rounders"]["min"] or 1
MAX_ALL_ROUNDERS = limits["all_rounders"]["max"] or 4

MIN_BOWLERS = limits["bowlers"]["min"] or 3
MAX_BOWLERS = limits["bowlers"]["max"] or 6

MIN_HOME_TEAM_PLAYERS = limits["home_team_players"]["min"] or 4
MAX_HOME_TEAM_PLAYERS = limits["home_team_players"]["max"] or 7

MIN_AWAY_TEAM_PLAYERS = limits["away_team_players"]["min"] or 4
MAX_AWAY_TEAM_PLAYERS = limits["away_team_players"]["max"] or 7

MAX_PLAYERS = limits["max_players"] or 11
MAX_CREDITS = limits["max_credits"] or 100
