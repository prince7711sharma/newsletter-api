"""
dashboard_template.py - Premium Claymorphism UI for Newsletter Service
"""

def get_dashboard_html(admin_key: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard — R.S Education Solution</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-beige: #f5f3ef;
            --clay-bg: #fdfcfb;
            --clay-shadow-out: 8px 8px 16px #d1cfcb, -8px -8px 16px #ffffff;
            --clay-shadow-in: inset 4px 4px 8px #d1cfcb, inset -4px -4px 8px #ffffff;
            --clay-shadow-btn: 6px 6px 12px #d1cfcb, -6px -6px 12px #ffffff;
            --accent-blue: #4a90e2;
            --accent-green: #50c878;
            --accent-red: #ff6b6b;
            --text-main: #4a4a4a;
            --text-muted: #8e8e8e;
        }}

        * {{ box-sizing: border-box; transition: all 0.3s ease; }}

        body {{
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg-beige);
            color: var(--text-main);
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1000px;
            width: 100%;
            display: grid;
            grid-template-columns: 1fr 1.5fr;
            gap: 30px;
        }}

        @media (max-width: 850px) {{
            .container {{ grid-template-columns: 1fr; }}
        }}

        /* --- Components --- */

        .clay-card {{
            background: var(--clay-bg);
            border-radius: 30px;
            padding: 30px;
            box-shadow: var(--clay-shadow-out);
            border: 1px solid rgba(255,255,255,0.4);
            margin-bottom: 30px;
        }}

        .clay-title {{
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 25px;
            color: var(--accent-blue);
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .clay-input {{
            width: 100%;
            border: none;
            background: var(--bg-beige);
            box-shadow: var(--clay-shadow-in);
            padding: 15px 20px;
            border-radius: 20px;
            font-family: inherit;
            font-size: 15px;
            margin-bottom: 20px;
            outline: none;
        }}

        .clay-btn {{
            width: 100%;
            border: none;
            background: var(--clay-bg);
            box-shadow: var(--clay-shadow-btn);
            padding: 15px;
            border-radius: 20px;
            font-weight: 600;
            cursor: pointer;
            color: var(--accent-blue);
            font-size: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }}

        .clay-btn:active {{
            box-shadow: var(--clay-shadow-in);
            transform: scale(0.98);
        }}

        .clay-btn.primary {{
            background: var(--accent-blue);
            color: white;
            box-shadow: 6px 6px 12px rgba(74, 144, 226, 0.3), -6px -6px 12px #ffffff;
        }}

        .clay-btn.danger {{
            color: var(--accent-red);
        }}

        .badge {{
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            box-shadow: var(--clay-shadow-in);
        }}

        .badge.success {{ color: var(--accent-green); }}
        .badge.error {{ color: var(--accent-red); }}
        .badge.loading {{ color: var(--text-muted); }}

        /* --- Header --- */
        .header {{
            grid-column: 1 / -1;
            text-align: center;
            padding: 20px;
        }}

        .header h1 {{ margin: 0; font-size: 32px; color: #333; }}
        .header p {{ margin: 5px 0 0; color: var(--text-muted); }}

        /* --- Health Stats --- */
        .status-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}

        .status-item {{
            text-align: center;
            padding: 20px;
            border-radius: 25px;
            box-shadow: var(--clay-shadow-in);
        }}

        .status-label {{ font-size: 13px; color: var(--text-muted); margin-bottom: 10px; }}
        .status-value {{ font-size: 18px; font-weight: 700; }}

        /* --- Console --- */
        #console {{
            background: #2a2a2a;
            color: #50fa7b;
            font-family: 'Courier New', Courier, monospace;
            padding: 20px;
            border-radius: 20px;
            height: 200px;
            overflow-y: auto;
            font-size: 13px;
            box-shadow: inset 0 4px 10px rgba(0,0,0,0.5);
        }}
        .log-entry {{ margin-bottom: 5px; }}
        .log-time {{ color: #bd93f9; }}

    </style>
</head>
<body>

    <div class="container">
        <header class="header">
            <h1>📚 R.S Education <span style="color: var(--accent-blue)">Solution</span></h1>
            <p>Newsletter Control Center • Premium Testing UI</p>
        </header>

        <!-- Sidebar / Stats -->
        <aside>
            <div class="clay-card">
                <div class="clay-title"><span>🏥</span> Service Health</div>
                <div class="status-grid">
                    <div class="status-item">
                        <div class="status-label">Database</div>
                        <div id="db-status" class="status-value badge loading">Checking...</div>
                    </div>
                    <div class="status-item">
                        <div class="status-label">Scheduler</div>
                        <div id="sched-status" class="status-value badge loading">Checking...</div>
                    </div>
                </div>
                <div style="margin-top: 20px; text-align: center;">
                    <button class="clay-btn" onclick="updateHealth()">🔄 Refresh Status</button>
                </div>
            </div>

            <div class="clay-card">
                <div class="clay-title"><span>🔐</span> Authentication</div>
                <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 15px;">
                    Enter your <b>ADMIN_API_KEY</b> to trigger manual tasks.
                </p>
                <input type="password" id="api-key" class="clay-input" placeholder="Enter API Key..." value="{admin_key}">
            </div>

            <div class="clay-card">
                <div class="clay-title"><span>⚡</span> Admin Actions</div>
                <button class="clay-btn primary" onclick="triggerNow()" style="margin-bottom: 15px;">
                    🚀 Trigger Pipeline Now
                </button>
                <button class="clay-btn danger" onclick="clearConsole()">
                    🗑️ Clear Console Logs
                </button>
            </div>
        </aside>

        <!-- Main Content -->
        <main>
            <div class="clay-card">
                <div class="clay-title"><span>📩</span> Subscribe Student</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <input type="text" id="sub-name" class="clay-input" placeholder="Full Name">
                    <input type="email" id="sub-email" class="clay-input" placeholder="Email Address">
                </div>
                <input type="text" id="sub-interests" class="clay-input" placeholder="Interests (e.g. B.Tech, AI)">
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px;">
                    <input type="number" id="sub-marks" class="clay-input" placeholder="Marks (%)">
                    <input type="number" id="sub-budget" class="clay-input" placeholder="Budget (₹)">
                    <input type="text" id="sub-location" class="clay-input" placeholder="Location">
                </div>
                <button class="clay-btn" style="color: var(--accent-green)" onclick="subscribe()">
                    ✨ Add Subscriber
                </button>
            </div>

            <div class="clay-card">
                <div class="clay-title"><span>🧪</span> Send Test Newsletter</div>
                <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 15px;">
                    Simulates a personalized newsletter without saving to database.
                </p>
                <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 15px;">
                    <input type="email" id="test-email" class="clay-input" placeholder="Recipient Email">
                    <button class="clay-btn primary" onclick="sendTest()">📬 Send Test</button>
                </div>
            </div>

            <div class="clay-card" style="padding: 15px;">
                <div class="clay-title" style="margin-bottom: 10px; font-size: 18px;">
                    <span>📜</span> Activity Logs
                </div>
                <div id="console">
                    <div class="log-entry">Dashboard initialized...</div>
                </div>
            </div>

            <div class="clay-card">
                <div class="clay-title" style="display: flex; justify-content: space-between;">
                    <span>👥</span> Subscribed Users
                    <button class="clay-btn" onclick="fetchUsers()" style="width: auto; padding: 5px 15px; font-size: 12px;">🔄 Load Users</button>
                </div>
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                        <thead>
                            <tr style="text-align: left; border-bottom: 1px solid #ddd;">
                                <th style="padding: 10px;">Name</th>
                                <th style="padding: 10px;">Email</th>
                                <th style="padding: 10px;">Location</th>
                                <th style="padding: 10px;">Last Sent</th>
                            </tr>
                        </thead>
                        <tbody id="user-table-body">
                            <tr>
                                <td colspan="4" style="text-align: center; padding: 20px; color: var(--text-muted);">
                                    Enter API key and click "Load Users" to see the list.
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </main>
    </div>

    <script>
        const logPanel = document.getElementById('console');

        function log(msg, type = 'info') {{
            const time = new Date().toLocaleTimeString();
            const div = document.createElement('div');
            div.className = 'log-entry';
            let color = '#50fa7b';
            if (type === 'error') color = '#ff5555';
            if (type === 'warn') color = '#ffb86c';
            
            div.innerHTML = `<span class="log-time">[${{time}}]</span> <span style="color: ${{color}}">${{msg}}</span>`;
            logPanel.appendChild(div);
            logPanel.scrollTop = logPanel.scrollHeight;
        }}

        async function updateHealth() {{
            try {{
                const res = await fetch('/health');
                const data = await res.json();
                
                const db = document.getElementById('db-status');
                const sched = document.getElementById('sched-status');
                
                db.innerText = data.database;
                db.className = 'status-value badge ' + (data.database.includes('connected') ? 'success' : 'error');
                
                sched.innerText = data.scheduler.running ? 'Active' : 'Stopped';
                sched.className = 'status-value badge ' + (data.scheduler.running ? 'success' : 'error');
                
                log('Health status updated.');
            }} catch (e) {{
                log('Failed to fetch health status', 'error');
            }}
        }}

        async function subscribe() {{
            const body = {{
                name: document.getElementById('sub-name').value,
                email: document.getElementById('sub-email').value,
                interests: document.getElementById('sub-interests').value.split(',').map(s => s.trim()),
                marks: parseInt(document.getElementById('sub-marks').value) || null,
                budget: parseInt(document.getElementById('sub-budget').value) || null,
                location: document.getElementById('sub-location').value
            }};

            if (!body.email || !body.name) return log('Name and Email are required!', 'error');

            log(`Subscribing ${{body.email}}...`);
            try {{
                const res = await fetch('/subscribe', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(body)
                }});
                const data = await res.json();
                if (res.ok) log('✅ ' + data.message);
                else log('❌ ' + data.detail, 'error');
            }} catch (e) {{
                log('Network error during subscription', 'error');
            }}
        }}

        async function sendTest() {{
            const email = document.getElementById('test-email').value;
            const key = document.getElementById('api-key').value;
            if (!email) return log('Test email required!', 'error');

            log(`Sending test newsletter to ${{email}}...`);
            try {{
                const res = await fetch('/send-test', {{
                    method: 'POST',
                    headers: {{ 
                        'Content-Type': 'application/json',
                        'X-API-KEY': key
                    }},
                    body: JSON.stringify({{ email: email }})
                }});
                const data = await res.json();
                if (res.ok) log('✅ Test newsletter sent!');
                else log('❌ Error: ' + (data.detail || 'Check API Key'), 'error');
            }} catch (e) {{
                log('Network error during test send', 'error');
            }}
        }}

        async function triggerNow() {{
            const key = document.getElementById('api-key').value;
            log('Triggering full pipeline manual run...');
            try {{
                const res = await fetch('/trigger-now', {{
                    method: 'POST',
                    headers: {{ 'X-API-KEY': key }}
                }});
                const data = await res.json();
                if (res.ok) log('🎉 Pipeline completed! ' + JSON.stringify(data.summary));
                else log('❌ Error: ' + (data.detail || 'Authentication failed'), 'error');
            }} catch (e) {{
                log('Network error during pipeline trigger', 'error');
            }}
        }}

        async function fetchUsers() {{
            const key = document.getElementById('api-key').value;
            if (!key) return log('Admin API Key is required to view users!', 'error');

            log('Fetching user list...');
            try {{
                const res = await fetch('/users', {{
                    headers: {{ 'X-API-KEY': key }}
                }});
                const data = await res.json();
                if (res.ok) {{
                    const tbody = document.getElementById('user-table-body');
                    if (data.users.length === 0) {{
                        tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 20px;">No users found.</td></tr>';
                    }} else {{
                        tbody.innerHTML = data.users.map(u => `
                            <tr style="border-bottom: 1px solid #eee;">
                                <td style="padding: 10px;">${{u.name}}</td>
                                <td style="padding: 10px;">${{u.email}}</td>
                                <td style="padding: 10px;">${{u.location || 'N/A'}}</td>
                                <td style="padding: 10px;">${{u.last_sent ? new Date(u.last_sent).toLocaleDateString() : 'Never'}}</td>
                            </tr>
                        `).join('');
                        log(`✅ Loaded ${{data.users.length}} users.`);
                    }}
                } else {{
                    log('❌ Error: ' + (data.detail || 'Authentication failed'), 'error');
                }}
            } catch (e) {{
                log('Network error during user fetch', 'error');
            }}
        }}

        function clearConsole() {{
            logPanel.innerHTML = '<div class="log-entry">Console cleared. Ready.</div>';
        }}

        // Initial load
        updateHealth();
        setInterval(updateHealth, 30000); // Auto refresh every 30s

    </script>
</body>
</html>"""
