# feeds.py — Arizona Cardinals
# Defines (1) news feeds the collector reads and (2) quick-link buttons for the UI.

TEAM_NAME = "Arizona Cardinals"

# News sources (shown in the Sources dropdown; also used for filtering labels)
# We lean on reliable RSS and Google News domain queries so it never runs empty.
FEEDS = [
    # Broad aggregators (high volume, good backfill)
    {"name": "Google News — \"Arizona Cardinals\"", "url": "https://news.google.com/rss/search?q=%22Arizona+Cardinals%22&hl=en-US&gl=US&ceid=US:en"},
    {"name": "Bing News — Arizona Cardinals",       "url": "https://www.bing.com/news/search?q=%22Arizona+Cardinals%22&format=rss"},

    # Official / league
    {"name": "azcardinals.com (official)",          "url": "https://news.google.com/rss/search?q=site%3Aazcardinals.com+%22Arizona+Cardinals%22&hl=en-US&gl=US&ceid=US:en"},
    {"name": "NFL.com — Arizona Cardinals",         "url": "https://news.google.com/rss/search?q=site%3Anfl.com+%22Arizona+Cardinals%22&hl=en-US&gl=US&ceid=US:en"},

    # National outlets (team sections)
    {"name": "ESPN — Arizona Cardinals",            "url": "https://news.google.com/rss/search?q=site%3Aespn.com+%22Arizona+Cardinals%22&hl=en-US&gl=US&ceid=US:en"},
    {"name": "Yahoo Sports — Arizona Cardinals",    "url": "https://news.google.com/rss/search?q=site%3Asports.yahoo.com+%22Arizona+Cardinals%22&hl=en-US&gl=US&ceid=US:en"},
    {"name": "Bleacher Report — Arizona Cardinals", "url": "https://news.google.com/rss/search?q=site%3Ableacherreport.com+%22Arizona+Cardinals%22&hl=en-US&gl=US&ceid=US:en"},
    {"name": "ProFootballTalk — Cardinals",         "url": "https://news.google.com/rss/search?q=site%3Aprofootballtalk.nbcsports.com+Cardinals&hl=en-US&gl=US&ceid=US:en"},

    # Team/beat sites with stable feeds
    {"name": "Cards Wire (USA Today)",              "url": "https://cardswire.usatoday.com/feed/"},
    {"name": "Revenge of the Birds (SB Nation)",    "url": "https://www.revengeofthebirds.com/rss/index.xml"},
    {"name": "SI — All Cardinals",                  "url": "https://www.si.com/nfl/cardinals/rss"}
]

# Quick-link buttons across the top (appear in the UI immediately)
STATIC_LINKS = [
    {"label": "Schedule",   "url": "https://www.azcardinals.com/schedule/"},
    {"label": "Roster",     "url": "https://www.azcardinals.com/team/players-roster/"},
    {"label": "Depth Chart","url": "https://www.ourlads.com/nfldepthcharts/depthchart/ARZ"},
    {"label": "Injury Report","url": "https://www.azcardinals.com/team/injury-report/"},
    {"label": "Tickets",    "url": "https://www.azcardinals.com/tickets/"},
    {"label": "Team Shop",  "url": "https://shop.azcardinals.com/"},
    {"label": "Reddit",     "url": "https://www.reddit.com/r/azcardinals/"},
    {"label": "Bleacher Report", "url": "https://bleacherreport.com/arizona-cardinals"},
    {"label": "ESPN Team",  "url": "https://www.espn.com/nfl/team/_/name/ari/arizona-cardinals"},
    {"label": "Yahoo Team", "url": "https://sports.yahoo.com/nfl/teams/ari/"},
    {"label": "PFF Team Page","url": "https://www.pff.com/nfl/teams/arizona-cardinals"},
    {"label": "Pro-Football-Reference","url": "https://www.pro-football-reference.com/teams/crd/"},
    {"label": "NFL Power Rankings","url": "https://www.nfl.com/news/power-rankings"},
    {"label": "Stats","url": "https://www.nfl.com/teams/arizona-cardinals/stats/"},
    {"label": "Standings","url": "https://www.nfl.com/standings/league/"}
]