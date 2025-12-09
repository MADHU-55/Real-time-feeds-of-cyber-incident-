# backend/collector/collector_sources.py

SOURCES = [
    {
        "name": "CERT-IN",
        "url": "https://www.cert-in.org.in/RSS_Feed.xml",
        "category": "Cyber Alert"
    },
    {
        "name": "CISA",
        "url": "https://www.cisa.gov/cybersecurity-advisories/all.xml",
        "category": "Cyber Advisory"
    },
    {
        "name": "NCIIPC",
        "url": "https://nciipc.gov.in/documents/rss.xml",
        "category": "Critical Infrastructure"
    },
    {
        "name": "ENISA Threat Feeds",
        "url": "https://www.enisa.europa.eu/media/news-items/RSS",
        "category": "Threat Intelligence"
    },
    {
        "name": "TheHackerNews",
        "url": "https://feeds.feedburner.com/TheHackersNews",
        "category": "Cyber News"
    },
    {
        "name": "BleepingComputer",
        "url": "https://www.bleepingcomputer.com/feed/",
        "category": "Cyber News"
    },
    {
        "name": "SecurityWeek",
        "url": "https://feeds.feedburner.com/securityweek",
        "category": "Security Research"
    },
    {
        "name": "KrebsOnSecurity",
        "url": "https://krebsonsecurity.com/feed/",
        "category": "Security Research"
    }
]
