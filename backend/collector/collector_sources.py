# backend/collector/collector_sources.py

SOURCES = [
    # ================= GOVERNMENT / NATIONAL =================
    {
        "name": "CERT-IN",
        "url": "https://www.cert-in.org.in/RSS_Feed.xml",
        "category": "Government Advisory"
    },
    {
        "name": "CISA Advisories",
        "url": "https://www.cisa.gov/cybersecurity-advisories/all.xml",
        "category": "Government Advisory"
    },
    {
        "name": "US-CERT Alerts",
        "url": "https://www.cisa.gov/news.xml",
        "category": "Government Alert"
    },
    {
        "name": "NCIIPC",
        "url": "https://nciipc.gov.in/documents/rss.xml",
        "category": "Critical Infrastructure"
    },

    # ================= INTERNATIONAL AGENCIES =================
    {
        "name": "ENISA",
        "url": "https://www.enisa.europa.eu/media/news-items/RSS",
        "category": "Threat Intelligence"
    },
    {
        "name": "NCSC UK",
        "url": "https://www.ncsc.gov.uk/api/1/services/v1/all-rss-feed.xml",
        "category": "Government Advisory"
    },

    # ================= HIGH-FREQUENCY CYBER NEWS =================
    {
        "name": "The Hacker News",
        "url": "https://feeds.feedburner.com/TheHackersNews",
        "category": "Cyber News"
    },
    {
        "name": "BleepingComputer",
        "url": "https://www.bleepingcomputer.com/feed/",
        "category": "Cyber News"
    },
    {
        "name": "Dark Reading",
        "url": "https://www.darkreading.com/rss.xml",
        "category": "Cyber News"
    },
    {
        "name": "SecurityWeek",
        "url": "https://feeds.feedburner.com/securityweek",
        "category": "Security Research"
    },
    {
        "name": "Krebs on Security",
        "url": "https://krebsonsecurity.com/feed/",
        "category": "Security Research"
    },

    # ================= VULNERABILITIES / CVE =================
    {
        "name": "NVD Vulnerabilities",
        "url": "https://nvd.nist.gov/feeds/xml/cve/misc/nvd-rss.xml",
        "category": "Vulnerability"
    },
    {
        "name": "Exploit-DB",
        "url": "https://www.exploit-db.com/rss.xml",
        "category": "Exploit"
    },

    # ================= CLOUD / ENTERPRISE =================
    {
        "name": "Microsoft Security Blog",
        "url": "https://www.microsoft.com/security/blog/feed/",
        "category": "Cloud Security"
    },
    {
        "name": "Google Security Blog",
        "url": "https://security.googleblog.com/feeds/posts/default",
        "category": "Cloud Security"
    },

    # ================= OPEN SOURCE / DEV SECURITY =================
    {
        "name": "GitHub Security Advisories",
        "url": "https://github.blog/security/feed/",
        "category": "Supply Chain"
    },
    {
        "name": "Snyk Vulnerability Blog",
        "url": "https://snyk.io/blog/feed/",
        "category": "Supply Chain"
    },
]

# ---------------- HIGH-FREQUENCY FEEDS (polled more often) ----------------
HIGH_FREQUENCY_FEEDS = [
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.bleepingcomputer.com/feed/",
    "https://www.darkreading.com/rss.xml",
    "https://www.cisa.gov/news.xml",
    "https://www.exploit-db.com/rss.xml",
]
