# PDF to Slides Generator Agent

An autonomous agent that monitors directories for new PDF files and automatically generates presentation slides from research papers. The agent runs continuously in the background and provides both CLI and web interfaces for monitoring and control.

## Features

### 🤖 Autonomous Operation
- **File Monitoring**: Automatically detects new PDF files in configured directories
- **Queue Management**: Processes multiple PDFs concurrently with configurable limits
- **Background Processing**: Runs as a daemon service with minimal user intervention
- **Error Handling**: Robust error handling with detailed logging and notifications

### 📊 Web Dashboard
- **Real-time Status**: Monitor agent status, queue length, and active jobs
- **Job History**: View completed jobs with download links for generated slides
- **File Upload**: Web interface for uploading PDFs directly
- **Configuration**: Web-based configuration management

### 🔧 Flexible Configuration
- **Multiple Output Formats**: Markdown and JSON slide formats
- **Audience Adaptation**: Academic, general, or educational presentation styles
- **Concurrent Processing**: Configurable number of simultaneous jobs
- **Directory Watching**: Monitor multiple directories for new files

### 📝 Advanced Content Extraction
- **Improved Section Detection**: Better identification of academic paper sections
- **Domain-specific Scoring**: Enhanced content extraction for research terminology
- **Text Preprocessing**: Automatic cleaning of headers, footers, and artifacts
- **Metadata Extraction**: Automatic title and author detection

## Installation

1. **Install Dependencies**:
```bash
pip install -r agent_requirements.txt
```

2. **Create Directories**:
```bash
mkdir -p input_pdfs generated_slides processed_pdfs logs
```

3. **Initialize Configuration**:
```bash
python slide_generator_agent.py --status
```

## Usage

### Command Line Interface

#### Start the Agent
```bash
# Run the agent continuously
python slide_generator_agent.py

# Use custom configuration file
python slide_generator_agent.py --config my_config.json
```

#### Process Single File
```bash
# Process a specific PDF
python slide_generator_agent.py --process research_paper.pdf
```

#### Scan Existing Files
```bash
# Process all PDFs in watch directories and exit
python slide_generator_agent.py --scan-only
```

#### Check Status
```bash
# Show current agent status
python slide_generator_agent.py --status
```

### Web Interface

1. **Start the Web Interface**:
```bash
python agent_web_interface.py
```

2. **Access Dashboard**: Open http://localhost:5000 in your browser

3. **Features Available**:
   - **Dashboard**: Real-time status and job monitoring
   - **Upload**: Direct PDF upload interface
   - **Configuration**: Web-based settings management
   - **Downloads**: Access generated slides

## Configuration

The agent uses a JSON configuration file (`agent_config.json`) with the following options:

```json
{
  "watch_directories": ["./input_pdfs"],
  "output_directory": "./generated_slides",
  "processed_directory": "./processed_pdfs",
  "log_directory": "./logs",
  "auto_process": true,
  "output_format": "markdown",
  "audience": "academic",
  "check_interval": 30,
  "max_concurrent_jobs": 2,
  "notification_webhook": null,
  "email_notifications": false
}
```

### Configuration Options

- **`watch_directories`**: List of directories to monitor for new PDFs
- **`output_directory`**: Where generated slides are saved
- **`processed_directory`**: Where processed PDFs are moved
- **`auto_process`**: Whether to automatically process new files
- **`output_format`**: "markdown" or "json"
- **`audience`**: "academic", "general", or "educational"
- **`max_concurrent_jobs`**: Number of simultaneous processing jobs
- **`check_interval`**: How often to check for new jobs (seconds)

## Agent Workflow

1. **File Detection**: Agent monitors configured directories for new PDF files
2. **Queue Management**: New files are added to the processing queue
3. **Concurrent Processing**: Multiple PDFs can be processed simultaneously
4. **Content Extraction**: Advanced algorithms extract meaningful content
5. **Slide Generation**: Creates structured presentation slides
6. **File Management**: Moves processed PDFs to avoid reprocessing
7. **Notification**: Logs completion and optionally sends notifications

## Directory Structure

```
project/
├── slide_generator_agent.py      # Main agent implementation
├── agent_web_interface.py        # Web dashboard
├── pdf_to_slides_generator.py    # Core PDF processing
├── agent_requirements.txt        # Dependencies
├── agent_config.json            # Configuration (auto-generated)
├── input_pdfs/                  # Watch directory for new PDFs
├── generated_slides/            # Output directory for slides
├── processed_pdfs/              # Processed PDFs storage
├── logs/                        # Agent logs
└── templates/                   # Web interface templates
```

## API Endpoints

The web interface provides REST API endpoints:

- **`GET /api/status`**: Current agent status
- **`GET /api/jobs?limit=N`**: Recent job history
- **`POST /upload`**: Upload PDF files
- **`GET /download/<filename>`**: Download generated slides

## Logging

The agent provides comprehensive logging:

- **File Locations**: `./logs/agent_YYYYMMDD.log`
- **Log Levels**: INFO, ERROR, WARNING
- **Content**: File processing, errors, status changes
- **Rotation**: Daily log files

## Example Usage Scenarios

### Research Lab Setup
```bash
# Configure for academic papers
python slide_generator_agent.py --config lab_config.json
```

### Conference Presentation Prep
```bash
# Process specific paper for conference
python slide_generator_agent.py --process important_paper.pdf
```

### Batch Processing
```bash
# Process all papers in directory
cp *.pdf input_pdfs/
python slide_generator_agent.py --scan-only
```

### Continuous Monitoring
```bash
# Run agent as background service
nohup python slide_generator_agent.py > agent.log 2>&1 &
```

## Troubleshooting

### Common Issues

1. **No PDFs Detected**:
   - Check watch directory permissions
   - Verify directory paths in configuration
   - Check agent logs for errors

2. **Processing Failures**:
   - Ensure PDF files are not corrupted
   - Check available disk space
   - Review error messages in logs

3. **Web Interface Issues**:
   - Verify Flask is installed
   - Check port 5000 availability
   - Ensure templates directory exists

### Debug Mode

Enable detailed logging:
```bash
# Set environment variable for debug mode
export AGENT_DEBUG=1
python slide_generator_agent.py
```

## Performance Considerations

- **Memory Usage**: Each concurrent job uses ~100-200MB RAM
- **Processing Time**: 30-120 seconds per PDF depending on size
- **Disk Space**: Generated slides are typically 1-5KB each
- **CPU Usage**: Moderate during text extraction and processing

## Security Notes

- **File Access**: Agent only processes files in configured directories
- **Web Interface**: No authentication by default (add if needed)
- **File Uploads**: Limited to PDF files with size restrictions
- **Network**: Web interface binds to all interfaces (0.0.0.0)

## Future Enhancements

- **Authentication**: User login for web interface
- **Notifications**: Email/Slack notifications for job completion
- **Templates**: Custom slide templates and themes
- **API Integration**: REST API for external integrations
- **Clustering**: Multi-node agent deployment
- **Analytics**: Processing statistics and performance metrics

## Contributing

To extend the agent:

1. **Add New Features**: Extend the `SlideGeneratorAgent` class
2. **Custom Processors**: Create new PDF processing algorithms
3. **Output Formats**: Add support for PowerPoint, HTML, etc.
4. **Integrations**: Add webhook/API integrations
5. **UI Improvements**: Enhance the web dashboard

## License

This project is open source and available under the MIT License.
