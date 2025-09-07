# feeds.py — Arizona Cardinals sources + buttons

FEEDS = [
    # Official / league
    {"name": "azcardinals.com", "url": "https://www.azcardinals.com/rss", "trusted": True},

    # National/team-specific
    {"name": "ESPN — Arizona Cardinals", "url": "https://www.espn.com/blog/arizona-cardinals/rss", "trusted": True},
    {"name": "Yahoo Sports — Arizona Cardinals", "url": "https://sports.yahoo.com/nfl/teams/ari/rss/"},
    {"name": "USA Today — Cardinals Wire", "url": "https://cardswire.usatoday.com/feed/", "trusted": True},
    {"name": "SB Nation — Revenge of the Birds", "url": "https://www.revengeofthebirds.com/rss/index.xml"},
    {"name": "AZCentral — Cardinals", "url": "https://www.azcentral.com/sports/cardinals/rss/"},
    {"name": "Bleacher Report — Arizona Cardinals", "url": "https://bleacherreport.com/arizona-cardinals.rss"},

    # Backstops so the page is never empty
    {"name": "Google News — \"Arizona Cardinals\"", "url": "https://news.google.com/rss/search?q=%22Arizona+Cardinals%22&hl=en-US&gl=US&ceid=US:en"},
    {"name": "Google News — Kyler Murray", "url": "https://news.google.com/rss/search?q=%22Kyler+Murray%22+Cardinals&hl=en-US&gl=US&ceid=US:en"},
]

STATIC_LINKS = [
    {"label": "Schedule",  "url": "https://www.azcardinals.com/schedule/"},
    {"label": "Roster",    "url": "https://www.azcardinals.com/team/players-roster/"},
    {"label": "Depth Chart","url": "https://www.ourlads.com/nfldepthcharts/depthchart/ARZ"},
    {"label": "Injury Report","url": "https://www.azcardinals.com/team/injury-report/"},
    {"label": "Tickets",   "url": "https://www.azcardinals.com/tickets/"},
    {"label": "Team Shop", "url": "https://shop.azcardinals.com/"},
    {"label": "Reddit",    "url": "https://www.reddit.com/r/azcardinals/"},
    {"label": "Bleacher Report", "url": "https://bleacherreport.com/arizona-cardinals"},
    {"label": "ESPN Team", "url": "https://www.espn.com/nfl/team/_/name/ari/arizona-cardinals"},
    {"label": "Yahoo Team","url": "https://sports.yahoo.com/nfl/teams/ari/"},
    {"label": "PFF Team Page","url": "https://www.pff.com/nfl/teams/arizona-cardinals"},
    {"label": "Pro-Football-Reference","url": "https://www.pro-football-reference.com/teams/crd/"},
    {"label": "NFL Power Rankings","url": "https://www.nfl.com/news/power-rankings"},
    {"label": "Stats","url": "https://www.nfl.com/teams/arizona-cardinals/stats/"},
    {"label": "Standings","url": "https://www.nfl.com/standings/league/"},
]