#!/usr/bin/env python3
"""
Web Interface for PDF to Slides Generator Agent

A simple Flask web interface to monitor and control the slide generator agent.
"""

import os
import json
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from slide_generator_agent import SlideGeneratorAgent

app = Flask(__name__)
app.config['SECRET_KEY'] = 'slide-generator-agent-key'
app.config['UPLOAD_FOLDER'] = './input_pdfs'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

agent = None
agent_thread = None

def start_agent():
    """Start the agent in a background thread."""
    global agent, agent_thread
    if agent is None:
        agent = SlideGeneratorAgent()
        agent_thread = threading.Thread(target=agent.run, daemon=True)
        agent_thread.start()

@app.route('/')
def index():
    """Main dashboard page."""
    if agent is None:
        start_agent()
    
    status = agent.get_status() if agent else {}
    recent_jobs = agent.get_job_history(5) if agent else []
    
    return render_template('dashboard.html', status=status, recent_jobs=recent_jobs)

@app.route('/api/status')
def api_status():
    """API endpoint for agent status."""
    if agent is None:
        return jsonify({"error": "Agent not running"})
    
    return jsonify(agent.get_status())

@app.route('/api/jobs')
def api_jobs():
    """API endpoint for job history."""
    limit = request.args.get('limit', 10, type=int)
    
    if agent is None:
        return jsonify([])
    
    return jsonify(agent.get_job_history(limit))

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Handle PDF file uploads."""
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        
        if file and file.filename.lower().endswith('.pdf'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            file.save(filepath)
            
            if agent:
                agent.queue_processing_job(filepath)
            
            return redirect(url_for('index'))
    
    return render_template('upload.html')

@app.route('/config', methods=['GET', 'POST'])
def config():
    """Configuration management page."""
    if agent is None:
        start_agent()
    
    if request.method == 'POST':
        config_updates = {}
        
        config_updates['auto_process'] = 'auto_process' in request.form
        config_updates['output_format'] = request.form.get('output_format', 'markdown')
        config_updates['audience'] = request.form.get('audience', 'academic')
        config_updates['max_concurrent_jobs'] = int(request.form.get('max_concurrent_jobs', 2))
        config_updates['check_interval'] = int(request.form.get('check_interval', 30))
        config_updates['llm_enabled'] = request.form.get('llm_enabled', 'true') == 'true'
        config_updates['llm_model'] = request.form.get('llm_model', 'gpt-3.5-turbo')
        
        watch_dirs = request.form.get('watch_directories', '').split('\n')
        config_updates['watch_directories'] = [d.strip() for d in watch_dirs if d.strip()]
        
        if agent:
            agent.config_manager.update_config(config_updates)
        
        return redirect(url_for('config'))
    
    current_config = agent.config if agent else {}
    return render_template('config.html', config=current_config)

@app.route('/download/<path:filename>')
def download_file(filename):
    """Download generated slides."""
    output_dir = agent.config['output_directory'] if agent else './generated_slides'
    filepath = os.path.join(output_dir, filename)
    
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return "File not found", 404

def create_templates():
    """Create template directory and files."""
    template_dir = 'templates'
    os.makedirs(template_dir, exist_ok=True)
    
    dashboard_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>PDF to Slides Generator Agent</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { border-bottom: 2px solid #007bff; padding-bottom: 10px; margin-bottom: 20px; }
        .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }
        .status-card { background: #f8f9fa; padding: 15px; border-radius: 6px; border-left: 4px solid #007bff; }
        .status-card h3 { margin: 0 0 10px 0; color: #333; }
        .status-card .value { font-size: 24px; font-weight: bold; color: #007bff; }
        .jobs-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        .jobs-table th, .jobs-table td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        .jobs-table th { background-color: #f8f9fa; font-weight: bold; }
        .status-success { color: #28a745; }
        .status-failed { color: #dc3545; }
        .status-processing { color: #ffc107; }
        .nav-links { margin-bottom: 20px; }
        .nav-links a { margin-right: 15px; padding: 8px 16px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; }
        .nav-links a:hover { background: #0056b3; }
        .refresh-btn { background: #28a745; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; }
    </style>
    <script>
        function refreshStatus() {
            location.reload();
        }
        setInterval(refreshStatus, 30000); // Auto-refresh every 30 seconds
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>PDF to Slides Generator Agent</h1>
            <div class="nav-links">
                <a href="/">Dashboard</a>
                <a href="/upload">Upload PDF</a>
                <a href="/config">Configuration</a>
                <button class="refresh-btn" onclick="refreshStatus()">Refresh</button>
            </div>
        </div>
        
        <div class="status-grid">
            <div class="status-card">
                <h3>Agent Status</h3>
                <div class="value">{{ "Running" if status.running else "Stopped" }}</div>
            </div>
            <div class="status-card">
                <h3>Queue Length</h3>
                <div class="value">{{ status.queue_length or 0 }}</div>
            </div>
            <div class="status-card">
                <h3>Active Jobs</h3>
                <div class="value">{{ status.active_jobs or 0 }}</div>
            </div>
            <div class="status-card">
                <h3>Completed Jobs</h3>
                <div class="value">{{ status.completed_jobs or 0 }}</div>
            </div>
        </div>
        
        <h2>Recent Jobs</h2>
        <table class="jobs-table">
            <thead>
                <tr>
                    <th>PDF File</th>
                    <th>Status</th>
                    <th>Slides</th>
                    <th>Completed</th>
                    <th>Output</th>
                </tr>
            </thead>
            <tbody>
                {% for job in recent_jobs %}
                <tr>
                    <td>{{ job.pdf_path.split('/')[-1] }}</td>
                    <td class="status-{{ job.status }}">{{ job.status.title() }}</td>
                    <td>{{ job.slides_count or '-' }}</td>
                    <td>{{ job.completed_at[:19] if job.completed_at else '-' }}</td>
                    <td>
                        {% if job.status == 'completed' %}
                        <a href="/download/{{ job.output_path.split('/')[-1] }}">Download</a>
                        {% else %}
                        -
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        {% if not recent_jobs %}
        <p>No jobs processed yet. <a href="/upload">Upload a PDF</a> to get started!</p>
        {% endif %}
    </div>
</body>
</html>
    '''
    
    with open(os.path.join(template_dir, 'dashboard.html'), 'w') as f:
        f.write(dashboard_html)
    
    upload_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Upload PDF - Slide Generator Agent</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { border-bottom: 2px solid #007bff; padding-bottom: 10px; margin-bottom: 30px; }
        .upload-area { border: 2px dashed #007bff; padding: 40px; text-align: center; border-radius: 8px; margin: 20px 0; }
        .upload-area:hover { background-color: #f8f9fa; }
        input[type="file"] { margin: 20px 0; }
        .submit-btn { background: #007bff; color: white; border: none; padding: 12px 24px; border-radius: 4px; cursor: pointer; font-size: 16px; }
        .submit-btn:hover { background: #0056b3; }
        .nav-links a { margin-right: 15px; padding: 8px 16px; background: #6c757d; color: white; text-decoration: none; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Upload PDF</h1>
            <div class="nav-links">
                <a href="/">← Back to Dashboard</a>
            </div>
        </div>
        
        <form method="post" enctype="multipart/form-data">
            <div class="upload-area">
                <h3>Select PDF File</h3>
                <p>Choose a research paper PDF to generate slides</p>
                <input type="file" name="file" accept=".pdf" required>
            </div>
            <button type="submit" class="submit-btn">Upload and Process</button>
        </form>
        
        <div style="margin-top: 30px; padding: 20px; background: #e9ecef; border-radius: 6px;">
            <h4>Instructions:</h4>
            <ul>
                <li>Upload research papers in PDF format</li>
                <li>The agent will automatically process the file</li>
                <li>Generated slides will appear in the dashboard</li>
                <li>Maximum file size: 50MB</li>
            </ul>
        </div>
    </div>
</body>
</html>
    '''
    
    with open(os.path.join(template_dir, 'upload.html'), 'w') as f:
        f.write(upload_html)
    
    config_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Configuration - Slide Generator Agent</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { border-bottom: 2px solid #007bff; padding-bottom: 10px; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input, .form-group select, .form-group textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .form-group textarea { height: 100px; }
        .checkbox-group { display: flex; align-items: center; }
        .checkbox-group input { width: auto; margin-right: 10px; }
        .submit-btn { background: #007bff; color: white; border: none; padding: 12px 24px; border-radius: 4px; cursor: pointer; font-size: 16px; }
        .submit-btn:hover { background: #0056b3; }
        .nav-links a { margin-right: 15px; padding: 8px 16px; background: #6c757d; color: white; text-decoration: none; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Agent Configuration</h1>
            <div class="nav-links">
                <a href="/">← Back to Dashboard</a>
            </div>
        </div>
        
        <form method="post">
            <div class="form-group checkbox-group">
                <input type="checkbox" name="auto_process" {{ "checked" if config.auto_process else "" }}>
                <label>Auto-process new PDFs</label>
            </div>
            
            <div class="form-group">
                <label>Output Format:</label>
                <select name="output_format">
                    <option value="markdown" {{ "selected" if config.output_format == "markdown" else "" }}>Markdown</option>
                    <option value="json" {{ "selected" if config.output_format == "json" else "" }}>JSON</option>
                    <option value="html" {{ "selected" if config.output_format == "html" else "" }}>HTML</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>Target Audience:</label>
                <select name="audience">
                    <option value="academic" {{ "selected" if config.audience == "academic" else "" }}>Academic</option>
                    <option value="general" {{ "selected" if config.audience == "general" else "" }}>General</option>
                    <option value="educational" {{ "selected" if config.audience == "educational" else "" }}>Educational</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>LLM Analysis:</label>
                <select name="llm_enabled">
                    <option value="true" {{ "selected" if config.llm_enabled else "" }}>Enabled</option>
                    <option value="false" {{ "selected" if not config.llm_enabled else "" }}>Disabled</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>LLM Model:</label>
                <select name="llm_model">
                    <option value="gpt-3.5-turbo" {{ "selected" if config.llm_model == "gpt-3.5-turbo" else "" }}>GPT-3.5 Turbo</option>
                    <option value="gpt-4" {{ "selected" if config.llm_model == "gpt-4" else "" }}>GPT-4</option>
                    <option value="gpt-4-turbo" {{ "selected" if config.llm_model == "gpt-4-turbo" else "" }}>GPT-4 Turbo</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>Max Concurrent Jobs:</label>
                <input type="number" name="max_concurrent_jobs" value="{{ config.max_concurrent_jobs or 2 }}" min="1" max="10">
            </div>
            
            <div class="form-group">
                <label>Check Interval (seconds):</label>
                <input type="number" name="check_interval" value="{{ config.check_interval or 30 }}" min="10" max="300">
            </div>
            
            <div class="form-group">
                <label>Watch Directories (one per line):</label>
                <textarea name="watch_directories">{{ '\n'.join(config.watch_directories or []) }}</textarea>
            </div>
            
            <button type="submit" class="submit-btn">Save Configuration</button>
        </form>
    </div>
</body>
</html>
    '''
    
    with open(os.path.join(template_dir, 'config.html'), 'w') as f:
        f.write(config_html)

if __name__ == '__main__':
    os.makedirs('input_pdfs', exist_ok=True)
    os.makedirs('generated_slides', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    create_templates()
    
    print("Starting PDF to Slides Generator Agent Web Interface...")
    print("Access the dashboard at: http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
