# feeds.py — Arizona Cardinals sources
# This file is imported by collect.py.  Edit/commit to change sources.

TEAM = "Arizona Cardinals"

# Each source is: (display_name, feed_url_or_query, type)
# type: "rss" for direct feeds, "bing" for Bing News query, "google" for Google News RSS.
# You can comment out any you don’t want.

SOURCES = [
    # Official / team & league
    ("azcardinals.com", "https://www.azcardinals.com/rss/news", "rss"),
    ("NFL.com — Arizona Cardinals", "https://www.nfl.com/rss/rsslanding?searchString=arizona+cardinals", "rss"),

    # USA Today network (Cards Wire)
    ("Cards Wire (USA Today)", "https://cardswire.usatoday.com/feed/", "rss"),

    # ESPN team
    ("ESPN — Cardinals", "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/22/news", "rss"),  # ESPN JSON-as-RSS handled in collect.py

    # Yahoo team (query)
    ("Yahoo Sports — Cardinals", "https://news.google.com/rss/search?q=%22Arizona%20Cardinals%22%20site:sports.yahoo.com&hl=en-US&gl=US&ceid=US:en", "rss"),

    # Sports Illustrated FanNation
    ("SI — All Cardinals", "https://www.si.com/nfl/cardinals/.rss", "rss"),

    # ProFootballTalk (Cardinals tag)
    ("ProFootballTalk — Cardinals", "https://profootballtalk.nbcsports.com/team/arizona-cardinals/feed/", "rss"),

    # SB Nation (Revenge of the Birds)
    ("Revenge of the Birds (SB Nation)", "https://www.revengeofthebirds.com/rss/current", "rss"),

    # NBC Sports – general Cardinals news via Google News (gathers lots of outlets)
    ("Google News — Arizona Cardinals", "https://news.google.com/rss/search?q=%22Arizona%20Cardinals%22&hl=en-US&gl=US&ceid=US:en", "rss"),

    # Bing News query (broad catch-all)
    ("Bing News — Arizona Cardinals", "bing:Arizona Cardinals"),
]

# Buttons shown at the top of the page (label, url)
BUTTONS = [
    ("Schedule", "https://www.azcardinals.com/schedule/"),
    ("Roster", "https://www.azcardinals.com/team/players-roster/"),
    ("Depth Chart", "https://www.ourlads.com/nfldepthcharts/depthchart/ARZ"),
    ("Injury Report", "https://www.azcardinals.com/team/injury-report/"),
    ("Tickets", "https://www.azcardinals.com/tickets/"),
    ("Team Shop", "https://shop.azcardinals.com/"),
    ("Reddit", "https://www.reddit.com/r/azcardinals/"),
    ("Bleacher Report", "https://bleacherreport.com/arizona-cardinals"),
    ("ESPN Team", "https://www.espn.com/nfl/team/_/name/ari/arizona-cardinals"),
    ("Yahoo Team", "https://sports.yahoo.com/nfl/teams/ari/"),
    ("PFF Team Page", "https://www.pff.com/nfl/teams/arizona-cardinals"),
    ("Pro-Football-Reference", "https://www.pro-football-reference.com/teams/crd/"),
    ("NFL Power Rankings", "https://www.nfl.com/news/nfl-power-rankings"),
    ("Stats", "https://www.teamrankings.com/nfl/team/arizona-cardinals"),
    ("Standings", "https://www.nfl.com/standings/league/2024/REG"),
]

# Optional image/logo path used by index.html (keep as-is if you already have it)
LOGO_PATH = "static/logo.png"
TEAM_COLORS = {
    "primary": "#97233F",  # Cardinals red
    "accent":  "#FFC20E",  # gold beak accent
    "dark":    "#121212"
}