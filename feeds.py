# feeds.py — Arizona Cardinals (NFL-tailored)
# This file is imported by collect.py to build items.json

FEEDS = [
    # Google News queries (reliable RSS, good recency)
    {
        "name": "Google News — Arizona Cardinals",
        "url": "https://news.google.com/rss/search?q=%22Arizona%20Cardinals%22%20OR%20Cardinals%20NFL&hl=en-US&gl=US&ceid=US:en",
    },

    # Yahoo via Google News query (team tag pages often lack RSS)
    {
        "name": "Yahoo Sports — Cardinals",
        "url": "https://news.google.com/rss/search?q=site:sports.yahoo.com%20%22Arizona%20Cardinals%22&hl=en-US&gl=US&ceid=US:en",
    },

    # Official team site (if their RSS is unavailable, we fall back to Google News scoped to site)
    {
        "name": "azcardinals.com",
        "url": "https://news.google.com/rss/search?q=site:azcardinals.com%20%22Arizona%20Cardinals%22&hl=en-US&gl=US&ceid=US:en",
    },

    # SB Nation: Revenge of the Birds (RSS available)
    {
        "name": "Revenge of the Birds",
        "url": "https://www.revengeofthebirds.com/rss/index.xml",
    },

    # Arizona Sports (station site feed; Cardinals items appear in main feed)
    {
        "name": "Arizona Sports",
        "url": "https://arizonasports.com/feed/",
    },

    # ESPN team via scoped query (team pages no team-specific RSS)
    {
        "name": "ESPN — Cardinals",
        "url": "https://news.google.com/rss/search?q=site:espn.com%20%22Arizona%20Cardinals%22&hl=en-US&gl=US&ceid=US:en",
    },

    # CBS Sports team via scoped query
    {
        "name": "CBS Sports — Cardinals",
        "url": "https://news.google.com/rss/search?q=site:cbssports.com%20%22Arizona%20Cardinals%22&hl=en-US&gl=US&ceid=US:en",
    },

    # USA Today “Cards Wire” (site feed – lots of Cards)
    {
        "name": "Cards Wire (USA Today)",
        "url": "https://cardswire.usatoday.com/feed/",
    },

    # ProFootballTalk scoped to Cards
    {
        "name": "ProFootballTalk — Cardinals",
        "url": "https://news.google.com/rss/search?q=site:profootballtalk.nbcsports.com%20%22Arizona%20Cardinals%22&hl=en-US&gl=US&ceid=US:en",
    },
]