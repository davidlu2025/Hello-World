#!/usr/bin/env python3
"""
PDF to Slides Generator Agent

An autonomous agent that monitors directories for new PDF files and automatically
generates presentation slides from research papers.
"""

import os
import sys
import time
import json
import logging
import argparse
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import schedule

from pdf_to_slides_generator import PDFProcessor, SlideGenerator, SlideFormatter

class AgentConfig:
    """Configuration management for the slide generator agent."""
    
    def __init__(self, config_path: str = "agent_config.json"):
        self.config_path = config_path
        self.default_config = {
            "watch_directories": ["./input_pdfs"],
            "output_directory": "./generated_slides",
            "processed_directory": "./processed_pdfs",
            "log_directory": "./logs",
            "auto_process": True,
            "output_format": "markdown",
            "audience": "academic",
            "check_interval": 30,
            "max_concurrent_jobs": 2,
            "notification_webhook": None,
            "email_notifications": False
        }
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Load configuration from file or create default."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                for key, value in self.default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                logging.error(f"Error loading config: {e}. Using defaults.")
                return self.default_config.copy()
        else:
            self.save_config(self.default_config)
            return self.default_config.copy()
    
    def save_config(self, config: Dict = None) -> None:
        """Save configuration to file."""
        config = config or self.config
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving config: {e}")
    
    def update_config(self, updates: Dict) -> None:
        """Update configuration with new values."""
        self.config.update(updates)
        self.save_config()

class ProcessingJob:
    """Represents a PDF processing job."""
    
    def __init__(self, pdf_path: str, output_path: str, config: Dict):
        self.pdf_path = pdf_path
        self.output_path = output_path
        self.config = config
        self.status = "pending"
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.error_message = None
        self.slides_count = 0

class PDFWatcher(FileSystemEventHandler):
    """File system event handler for monitoring PDF files."""
    
    def __init__(self, agent):
        self.agent = agent
        super().__init__()
    
    def on_created(self, event):
        """Handle new file creation events."""
        if not event.is_directory and event.src_path.lower().endswith('.pdf'):
            logging.info(f"New PDF detected: {event.src_path}")
            self.agent.queue_processing_job(event.src_path)
    
    def on_moved(self, event):
        """Handle file move events."""
        if not event.is_directory and event.dest_path.lower().endswith('.pdf'):
            logging.info(f"PDF moved to watch directory: {event.dest_path}")
            self.agent.queue_processing_job(event.dest_path)

class SlideGeneratorAgent:
    """Main agent class for autonomous PDF to slides generation."""
    
    def __init__(self, config_path: str = "agent_config.json"):
        self.config_manager = AgentConfig(config_path)
        self.config = self.config_manager.config
        self.setup_logging()
        self.setup_directories()
        
        self.processing_queue = []
        self.active_jobs = {}
        self.completed_jobs = []
        self.observer = None
        self.running = False
        
        logging.info("Slide Generator Agent initialized")
    
    def setup_logging(self):
        """Setup logging configuration."""
        log_dir = Path(self.config["log_directory"])
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"agent_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def setup_directories(self):
        """Create necessary directories."""
        directories = [
            self.config["output_directory"],
            self.config["processed_directory"],
            self.config["log_directory"]
        ] + self.config["watch_directories"]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            logging.info(f"Directory ready: {directory}")
    
    def queue_processing_job(self, pdf_path: str):
        """Add a new PDF processing job to the queue."""
        pdf_name = Path(pdf_path).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        output_format = self.config.get("output_format", "markdown").lower()
        if output_format == "json":
            extension = ".json"
        elif output_format == "html":
            extension = ".html"
        else:
            extension = ".md"
        
        output_filename = f"{pdf_name}_{timestamp}{extension}"
        output_path = os.path.join(self.config["output_directory"], output_filename)
        
        job = ProcessingJob(pdf_path, output_path, self.config)
        self.processing_queue.append(job)
        
        logging.info(f"Queued processing job: {pdf_path} -> {output_path}")
        
        if self.config["auto_process"]:
            self.process_queue()
    
    def process_queue(self):
        """Process pending jobs in the queue."""
        max_concurrent = self.config["max_concurrent_jobs"]
        
        while (len(self.active_jobs) < max_concurrent and 
               len(self.processing_queue) > 0):
            
            job = self.processing_queue.pop(0)
            self.start_processing_job(job)
    
    def start_processing_job(self, job: ProcessingJob):
        """Start processing a single job in a separate thread."""
        job.status = "processing"
        job.started_at = datetime.now()
        
        thread = threading.Thread(target=self.process_pdf_job, args=(job,))
        thread.daemon = True
        thread.start()
        
        self.active_jobs[job.pdf_path] = job
        logging.info(f"Started processing: {job.pdf_path}")
    
    def process_pdf_job(self, job: ProcessingJob):
        """Process a single PDF file and generate slides."""
        try:
            logging.info(f"Processing PDF: {job.pdf_path}")
            
            processor = PDFProcessor(job.pdf_path)
            
            processor.extract_text()
            sections = processor.identify_sections()
            
            if not sections:
                raise Exception("No sections found in PDF")
            
            generator = SlideGenerator(sections, job.config.get("audience", "academic"))
            slides = generator.generate_slides()
            
            if not slides:
                raise Exception("No slides generated")
            
            output_format = job.config["output_format"].lower()
            if output_format == "json":
                content = SlideFormatter.format_as_json(slides)
                job.output_path = job.output_path.replace('.md', '.json')
            elif output_format == "html":
                content = SlideFormatter.format_as_html(slides)
                job.output_path = job.output_path.replace('.md', '.html')
            else:
                content = SlideFormatter.format_as_markdown(slides)
            
            with open(job.output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            processed_path = os.path.join(
                job.config["processed_directory"],
                os.path.basename(job.pdf_path)
            )
            
            if os.path.exists(job.pdf_path):
                os.rename(job.pdf_path, processed_path)
            
            job.status = "completed"
            job.completed_at = datetime.now()
            job.slides_count = len(slides)
            
            logging.info(f"Successfully processed: {job.pdf_path}")
            logging.info(f"Generated {len(slides)} slides: {job.output_path}")
            
            self.send_notification(job, "success")
            
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.now()
            
            logging.error(f"Failed to process {job.pdf_path}: {e}")
            self.send_notification(job, "error")
        
        finally:
            if job.pdf_path in self.active_jobs:
                del self.active_jobs[job.pdf_path]
            self.completed_jobs.append(job)
            
            self.process_queue()
    
    def send_notification(self, job: ProcessingJob, status: str):
        """Send notification about job completion."""
        if status == "success":
            message = f"✅ Successfully generated slides for {os.path.basename(job.pdf_path)}"
            message += f"\n📊 Generated {job.slides_count} slides"
            message += f"\n📁 Output: {job.output_path}"
        else:
            message = f"❌ Failed to process {os.path.basename(job.pdf_path)}"
            message += f"\n🔍 Error: {job.error_message}"
        
        logging.info(f"Notification: {message}")
        
        if self.config.get("notification_webhook"):
            pass
    
    def start_watching(self):
        """Start monitoring directories for new PDF files."""
        self.observer = Observer()
        
        for watch_dir in self.config["watch_directories"]:
            if os.path.exists(watch_dir):
                self.observer.schedule(
                    PDFWatcher(self), 
                    watch_dir, 
                    recursive=True
                )
                logging.info(f"Watching directory: {watch_dir}")
        
        self.observer.start()
        logging.info("File monitoring started")
    
    def stop_watching(self):
        """Stop monitoring directories."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logging.info("File monitoring stopped")
    
    def scan_existing_files(self):
        """Scan watch directories for existing PDF files."""
        for watch_dir in self.config["watch_directories"]:
            if os.path.exists(watch_dir):
                for pdf_file in Path(watch_dir).glob("**/*.pdf"):
                    if pdf_file.is_file():
                        logging.info(f"Found existing PDF: {pdf_file}")
                        self.queue_processing_job(str(pdf_file))
    
    def get_status(self) -> Dict:
        """Get current agent status."""
        return {
            "running": self.running,
            "queue_length": len(self.processing_queue),
            "active_jobs": len(self.active_jobs),
            "completed_jobs": len(self.completed_jobs),
            "watch_directories": self.config["watch_directories"],
            "last_updated": datetime.now().isoformat()
        }
    
    def get_job_history(self, limit: int = 10) -> List[Dict]:
        """Get recent job history."""
        recent_jobs = sorted(
            self.completed_jobs, 
            key=lambda x: x.completed_at or x.created_at, 
            reverse=True
        )[:limit]
        
        return [
            {
                "pdf_path": job.pdf_path,
                "output_path": job.output_path,
                "status": job.status,
                "slides_count": job.slides_count,
                "created_at": job.created_at.isoformat(),
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "error_message": job.error_message
            }
            for job in recent_jobs
        ]
    
    def run(self):
        """Main agent loop."""
        self.running = True
        logging.info("Starting Slide Generator Agent")
        
        schedule.every(self.config["check_interval"]).seconds.do(self.process_queue)
        
        self.start_watching()
        
        self.scan_existing_files()
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Received shutdown signal")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Gracefully shutdown the agent."""
        logging.info("Shutting down agent...")
        self.running = False
        self.stop_watching()
        
        while self.active_jobs:
            logging.info(f"Waiting for {len(self.active_jobs)} active jobs to complete...")
            time.sleep(2)
        
        logging.info("Agent shutdown complete")

def main():
    """Main entry point for the agent."""
    parser = argparse.ArgumentParser(description="PDF to Slides Generator Agent")
    parser.add_argument("--config", default="agent_config.json", 
                       help="Path to configuration file")
    parser.add_argument("--scan-only", action="store_true",
                       help="Scan existing files and exit")
    parser.add_argument("--status", action="store_true",
                       help="Show agent status and exit")
    parser.add_argument("--process", type=str,
                       help="Process a specific PDF file")
    
    args = parser.parse_args()
    
    agent = SlideGeneratorAgent(args.config)
    
    if args.status:
        status = agent.get_status()
        print(json.dumps(status, indent=2))
        return
    
    if args.process:
        if os.path.exists(args.process):
            agent.queue_processing_job(args.process)
            agent.process_queue()
            while agent.active_jobs:
                time.sleep(1)
        else:
            print(f"Error: File not found: {args.process}")
            sys.exit(1)
        return
    
    if args.scan_only:
        agent.scan_existing_files()
        agent.process_queue()
        while agent.active_jobs:
            time.sleep(1)
        return
    
    agent.run()

if __name__ == "__main__":
    main()
