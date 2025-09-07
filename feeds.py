# feeds.py — Arizona Cardinals

FEEDS = [
    # Broad news (high volume)
    {"name": "Google News — Arizona Cardinals",
     "url": "https://news.google.com/rss/search?q=%22Arizona+Cardinals%22&hl=en-US&gl=US&ceid=US:en"},
    {"name": "Bing News — Arizona Cardinals",
     "url": "https://www.bing.com/news/search?q=%22Arizona+Cardinals%22&format=rss"},

    # Team/beat outlets (reliable RSS)
    {"name": "Cards Wire (USA Today)", "url": "https://cardswire.usatoday.com/feed/"},
    {"name": "Revenge of the Birds (SB Nation)", "url": "https://www.revengeofthebirds.com/rss/index.xml"},
    {"name": "SI — All Cardinals", "url": "https://www.si.com/nfl/cardinals/rss"},
    {"name": "ProFootballTalk — Cardinals", "url": "https://profootballtalk.nbcsports.com/team/arizona-cardinals/feed/"},
]

# Quick-link buttons shown across the top of the page
STATIC_LINKS = [
    {"label": "Schedule", "url": "https://www.azcardinals.com/schedule/"},
    {"label": "Roster", "url": "https://www.azcardinals.com/team/roster/"},
    {"label": "Depth Chart", "url": "https://www.azcardinals.com/team/depth-chart/"},
    {"label": "Injury Report", "url": "https://www.azcardinals.com/team/injury-report/"},
    {"label": "Tickets", "url": "https://www.azcardinals.com/tickets/"},
    {"label": "Team Shop", "url": "https://shop.azcardinals.com/"},
    {"label": "Reddit", "url": "https://www.reddit.com/r/azcardinals/"},
    {"label": "Bleacher Report", "url": "https://bleacherreport.com/arizona-cardinals"},
    {"label": "ESPN Team", "url": "https://www.espn.com/nfl/team/_/name/ari/arizona-cardinals"},
    {"label": "Yahoo Team", "url": "https://sports.yahoo.com/nfl/teams/ari/"},
    {"label": "PFF Team Page", "url": "https://www.pff.com/nfl/teams/arizona-cardinals"},
    {"label": "Pro-Football-Reference", "url": "https://www.pro-football-reference.com/teams/crd/"},
    {"label": "NFL Power Rankings", "url": "https://www.nfl.com/news/power-rankings"},
    {"label": "Stats", "url": "https://www.espn.com/nfl/team/stats/_/name/ari/arizona-cardinals"},
    {"label": "Standings", "url": "https://www.nfl.com/standings/league/2025/REG"},
]