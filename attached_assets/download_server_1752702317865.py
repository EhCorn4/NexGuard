#!/usr/bin/env python3
"""
NexGuard Bot Download Server
Provides a web interface for downloading the complete bot package
"""

from flask import Flask, render_template_string, send_file, jsonify
import os
from datetime import datetime

app = Flask(__name__)

# HTML template for download page
DOWNLOAD_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NexGuard Bot - Download</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .container {
            background: white;
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 600px;
            width: 90%;
            text-align: center;
        }
        
        .logo {
            font-size: 2.5rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 1rem;
        }
        
        .version {
            background: #667eea;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
            margin-bottom: 2rem;
            display: inline-block;
        }
        
        h1 {
            color: #333;
            margin-bottom: 1rem;
            font-size: 2rem;
        }
        
        .description {
            color: #666;
            line-height: 1.6;
            margin-bottom: 2rem;
        }
        
        .features {
            text-align: left;
            margin: 2rem 0;
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
        }
        
        .features ul {
            list-style: none;
            padding: 0;
        }
        
        .features li {
            padding: 0.5rem 0;
            border-bottom: 1px solid #eee;
        }
        
        .features li:last-child {
            border-bottom: none;
        }
        
        .features li:before {
            content: "✅ ";
            margin-right: 0.5rem;
        }
        
        .download-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            border: none;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
            margin: 1rem 0;
            display: inline-block;
            text-decoration: none;
        }
        
        .download-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }
        
        .info-item {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        }
        
        .info-item h3 {
            color: #667eea;
            margin-bottom: 0.5rem;
        }
        
        .info-item p {
            color: #666;
            font-size: 0.9rem;
        }
        
        .footer {
            margin-top: 2rem;
            padding-top: 2rem;
            border-top: 1px solid #eee;
            color: #999;
            font-size: 0.9rem;
        }
        
        @media (max-width: 600px) {
            .container {
                padding: 2rem;
            }
            
            h1 {
                font-size: 1.5rem;
            }
            
            .logo {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🛡️ NexGuard</div>
        <div class="version">Version 2.0.0</div>
        
        <h1>Complete Bot Package</h1>
        <p class="description">
            Download the complete NexGuard Discord bot with all features, documentation, 
            and setup files. Everything you need to run your own advanced moderation bot.
        </p>
        
        <div class="features">
            <h3>📦 Package Contents</h3>
            <ul>
                <li>Complete bot source code with 50 slash commands</li>
                <li>AI-powered welcome system with OpenAI integration</li>
                <li>Advanced AutoMod with 5 detection types</li>
                <li>Comprehensive logging system</li>
                <li>Advanced ticket system with modal forms</li>
                <li>Web dashboard for server management</li>
                <li>Production deployment configuration</li>
                <li>Complete documentation and setup guides</li>
            </ul>
        </div>
        
        <div class="info-grid">
            <div class="info-item">
                <h3>📁 Size</h3>
                <p>{{ file_size }}</p>
            </div>
            <div class="info-item">
                <h3>📅 Created</h3>
                <p>{{ created_date }}</p>
            </div>
            <div class="info-item">
                <h3>🐍 Python</h3>
                <p>3.8+ Required</p>
            </div>
            <div class="info-item">
                <h3>🗄️ Database</h3>
                <p>SQLite Included</p>
            </div>
        </div>
        
        <a href="/download" class="download-btn">
            📥 Download NexGuard Bot v2.0.0
        </a>
        
        <div class="footer">
            <p>After download, run <code>install.sh</code> to get started</p>
            <p>Complete setup instructions included in README.md</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def download_page():
    """Main download page"""
    zip_file = "nexguard-bot-v2.0.0-20250710.zip"
    
    # Get file size
    file_size = "N/A"
    if os.path.exists(zip_file):
        size_bytes = os.path.getsize(zip_file)
        file_size = f"{size_bytes / (1024*1024):.2f} MB"
    
    return render_template_string(DOWNLOAD_PAGE, 
                                file_size=file_size,
                                created_date=datetime.now().strftime("%Y-%m-%d"))

@app.route('/download')
def download_file():
    """Download the bot package"""
    zip_file = "nexguard-bot-v2.0.0-20250710.zip"
    
    if os.path.exists(zip_file):
        return send_file(zip_file, 
                        as_attachment=True,
                        download_name="nexguard-bot-v2.0.0.zip")
    else:
        return jsonify({"error": "Download file not found"}), 404

@app.route('/api/info')
def package_info():
    """Get package information"""
    zip_file = "nexguard-bot-v2.0.0-20250710.zip"
    
    info = {
        "name": "NexGuard Discord Bot",
        "version": "2.0.0",
        "file_exists": os.path.exists(zip_file),
        "file_size": f"{os.path.getsize(zip_file) / (1024*1024):.2f} MB" if os.path.exists(zip_file) else "N/A",
        "created": datetime.now().isoformat(),
        "features": [
            "50 slash commands across 6 categories",
            "AI-powered welcome messages",
            "Advanced AutoMod system",
            "Comprehensive logging",
            "Ticket system with transcripts",
            "Web dashboard",
            "Production deployment ready"
        ]
    }
    
    return jsonify(info)

if __name__ == '__main__':
    print("Starting NexGuard Bot Download Server...")
    print("Visit http://localhost:3000 to download the bot package")
    app.run(host='0.0.0.0', port=3000, debug=False)