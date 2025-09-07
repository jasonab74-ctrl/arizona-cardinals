# Cardinals sources + shared helpers for the collector

TEAM = "Arizona Cardinals"

# IMPORTANT:
# Keep ~8–12 reliable sources. Query feeds (Bing/Google) help fill the gaps.
SOURCES = [
    # Team / league
    ("philadelphiaeagles.com (ignore—template check)", "https://www.philadelphiaeagles.com/rss/rss-team-news.xml"),  # harmless if empty
    ("azcardinals.com", "https://www.azcardinals.com/rss/rss-team-news.xml"),
    ("NFL.com — Arizona Cardinals", "https://www.nfl.com/feeds-rs/news/team/arizona-cardinals"),
    # Media
    ("Cards Wire (USA Today)", "https://cardswire.usatoday.com/feed/"),
    ("ESPN — Arizona Cardinals", "https://www.espn.com/espn/rss/nfl/team?team=ari"),
    ("Yahoo Sports — Cardinals", "https://sports.yahoo.com/nfl/teams/ari/rss/"),
    ("SI — All Cardinals", "https://www.si.com/nfl/cardinals/.rss/full/"),
    ("ProFootballTalk — Cardinals", "https://profootballtalk.nbcsports.com/category/teams/nfc/arizona-cardinals/feed/"),
    ("Revenge of the Birds (SB Nation)", "https://www.revengeofthebirds.com/rss/index.xml"),
    # Meta queries
    ("Bing News — Arizona Cardinals", "https://www.bing.com/news/search?q=Arizona+Cardinals&format=rss"),
    ("Google News — Arizona Cardinals", "https://news.google.com/rss/search?q=Arizona+Cardinals"),
]

# Maximum items to keep in items.json
MAX_ITEMS = 50