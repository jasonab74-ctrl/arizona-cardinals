# -------------------------------
# Arizona Cardinals — feeds.py
# -------------------------------

TEAM_NAME = "Arizona Cardinals"

# Feeds: favor official + reputable outlets; include 1-2 news queries
FEEDS = [
    # Official / league
    {"name": "azcardinals.com", "url": "https://www.azcardinals.com/rss"},           # official
    {"name": "NFL.com — Arizona Cardinals", "url": "https://www.nfl.com/feeds-rs/team/arizona-cardinals/rss.xml"},

    # National outlets (team sections)
    {"name": "ESPN — Arizona Cardinals", "url": "https://www.espn.com/blog/arizona-cardinals/rss"},
    {"name": "Yahoo Sports — Arizona Cardinals", "url": "https://sports.yahoo.com/nfl/teams/ari/rss/"},
    {"name": "Bleacher Report — Arizona Cardinals", "url": "https://feeds.feedburner.com/ArizonaCardinals"},
    {"name": "USA Today — Cards Wire", "url": "https://cardswire.usatoday.com/feed/"},
    {"name": "ProFootballTalk — Cardinals", "url": "https://profootballtalk.nbcsports.com/team/arizona-cardinals/feed/"},
    {"name": "Sports Illustrated — All Cardinals", "url": "https://www.si.com/nfl/cardinals/.rss"},  # SI FanNation

    # Local / SB Nation
    {"name": "Revenge of the Birds", "url": "https://www.revengeofthebirds.com/rss/index.xml"},

    # Broad news queries (backfill)
    {"name": "Bing News — Arizona Cardinals", "url": "https://www.bing.com/news/search?q=%22Arizona+Cardinals%22&format=RSS"},
    {"name": "Google News — Arizona Cardinals", "url": "https://news.google.com/rss/search?q=%22Arizona+Cardinals%22"},
]

# Quick links (buttons)
STATIC_LINKS = [
    {"label": "Schedule", "url": "https://www.azcardinals.com/schedule/"},
    {"label": "Roster", "url": "https://www.azcardinals.com/team/"},
    {"label": "Depth Chart", "url": "https://www.espn.com/nfl/team/depth/_/name/ari"},
    {"label": "Injury Report", "url": "https://www.azcardinals.com/team/injury-report/"},
    {"label": "Tickets", "url": "https://www.azcardinals.com/tickets/"},
    {"label": "Team Shop", "url": "https://shop.azcardinals.com/"},
    {"label": "Reddit", "url": "https://www.reddit.com/r/azcardinals/"},
    {"label": "Bleacher Report", "url": "https://bleacherreport.com/arizona-cardinals"},
    {"label": "ESPN Team", "url": "https://www.espn.com/nfl/team/_/name/ari/arizona-cardinals"},
    {"label": "Yahoo Team", "url": "https://sports.yahoo.com/nfl/teams/arizona/"},
    {"label": "PFF Team Page", "url": "https://www.pff.com/nfl/teams/arizona-cardinals"},
    {"label": "Pro-Football-Reference", "url": "https://www.pro-football-reference.com/teams/crd/"},
    {"label": "NFL Power Rankings", "url": "https://www.nfl.com/news/power-rankings"},
    {"label": "Stats", "url": "https://www.nfl.com/teams/arizona-cardinals/stats"},
    {"label": "Standings", "url": "https://www.nfl.com/standings/league/2025/REG"},
]