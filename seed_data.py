"""
SkillMap Database Initialization & Domain Seed Data
---------------------------------------------------
Populates the SQLite catalog with six structured technology career paths,
tiered skills (Beginner, Intermediate, Advanced), recommended projects,
curated learning resources, skill assessment questions, and an optional
demo learner account with real relational records.

AI Assistance Note:
Curriculum descriptions and assessment question banks were structured with
AI assistance and verified for technical accuracy.
"""

from datetime import datetime, timedelta
from typing import Optional
from werkzeug.security import generate_password_hash

from database import get_db


CAREER_CATALOG = [
    {
        "slug": "cybersecurity",
        "title": "Cybersecurity",
        "tagline": "Defend infrastructure, audit vulnerabilities, and respond to security incidents.",
        "description": (
            "Cybersecurity engineers protect systems, networks, and applications from unauthorized "
            "access and data breaches. This track builds from Linux and networking fundamentals into "
            "threat modeling, web application security, SIEM monitoring, and incident response."
        ),
        "estimated_hours": 320,
        "estimated_months": 6,
        "difficulty_summary": "Beginner to Advanced",
        "icon_name": "shield",
        "accent_color": "#E11D48",
        "skills": [
            ("Linux & Shell Security", "Beginner", "User permissions, systemd hardening, SSH configuration, and bash auditing.", 35, 1),
            ("TCP/IP & Packet Analysis", "Beginner", "OSI layers, subnetting, DNS/TLS inspection, and Wireshark traffic analysis.", 40, 2),
            ("Web Application Security", "Intermediate", "OWASP Top 10 vulnerabilities, authentication flaws, SQLi, XSS, and CSRF defense.", 55, 3),
            ("Network Defense & Firewalls", "Intermediate", "Zero-trust segmentation, iptables/nftables, IDS/IPS rules, and VPN tunneling.", 50, 4),
            ("SIEM & Threat Hunting", "Advanced", "Log aggregation, correlation rules, MITRE ATT&CK mapping, and anomaly triage.", 70, 5),
            ("Incident Response & Forensics", "Advanced", "Containment playbooks, memory/disk artifact capture, and post-incident reporting.", 70, 6),
        ],
        "recommended_projects": [
            ("SSH & Firewall Hardening Baseline", "Beginner", "Write an automated Bash script that audits Linux permissions, configures UFW rules, and disables insecure SSH auth.", "Bash, UFW, Linux, OpenSSH", 14),
            ("OWASP Vulnerability Lab Analyzer", "Intermediate", "Build a Python scanner that detects insecure HTTP headers, cookie flags, and reflected input patterns on test apps.", "Python, Requests, OWASP ZAP", 24),
            ("Mini SIEM Log Correlation Engine", "Advanced", "Ingest auth.log and Nginx access logs into SQLite/Python to flag brute-force patterns and anomalous IP bursts.", "Python, SQLite, Regex, Syslog", 36),
        ],
        "resources": [
            ("OWASP Web Security Testing Guide", "Comprehensive methodology for testing web application security controls.", "https://owasp.org/www-project-web-security-testing-guide/", "Documentation", "Intermediate"),
            ("OverTheWire: Bandit Wargame", "Hands-on Linux command-line and privilege fundamentals through progressive challenges.", "https://overthewire.org/wargames/bandit/", "Practice Lab", "Beginner"),
            ("MITRE ATT&CK Framework", "Adversary tactics and techniques knowledge base for threat hunting and detection.", "https://attack.mitre.org/", "Documentation", "Advanced"),
            ("PortSwigger Web Security Academy", "Interactive labs covering SQL injection, CSRF, authentication bypass, and SSRF.", "https://portswigger.net/web-security", "Practice Lab", "Intermediate"),
        ],
        "questions": [
            ("TCP/IP & Packet Analysis", "Beginner", "Which protocol operates at the Transport layer and guarantees ordered, reliable byte-stream delivery?", "UDP", "TCP", "ICMP", "ARP", "B", "TCP provides connection-oriented, ordered, and reliable delivery using acknowledgments and sequence numbers."),
            ("Linux & Shell Security", "Beginner", "What octal permission grants the file owner read/write/execute, the group read/execute, and others no access?", "750", "644", "755", "700", "A", "7 (rwx) for owner, 5 (r-x) for group, and 0 (---) for others corresponds to 750."),
            ("Web Application Security", "Intermediate", "What is the primary defense against SQL Injection when querying a relational database?", "Escaping quotes manually in JavaScript", "Parameterized prepared statements", "Base64 encoding user inputs", "Hiding error stack traces only", "B", "Parameterized queries separate SQL structure from untrusted data so input cannot alter query syntax."),
            ("Web Application Security", "Intermediate", "Which cookie attribute prevents client-side JavaScript from reading a session identifier via document.cookie?", "SameSite=Strict", "Secure", "HttpOnly", "Max-Age", "C", "HttpOnly instructs the browser to exclude the cookie from the DOM document.cookie API, mitigating XSS session theft."),
            ("SIEM & Threat Hunting", "Advanced", "In the MITRE ATT&CK matrix, what does the 'Persistence' tactic describe?", "Techniques used to exfiltrate archived files", "Techniques adversaries use to maintain access across restarts", "Scanning open ports on an external perimeter", "Encrypting backups for ransomware leverage", "B", "Persistence consists of techniques like scheduled tasks or startup scripts used to keep access after reboots or credential changes."),
        ],
    },
    {
        "slug": "network-engineering",
        "title": "Network Engineering",
        "tagline": "Design resilient routing topologies, automate switches, and troubleshoot packet flows.",
        "description": (
            "Network engineers architect the physical and cloud connectivity powering modern applications. "
            "Master IPv4/IPv6 subnetting, VLAN switching, dynamic routing protocols like OSPF and BGP, "
            "cloud VPC design, and Python-based network automation."
        ),
        "estimated_hours": 290,
        "estimated_months": 5,
        "difficulty_summary": "Beginner to Advanced",
        "icon_name": "network",
        "accent_color": "#0891B2",
        "skills": [
            ("IPv4 & IPv6 Subnetting", "Beginner", "CIDR notation, VLSM allocation, address planning, and broadcast domain sizing.", 30, 1),
            ("Switching & VLAN Design", "Beginner", "802.1Q trunking, Spanning Tree Protocol (STP), and port security.", 40, 2),
            ("Dynamic Routing (OSPF)", "Intermediate", "Link-state advertisements, multi-area OSPF, route summarization, and failover.", 55, 3),
            ("DNS, DHCP & Load Balancing", "Intermediate", "Authoritative DNS records, DHCP relay, L4/L7 reverse proxies, and health checks.", 45, 4),
            ("BGP & Edge Peering", "Advanced", "Autonomous systems, path attributes, route filtering, and multi-homed redundancy.", 60, 5),
            ("Network Automation", "Advanced", "Paramiko/Netmiko scripting, telemetry polling, and declarative topology validation.", 60, 6),
        ],
        "recommended_projects": [
            ("CIDR Subnet Planner CLI", "Beginner", "Build a Python tool that computes network ranges, usable host counts, and non-overlapping VLSM allocations.", "Python, ipaddress, CLI", 12),
            ("Multi-VLAN & OSPF Topology Lab", "Intermediate", "Design a redundant 3-router, 2-switch topology with inter-VLAN routing and documented failover tests.", "GNS3 / Containerlab, OSPF, VLANs", 26),
            ("Automated Config Drift Auditor", "Advanced", "Create a Python utility that diffs router configurations against a YAML baseline and logs drift alerts.", "Python, YAML, SSH, SQLite", 34),
        ],
        "resources": [
            ("Cloudflare Learning Center: Networking", "Clear explanations of BGP, DNS, Anycast, and internet routing architecture.", "https://www.cloudflare.com/learning/network-layer/what-is-the-network-layer/", "Article", "Beginner"),
            ("Beej's Guide to Network Concepts", "Foundational guide to sockets, TCP/IP framing, and low-level network behavior.", "https://beej.us/guide/bgnet0/", "Book", "Beginner"),
            ("RFC 2328 — OSPF Version 2", "Primary protocol specification for Open Shortest Path First link-state routing.", "https://datatracker.ietf.org/doc/html/rfc2328", "Documentation", "Intermediate"),
            ("Nornir Network Automation Docs", "Pluggable Python automation framework for inventory and parallel device tasks.", "https://nornir.readthedocs.io/", "Tool", "Advanced"),
        ],
        "questions": [
            ("IPv4 & IPv6 Subnetting", "Beginner", "How many usable host IPv4 addresses are available in a /26 subnet?", "64", "62", "30", "126", "B", "A /26 leaves 6 host bits (2^6 = 64 total addresses), minus 2 for network and broadcast addresses = 62 usable hosts."),
            ("Switching & VLAN Design", "Beginner", "Which IEEE standard defines VLAN tagging on Ethernet trunk frames?", "802.11ax", "802.1Q", "802.3af", "802.1X", "B", "IEEE 802.1Q inserts a 4-byte VLAN tag into the Ethernet frame header to carry multiple VLANs over a trunk link."),
            ("Dynamic Routing (OSPF)", "Intermediate", "In a multi-area OSPF network, which area must all other areas connect to directly (or via virtual link)?", "Area 1", "Area 255", "Area 0 (Backbone)", "Area 10", "C", "Area 0 is the OSPF backbone area responsible for distributing routing information between non-backbone areas."),
            ("DNS, DHCP & Load Balancing", "Intermediate", "During the DORA DHCP lease sequence, which message does the client send first?", "DHCP Offer", "DHCP Request", "DHCP Discover", "DHCP Ack", "C", "A client broadcasts a DHCP Discover message to locate available DHCP servers on the local segment."),
            ("BGP & Edge Peering", "Advanced", "Which BGP path attribute is evaluated first (among standard attributes after Weight) to prefer an outbound route?", "AS_PATH length", "MED", "LOCAL_PREF", "Origin code", "C", "After Cisco-proprietary Weight, BGP compares LOCAL_PREF (higher is preferred) across an autonomous system."),
        ],
    },
    {
        "slug": "backend-development",
        "title": "Backend Development",
        "tagline": "Architect APIs, relational data models, authentication systems, and scalable services.",
        "description": (
            "Backend engineers build the server-side logic, databases, and APIs that power web and mobile "
            "applications. Learn Python/Flask or Node services, normalized SQL schema design, REST API design, "
            "caching, automated testing, and containerized deployment."
        ),
        "estimated_hours": 340,
        "estimated_months": 6,
        "difficulty_summary": "Beginner to Advanced",
        "icon_name": "server",
        "accent_color": "#6D28D9",
        "skills": [
            ("HTTP, REST & Routing", "Beginner", "Request/response lifecycle, status codes, content negotiation, and clean endpoint design.", 35, 1),
            ("Relational SQL & Modeling", "Beginner", "Normalization (1NF–3NF), foreign keys, joins, indexes, and transaction isolation.", 50, 2),
            ("Authentication & Security", "Intermediate", "Password hashing (PBKDF2/Argon2), session management, RBAC, and CSRF protection.", 55, 3),
            ("Automated Testing & CI", "Intermediate", "Unit/integration test suites, fixtures, mocking external APIs, and regression coverage.", 50, 4),
            ("Caching & Async Queues", "Advanced", "Redis caching strategies, background job workers, idempotency, and rate limiting.", 75, 5),
            ("Observability & Performance", "Advanced", "Query profiling, structured logging, N+1 elimination, and graceful error recovery.", 75, 6),
        ],
        "recommended_projects": [
            ("Bookmark & Tagging REST API", "Beginner", "Create a Flask + SQLite REST service with pagination, search filtering, and input validation.", "Python, Flask, SQLite", 16),
            ("Role-Based Issue Tracker Backend", "Intermediate", "Implement multi-user auth, project permissions, audit logs, and full integration tests.", "Flask, SQLite, Werkzeug, Unittest", 28),
            ("Rate-Limited Webhook Processor", "Advanced", "Build an idempotent event ingestion API with retry queues, signature verification, and metrics.", "Python, SQL, HMAC, Workers", 40),
        ],
        "resources": [
            ("Flask Official Documentation", "Authoritative guide to blueprints, application factories, testing, and sessions.", "https://flask.palletsprojects.com/", "Documentation", "Beginner"),
            ("SQLite Query Language & Indexing", "Deep dive into SQLite B-tree indexes, EXPLAIN QUERY PLAN, and constraints.", "https://www.sqlite.org/queryplanner.html", "Documentation", "Intermediate"),
            ("OWASP API Security Top 10", "Essential security checklist for authentication, authorization, and rate limiting in APIs.", "https://owasp.org/API-Security/", "Documentation", "Intermediate"),
            ("Designing Data-Intensive Applications", "Foundational architecture patterns for consistency, replication, and batch/stream processing.", "https://dataintensive.net/", "Book", "Advanced"),
        ],
        "questions": [
            ("HTTP, REST & Routing", "Beginner", "Which HTTP status code indicates a resource was successfully created following a POST request?", "200 OK", "201 Created", "204 No Content", "302 Found", "B", "201 Created explicitly signals that the request succeeded and led to the creation of a new resource."),
            ("Relational SQL & Modeling", "Beginner", "What is the primary purpose of an ON DELETE CASCADE foreign key constraint?", "Encrypt child records automatically", "Automatically delete dependent child rows when the parent row is deleted", "Prevent any reads on the child table", "Convert NULL values to empty strings", "B", "ON DELETE CASCADE maintains referential integrity by deleting child rows referencing a deleted parent row."),
            ("Authentication & Security", "Intermediate", "Why should user passwords be stored using salted slow hashes (e.g., scrypt, Argon2, PBKDF2) rather than SHA-256?", "SHA-256 cannot hash strings longer than 16 characters", "Slow salted hashes resist rainbow tables and brute-force GPU cracking", "Salted hashes allow admins to decrypt passwords", "SHA-256 is only supported in browsers", "B", "Fast hashes like raw SHA-256 can be brute-forced at billions of guesses per second; unique salts and work factors slow attackers."),
            ("Observability & Performance", "Advanced", "What characterizes the 'N+1 query problem' in backend applications?", "Executing 1 query for N items followed by N separate queries for related records", "Returning N+1 HTTP headers on every response", "Running out of database connections at midnight", "Storing JSON inside more than N columns", "A", "Fetching a list of N rows and querying child data inside a loop causes N+1 round-trips instead of a single JOIN."),
            ("Caching & Async Queues", "Advanced", "What makes an API endpoint idempotent?", "It responds in under 10 milliseconds", "Repeating the identical request produces the same server state as calling it once", "It only accepts GET parameters", "It caches every response forever", "B", "Idempotency guarantees that duplicate retries (e.g., due to network timeouts) do not create duplicate side effects."),
        ],
    },
    {
        "slug": "frontend-development",
        "title": "Frontend Development",
        "tagline": "Craft accessible, responsive, high-performance user interfaces with modern web standards.",
        "description": (
            "Frontend engineers translate product requirements into fast, accessible, and responsive browser "
            "experiences. Build mastery in semantic HTML5, modern CSS layout systems, modular JavaScript/TypeScript, "
            "accessibility (WCAG), state architecture, and browser performance."
        ),
        "estimated_hours": 300,
        "estimated_months": 5,
        "difficulty_summary": "Beginner to Advanced",
        "icon_name": "layout",
        "accent_color": "#DB2777",
        "skills": [
            ("Semantic HTML5 & Accessibility", "Beginner", "Landmark elements, ARIA roles, keyboard focus management, and screen-reader semantics.", 35, 1),
            ("Modern CSS Grid & Flexbox", "Beginner", "Responsive fluid grids, custom properties, container queries, and design systems.", 45, 2),
            ("DOM & Async JavaScript", "Intermediate", "Event delegation, Fetch API, Promises/async-await, and clean client state updates.", 55, 3),
            ("Data Visualization & Canvas", "Intermediate", "Interactive Chart.js / SVG visualizations, responsive legends, and clean data formatting.", 45, 4),
            ("Component Architecture & TypeScript", "Advanced", "Predictable unidirectional state, strict typing, reusable primitives, and error boundaries.", 60, 5),
            ("Core Web Vitals & Performance", "Advanced", "Bundle splitting, layout shift (CLS) elimination, caching headers, and lighthouse auditing.", 60, 6),
        ],
        "recommended_projects": [
            ("Accessible Editorial Landing Page", "Beginner", "Build a keyboard-navigable responsive site with semantic landmarks and zero layout overflow.", "HTML5, CSS Grid, Flexbox", 14),
            ("Interactive Expense & Budget Dashboard", "Intermediate", "Create a client-side dashboard with Chart.js visualizations, live filtering, and accessible tables.", "JavaScript, Chart.js, CSS Variables", 26),
            ("Collaborative Kanban State Engine", "Advanced", "Implement drag-free accessible card reordering, optimistic API sync, and offline state recovery.", "TypeScript, Fetch API, LocalStorage", 36),
        ],
        "resources": [
            ("MDN Web Docs: Learn Web Development", "Canonical reference for HTML5, CSS Grid, Flexbox, and Web APIs.", "https://developer.mozilla.org/en-US/docs/Learn", "Documentation", "Beginner"),
            ("web.dev: Learn Accessibility", "Practical engineering patterns for WCAG contrast, keyboard navigation, and ARIA.", "https://web.dev/learn/accessibility", "Course", "Intermediate"),
            ("Chart.js Official Documentation", "Complete reference for responsive charts, datasets, scales, and interactive tooltips.", "https://www.chartjs.org/docs/latest/", "Documentation", "Intermediate"),
            ("Patterns.dev — Rendering & Performance", "Modern web architecture patterns for hydration, prefetching, and performance budgets.", "https://www.patterns.dev/", "Book", "Advanced"),
        ],
        "questions": [
            ("Semantic HTML5 & Accessibility", "Beginner", "Which HTML element is semantically appropriate for the primary navigation block of a page?", "<div class='nav'>", "<nav>", "<section>", "<aside>", "B", "The <nav> landmark element communicates major navigation links directly to assistive technologies."),
            ("Modern CSS Grid & Flexbox", "Beginner", "In CSS Grid, what does `grid-template-columns: repeat(auto-fit, minmax(260px, 1fr))` accomplish?", "Fixes every column to exactly 260px regardless of viewport width", "Creates responsive columns that wrap automatically and share remaining space", "Stacks all items vertically on desktop", "Centers a single item horizontally", "B", "auto-fit combined with minmax(260px, 1fr) dynamically fits as many >=260px columns as space permits."),
            ("DOM & Async JavaScript", "Intermediate", "Why is event delegation on a parent container useful for dynamic lists?", "It disables browser bubbling", "One listener handles events on dynamically added child items without re-binding", "It converts synchronous code into WebAssembly", "It bypasses CORS restrictions", "B", "Because events bubble up the DOM tree, a single listener on a stable parent handles clicks from future child elements."),
            ("Core Web Vitals & Performance", "Advanced", "Which Core Web Vital measures unexpected visual movement of page elements during loading?", "LCP (Largest Contentful Paint)", "INP (Interaction to Next Paint)", "CLS (Cumulative Layout Shift)", "TTFB (Time to First Byte)", "C", "Cumulative Layout Shift (CLS) quantifies how much visible content shifts unexpectedly during page rendering."),
            ("Semantic HTML5 & Accessibility", "Intermediate", "According to WCAG AA guidelines, what is the minimum contrast ratio for normal-sized body text?", "2.0:1", "3.0:1", "4.5:1", "7.0:1", "C", "WCAG 2.1 Level AA requires at least 4.5:1 contrast for normal text and 3:1 for large text."),
        ],
    },
    {
        "slug": "android-development",
        "title": "Android Development",
        "tagline": "Build responsive native Android apps using Kotlin, Jetpack Compose, and offline-first storage.",
        "description": (
            "Android engineers create reliable mobile applications for billions of devices. Learn modern Kotlin, "
            "declarative UI with Jetpack Compose, MVVM architecture, Room SQLite persistence, background work with "
            "Coroutines, and Play Store release engineering."
        ),
        "estimated_hours": 330,
        "estimated_months": 6,
        "difficulty_summary": "Beginner to Advanced",
        "icon_name": "smartphone",
        "accent_color": "#2563EB",
        "skills": [
            ("Kotlin Language Fundamentals", "Beginner", "Null safety, data classes, sealed interfaces, extension functions, and collections.", 40, 1),
            ("Jetpack Compose UI", "Beginner", "Declarative composables, state hoisting, Material 3 theming, and adaptive layouts.", 50, 2),
            ("Lifecycle & MVVM Architecture", "Intermediate", "ViewModel, StateFlow, unidirectional data flow, and configuration survival.", 55, 3),
            ("Room SQLite & Networking", "Intermediate", "Local relational caching with Room DAOs, Retrofit/Ktor clients, and DTO mapping.", 55, 4),
            ("Coroutines & WorkManager", "Advanced", "Structured concurrency, Flow operators, dispatchers, and reliable background sync.", 65, 5),
            ("Testing & Performance Profiling", "Advanced", "Compose UI tests, Macrobenchmark, memory leak detection, and APK optimization.", 65, 6),
        ],
        "recommended_projects": [
            ("Habit Streak Tracker in Compose", "Beginner", "Build a clean Material 3 habit list with state hoisting and custom dark/light tokens.", "Kotlin, Jetpack Compose, Material 3", 16),
            ("Offline-First Study Flashcards", "Intermediate", "Persist decks in Room SQLite with spaced-repetition scheduling and ViewModel StateFlow.", "Kotlin, Room, ViewModel, Flow", 30),
            ("Real-Time Transit Companion", "Advanced", "Combine remote REST polling, local caching, and WorkManager alerts with unit-tested repositories.", "Kotlin, Coroutines, Ktor, WorkManager", 42),
        ],
        "resources": [
            ("Android Basics with Compose", "Official Google curriculum covering Kotlin, Compose layouts, and app architecture.", "https://developer.android.com/courses/android-basics-compose/course", "Course", "Beginner"),
            ("Kotlin Language Documentation", "Official guide to Kotlin coroutines, null safety, and idiomatic standard library APIs.", "https://kotlinlang.org/docs/home.html", "Documentation", "Beginner"),
            ("Guide to App Architecture", "Official Jetpack guidance on UI layer, domain layer, and single-source-of-truth data.", "https://developer.android.com/topic/architecture", "Documentation", "Intermediate"),
            ("Testing on Android Developers", "Unit, integration, and Compose UI testing strategies for production reliability.", "https://developer.android.com/training/testing", "Documentation", "Advanced"),
        ],
        "questions": [
            ("Kotlin Language Fundamentals", "Beginner", "Which Kotlin operator safely accesses a property only if the receiver is non-null?", "!!", "?.", "::", "->", "B", "The safe call operator (?.) evaluates the property or method if non-null and returns null otherwise."),
            ("Jetpack Compose UI", "Beginner", "What is 'state hoisting' in Jetpack Compose?", "Storing all UI state in global static variables", "Moving state to a composable's caller to make the child stateless and reusable", "Encrypting state inside SharedPreferences", "Running UI rendering on Dispatchers.IO", "B", "State hoisting passes state down and events up, creating single-source-of-truth, testable composables."),
            ("Lifecycle & MVVM Architecture", "Intermediate", "Why is ViewModel preferred over holding state directly inside an Activity?", "ViewModel survives configuration changes like screen rotation automatically", "ViewModel can bypass AndroidManifest permissions", "ViewModel renders OpenGL frames faster", "ViewModel replaces SQLite databases", "A", "A ViewModel is scoped to a LifecycleOwner's store and persists across configuration recreations such as rotations."),
            ("Coroutines & WorkManager", "Advanced", "Which Kotlin Coroutines dispatcher is designed specifically for disk and network I/O operations?", "Dispatchers.Main", "Dispatchers.IO", "Dispatchers.Unconfined", "Dispatchers.UI", "B", "Dispatchers.IO uses a shared pool of threads tuned for blocking I/O tasks like database and network calls."),
            ("Room SQLite & Networking", "Intermediate", "In Room, what annotation marks an interface containing SQL query methods?", "@Entity", "@Database", "@Dao", "@Repository", "C", "@Dao (Data Access Object) defines methods annotated with @Query, @Insert, @Update, and @Delete."),
        ],
    },
    {
        "slug": "data-analysis",
        "title": "Data Analysis",
        "tagline": "Transform raw datasets into statistical insights, executive dashboards, and clear decisions.",
        "description": (
            "Data analysts turn messy operational data into trustworthy metrics and actionable narratives. "
            "Master SQL analytics, Python with pandas, exploratory data analysis, hypothesis testing, "
            "dimensional modeling, and clear visual storytelling."
        ),
        "estimated_hours": 280,
        "estimated_months": 5,
        "difficulty_summary": "Beginner to Advanced",
        "icon_name": "bar-chart",
        "accent_color": "#0D9488",
        "skills": [
            ("SQL Analytics & Window Functions", "Beginner", "CTEs, aggregations, CASE expressions, RANK/ROW_NUMBER, and cohort queries.", 45, 1),
            ("Spreadsheet & KPI Modeling", "Beginner", "Pivot tables, lookup logic, data validation, and metric definitions.", 30, 2),
            ("Python & Pandas Data Cleaning", "Intermediate", "Missing value handling, tidy reshaping, merges, datetime indexing, and pipelines.", 55, 3),
            ("Exploratory Visualization", "Intermediate", "Choosing the right chart encoding, outlier inspection, and honest axis scaling.", 45, 4),
            ("Statistical Inference & A/B Testing", "Advanced", "Confidence intervals, p-values, sample sizing, and regression diagnostics.", 55, 5),
            ("BI Dashboards & Data Storytelling", "Advanced", "Star schema metrics layers, executive reporting, and narrative synthesis.", 50, 6),
        ],
        "recommended_projects": [
            ("E-Commerce Cohort Retention SQL Study", "Beginner", "Write analytical SQL queries using CTEs and window functions to compute monthly customer retention.", "SQL, SQLite, Window Functions", 15),
            ("Transit Delay Exploratory Notebook", "Intermediate", "Clean 100k rows of public transit schedules in pandas and visualize peak bottleneck corridors.", "Python, Pandas, Matplotlib", 24),
            ("A/B Experiment Evaluation Report", "Advanced", "Analyze conversion lift, statistical significance, and segment effects with a reproducible report.", "Python, SciPy, SQL, Statistics", 32),
        ],
        "resources": [
            ("Mode SQL Tutorial", "Practical, business-focused SQL lessons covering joins, aggregations, and window functions.", "https://mode.com/sql-tutorial/", "Course", "Beginner"),
            ("Pandas Official User Guide", "Authoritative reference on indexing, grouping, merging, and time-series manipulation.", "https://pandas.pydata.org/docs/user_guide/index.html", "Documentation", "Intermediate"),
            ("Storytelling with Data", "Principles for uncluttered, accurate analytical charts and executive communication.", "https://www.storytellingwithdata.com/", "Book", "Intermediate"),
            ("Evan Miller's A/B Testing Guide", "Rigorous statistical foundations for sample size calculation and avoiding peeking errors.", "https://www.evanmiller.org/how-not-to-run-an-ab-test.html", "Article", "Advanced"),
        ],
        "questions": [
            ("SQL Analytics & Window Functions", "Beginner", "Which SQL clause filters groups AFTER aggregation (such as COUNT or SUM) has been computed?", "WHERE", "HAVING", "ORDER BY", "GROUP BY", "B", "WHERE filters individual rows before grouping, whereas HAVING filters aggregated groups."),
            ("SQL Analytics & Window Functions", "Intermediate", "What does a SQL window function (`OVER (PARTITION BY ...)` ) do compared to `GROUP BY`?", "It deletes duplicate rows permanently", "It computes an aggregate or rank while preserving every individual row", "It only works on string columns", "It converts tables into CSV files", "B", "Window functions compute metrics across a window of rows without collapsing the result set into one row per group."),
            ("Python & Pandas Data Cleaning", "Intermediate", "In pandas, which method fills missing (NaN) values with a specified replacement?", "dropna()", "fillna()", "isna()", "astype()", "B", "fillna() substitutes NaN entries with a constant, dictionary mapping, or forward/backward fill strategy."),
            ("Statistical Inference & A/B Testing", "Advanced", "What error occurs when an analyst repeatedly checks an A/B test and stops as soon as p < 0.05?", "Type I error inflation (false positive)", "Division by zero", "Data normalization bias", "Survivorship truncation", "A", "Peeking at sequential test results without correction inflates the false-positive (Type I) rate well above 5%."),
            ("Exploratory Visualization", "Beginner", "Why should bar charts comparing absolute magnitudes generally start their numeric axis at zero?", "To make CSS rendering faster", "To ensure bar lengths remain proportional to the underlying values", "Because SQL requires zero values", "To hide outliers automatically", "B", "Truncating a bar chart axis exaggerates minor differences because readers judge bar area and length proportionally."),
        ],
    },
]


def seed_catalog() -> None:
    """Idempotently seed career paths, skills, recommended projects, resources, and questions."""
    db = get_db()

    for career in CAREER_CATALOG:
        existing = db.execute(
            "SELECT id FROM career_paths WHERE slug = ?", (career["slug"],)
        ).fetchone()
        if existing:
            career_id = existing["id"]
            db.execute(
                "UPDATE career_paths SET icon_name = ?, accent_color = ? WHERE id = ?",
                (career["icon_name"], career["accent_color"], career_id),
            )
        else:
            cursor = db.execute(
                """
                INSERT INTO career_paths
                (slug, title, tagline, description, estimated_hours, estimated_months, difficulty_summary, icon_name, accent_color)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    career["slug"],
                    career["title"],
                    career["tagline"],
                    career["description"],
                    career["estimated_hours"],
                    career["estimated_months"],
                    career["difficulty_summary"],
                    career["icon_name"],
                    career["accent_color"],
                ),
            )
            career_id = cursor.lastrowid

        # Seed skills
        skill_id_by_name = {}
        for name, level, desc, hours, sort_order in career["skills"]:
            skill_row = db.execute(
                "SELECT id FROM skills WHERE career_path_id = ? AND name = ?",
                (career_id, name),
            ).fetchone()
            if skill_row:
                skill_id_by_name[name] = skill_row["id"]
            else:
                cur = db.execute(
                    """
                    INSERT INTO skills (career_path_id, name, level, description, estimated_hours, sort_order)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (career_id, name, level, desc, hours, sort_order),
                )
                skill_id_by_name[name] = cur.lastrowid

        # Seed recommended projects (if none exist for this career)
        rec_count = db.execute(
            "SELECT COUNT(*) FROM career_recommended_projects WHERE career_path_id = ?",
            (career_id,),
        ).fetchone()[0]
        if rec_count == 0:
            for title, level, desc, stack, hours in career["recommended_projects"]:
                db.execute(
                    """
                    INSERT INTO career_recommended_projects
                    (career_path_id, title, level, description, tech_stack, estimated_hours)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (career_id, title, level, desc, stack, hours),
                )

        # Seed curated system resources (user_id IS NULL)
        res_count = db.execute(
            "SELECT COUNT(*) FROM resources WHERE user_id IS NULL AND career_path_id = ?",
            (career_id,),
        ).fetchone()[0]
        if res_count == 0:
            for title, desc, url, category, difficulty in career["resources"]:
                db.execute(
                    """
                    INSERT INTO resources
                    (user_id, career_path_id, title, description, url, category, difficulty, is_completed)
                    VALUES (NULL, ?, ?, ?, ?, ?, ?, 0)
                    """,
                    (career_id, title, desc, url, category, difficulty),
                )

        # Seed assessment questions
        q_count = db.execute(
            "SELECT COUNT(*) FROM assessment_questions WHERE career_path_id = ?",
            (career_id,),
        ).fetchone()[0]
        if q_count == 0:
            for skill_name, difficulty, q_text, a, b, c, d, correct, explanation in career["questions"]:
                skill_id = skill_id_by_name.get(skill_name)
                db.execute(
                    """
                    INSERT INTO assessment_questions
                    (career_path_id, skill_id, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, difficulty)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (career_id, skill_id, q_text, a, b, c, d, correct, explanation, difficulty),
                )

    db.commit()


def enroll_user_in_career(
    user_id: int,
    career_path_id: int,
    personal_goal: Optional[str] = None,
    target_date: Optional[str] = None,
) -> bool:
    """
    Enroll a user in a career path, create per-skill progress rows, and generate
    initial roadmap tasks from the career's structured skills if none exist yet.
    Returns True if newly enrolled, False if already enrolled.
    """
    db = get_db()
    career = db.execute(
        "SELECT id, title FROM career_paths WHERE id = ?", (career_path_id,)
    ).fetchone()
    if not career:
        return False

    existing_goal = db.execute(
        "SELECT id FROM user_progress WHERE user_id = ? AND career_path_id = ? AND skill_id IS NULL",
        (user_id, career_path_id),
    ).fetchone()

    default_goal = personal_goal or f"Complete core {career['title']} milestones and portfolio projects"
    default_target = target_date or (datetime.utcnow() + timedelta(days=90)).strftime("%Y-%m-%d")

    if not existing_goal:
        db.execute(
            """
            INSERT INTO user_progress
            (user_id, career_path_id, skill_id, mastery_percent, hours_logged, personal_goal, target_date, is_active_path)
            VALUES (?, ?, NULL, 0, 0.0, ?, ?, 1)
            """,
            (user_id, career_path_id, default_goal, default_target),
        )
    else:
        db.execute(
            "UPDATE user_progress SET is_active_path = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (existing_goal["id"],),
        )

    skills = db.execute(
        "SELECT id, name, level, description, estimated_hours FROM skills WHERE career_path_id = ? ORDER BY sort_order ASC",
        (career_path_id,),
    ).fetchall()

    for skill in skills:
        prog = db.execute(
            "SELECT id FROM user_progress WHERE user_id = ? AND career_path_id = ? AND skill_id = ?",
            (user_id, career_path_id, skill["id"]),
        ).fetchone()
        if not prog:
            db.execute(
                """
                INSERT INTO user_progress (user_id, career_path_id, skill_id, mastery_percent, hours_logged, is_active_path)
                VALUES (?, ?, ?, 0, 0.0, 1)
                """,
                (user_id, career_path_id, skill["id"]),
            )

    existing_tasks = db.execute(
        "SELECT COUNT(*) FROM roadmap_tasks WHERE user_id = ? AND career_path_id = ?",
        (user_id, career_path_id),
    ).fetchone()[0]

    if existing_tasks == 0:
        for idx, skill in enumerate(skills):
            due_offset = 10 + (idx * 12)
            due_str = (datetime.utcnow() + timedelta(days=due_offset)).strftime("%Y-%m-%d")
            db.execute(
                """
                INSERT INTO roadmap_tasks
                (user_id, career_path_id, skill_id, title, description, level, estimated_hours, is_completed, due_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
                """,
                (
                    user_id,
                    career_path_id,
                    skill["id"],
                    f"Master {skill['name']}",
                    skill["description"],
                    skill["level"],
                    min(12.0, round(skill["estimated_hours"] * 0.25, 1)),
                    due_str,
                ),
            )
            db.execute(
                """
                INSERT INTO roadmap_tasks
                (user_id, career_path_id, skill_id, title, description, level, estimated_hours, is_completed, due_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
                """,
                (
                    user_id,
                    career_path_id,
                    skill["id"],
                    f"Apply {skill['name']} in a hands-on exercise",
                    f"Build or document a practical lab demonstrating {skill['name'].lower()}.",
                    skill["level"],
                    min(8.0, round(skill["estimated_hours"] * 0.15, 1)),
                    (datetime.utcnow() + timedelta(days=due_offset + 5)).strftime("%Y-%m-%d"),
                ),
            )

    # Set user's target_career_id if unset
    user_row = db.execute("SELECT target_career_id FROM users WHERE id = ?", (user_id,)).fetchone()
    if user_row and user_row["target_career_id"] is None:
        db.execute("UPDATE users SET target_career_id = ? WHERE id = ?", (career_path_id, user_id))

    db.execute(
        """
        INSERT INTO activity_logs (user_id, career_path_id, action_type, description, hours_spent)
        VALUES (?, ?, 'roadmap_enrolled', ?, 0.5)
        """,
        (user_id, career_path_id, f"Enrolled in {career['title']} learning roadmap"),
    )
    db.commit()
    return not bool(existing_goal)


def seed_demo_user() -> None:
    """
    Create a showcase learner account (alex.chen@skillmap.dev / SkillMap2026!)
    only if no users exist yet, populated with realistic database records.
    """
    db = get_db()
    user_count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if user_count > 0:
        return

    backend_row = db.execute("SELECT id FROM career_paths WHERE slug = 'backend-development'").fetchone()
    cyber_row = db.execute("SELECT id FROM career_paths WHERE slug = 'cybersecurity'").fetchone()
    if not backend_row or not cyber_row:
        return

    backend_id = backend_row["id"]
    cyber_id = cyber_row["id"]

    cursor = db.execute(
        """
        INSERT INTO users (full_name, email, password_hash, bio, target_career_id, weekly_goal_hours)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            "Alex Chen",
            "alex.chen@skillmap.dev",
            generate_password_hash("SkillMap2026!"),
            "Aspiring Backend & Security Engineer building production APIs in Python and SQL.",
            backend_id,
            12.0,
        ),
    )
    user_id = cursor.lastrowid

    enroll_user_in_career(
        user_id,
        backend_id,
        personal_goal="Ship 2 tested Flask REST APIs and master relational SQL indexing.",
        target_date=(datetime.utcnow() + timedelta(days=60)).strftime("%Y-%m-%d"),
    )
    enroll_user_in_career(
        user_id,
        cyber_id,
        personal_goal="Complete OWASP Top 10 labs and Linux hardening checklist.",
        target_date=(datetime.utcnow() + timedelta(days=110)).strftime("%Y-%m-%d"),
    )

    # Mark initial beginner & early intermediate tasks completed for realistic progress
    backend_tasks = db.execute(
        "SELECT id, skill_id FROM roadmap_tasks WHERE user_id = ? AND career_path_id = ? ORDER BY id ASC",
        (user_id, backend_id),
    ).fetchall()
    for idx, task in enumerate(backend_tasks[:5]):
        completed_time = (datetime.utcnow() - timedelta(days=6 - idx)).strftime("%Y-%m-%d %H:%M:%S")
        db.execute(
            "UPDATE roadmap_tasks SET is_completed = 1, completed_at = ? WHERE id = ?",
            (completed_time, task["id"]),
        )

    cyber_tasks = db.execute(
        "SELECT id FROM roadmap_tasks WHERE user_id = ? AND career_path_id = ? ORDER BY id ASC",
        (user_id, cyber_id),
    ).fetchall()
    for idx, task in enumerate(cyber_tasks[:2]):
        completed_time = (datetime.utcnow() - timedelta(days=3 - idx)).strftime("%Y-%m-%d %H:%M:%S")
        db.execute(
            "UPDATE roadmap_tasks SET is_completed = 1, completed_at = ? WHERE id = ?",
            (completed_time, task["id"]),
        )

    # Update skill mastery rows based on completed tasks & practice
    backend_skills = db.execute(
        "SELECT id, name FROM skills WHERE career_path_id = ? ORDER BY sort_order ASC",
        (backend_id,),
    ).fetchall()
    mastery_levels = [88, 76, 62, 44, 20, 10]
    for skill, pct in zip(backend_skills, mastery_levels):
        db.execute(
            """
            UPDATE user_progress
            SET mastery_percent = ?, hours_logged = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND career_path_id = ? AND skill_id = ?
            """,
            (pct, round(pct * 0.2, 1), user_id, backend_id, skill["id"]),
        )

    cyber_skills = db.execute(
        "SELECT id FROM skills WHERE career_path_id = ? ORDER BY sort_order ASC",
        (cyber_id,),
    ).fetchall()
    for skill, pct in zip(cyber_skills, [72, 55, 35, 15, 0, 0]):
        db.execute(
            """
            UPDATE user_progress
            SET mastery_percent = ?, hours_logged = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND career_path_id = ? AND skill_id = ?
            """,
            (pct, round(pct * 0.15, 1), user_id, cyber_id, skill["id"]),
        )

    # Personal resources
    demo_resources = [
        (backend_id, "SQLite Foreign Keys & WAL Mode Guide", "Notes on enabling PRAGMA foreign_keys and concurrent reads in SQLite.", "https://www.sqlite.org/foreignkeys.html", "Documentation", "Beginner", 1),
        (backend_id, "Flask Application Factory Pattern", "Official walkthrough for modular blueprints and test configs.", "https://flask.palletsprojects.com/en/latest/patterns/appfactories/", "Documentation", "Intermediate", 1),
        (backend_id, "Test-Driven Development with Python", "Full workflow for integration testing web routes and database layers.", "https://www.obeythetestinggoat.com/", "Book", "Intermediate", 0),
        (cyber_id, "PortSwigger SQL Injection Labs", "Hands-on union-based and blind SQLi practice exercises.", "https://portswigger.net/web-security/sql-injection", "Practice Lab", "Intermediate", 0),
    ]
    for cid, title, desc, url, cat, diff, done in demo_resources:
        db.execute(
            """
            INSERT INTO resources (user_id, career_path_id, title, description, url, category, difficulty, is_completed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, cid, title, desc, url, cat, diff, done),
        )

    # Personal projects
    demo_projects = [
        (backend_id, "LedgerFlow API", "Double-entry expense tracking REST service with idempotent transfers and SQLite audit logs.", "Python, Flask, SQLite, Pytest", "In Progress", "https://github.com/alexchen-dev/ledgerflow-api", 72),
        (backend_id, "AuthVault Session Service", "Reusable PBKDF2 authentication microservice with CSRF middleware and role guards.", "Python, Werkzeug, Flask", "Completed", "https://github.com/alexchen-dev/authvault", 100),
        (cyber_id, "LogSentinel Analyzer", "CLI parser that inspects SSH and Nginx logs to surface brute-force bursts.", "Python, Regex, SQLite", "Planned", "https://github.com/alexchen-dev/logsentinel", 15),
    ]
    for cid, name, desc, stack, status, url, pct in demo_projects:
        db.execute(
            """
            INSERT INTO projects (user_id, career_path_id, name, description, tech_stack, status, github_url, completion_percent)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, cid, name, desc, stack, status, url, pct),
        )

    # Notes
    if backend_skills:
        db.execute(
            """
            INSERT INTO notes (user_id, career_path_id, skill_id, title, content)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                backend_id,
                backend_skills[1]["id"],
                "SQLite Indexing Rules of Thumb",
                "1. Always index foreign key columns used in JOINs and WHERE user_id = ? filters.\n"
                "2. Use composite indexes (user_id, created_at) for dashboard activity feeds.\n"
                "3. Verify query plans with EXPLAIN QUERY PLAN before shipping new filters.",
            ),
        )
        db.execute(
            """
            INSERT INTO notes (user_id, career_path_id, skill_id, title, content)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                backend_id,
                backend_skills[2]["id"],
                "Session Cookie Hardening Checklist",
                "- Set HttpOnly to block document.cookie access.\n"
                "- Pair SameSite=Lax/None appropriately with HTTPS Secure flag.\n"
                "- Validate CSRF tokens on every state-changing POST/PATCH/DELETE endpoint.",
            ),
        )

    # Assessments (including one below 70% to demonstrate weak-skill surfacing)
    if len(backend_skills) >= 4:
        db.execute(
            """
            INSERT INTO assessments (user_id, career_path_id, skill_id, title, assessment_type, score, total_questions, correct_answers, needs_practice, feedback)
            VALUES (?, ?, ?, ?, 'Quiz', 80, 5, 4, 0, ?)
            """,
            (
                user_id,
                backend_id,
                backend_skills[0]["id"],
                "Backend Core Fundamentals Check",
                "Strong grasp of HTTP status codes and relational constraints.",
            ),
        )
        db.execute(
            """
            INSERT INTO assessments (user_id, career_path_id, skill_id, title, assessment_type, score, total_questions, correct_answers, needs_practice, feedback)
            VALUES (?, ?, ?, ?, 'Practical', 58, 5, 3, 1, ?)
            """,
            (
                user_id,
                backend_id,
                backend_skills[3]["id"],
                "Automated Testing & Fixtures Drill",
                "Review isolated test fixtures and edge-case assertion patterns.",
            ),
        )

    # Activity logs spanning the past 7 days for real weekly chart rendering
    activity_entries = [
        (6, backend_id, "task_completed", "Completed task: Master HTTP, REST & Routing", 2.0),
        (5, backend_id, "resource_completed", "Finished reading SQLite Foreign Keys Guide", 1.5),
        (4, backend_id, "task_completed", "Completed task: Master Relational SQL & Modeling", 2.5),
        (3, cyber_id, "task_completed", "Completed task: Master Linux & Shell Security", 1.8),
        (2, backend_id, "project_updated", "Updated LedgerFlow API progress to 72%", 3.0),
        (1, backend_id, "assessment_taken", "Completed Backend Core Fundamentals Check (80%)", 1.0),
        (0, backend_id, "note_created", "Added study note: Session Cookie Hardening Checklist", 1.2),
    ]
    for days_ago, cid, action_type, desc, hours in activity_entries:
        ts = (datetime.utcnow() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
        db.execute(
            """
            INSERT INTO activity_logs (user_id, career_path_id, action_type, description, hours_spent, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, cid, action_type, desc, hours, ts),
        )

    db.commit()
