# Video Processing Bot

A combined web application that provides video processing capabilities with a modern React frontend and Flask backend.

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/ryan0980/20250502_bot_docker_version)

## Features

- Video upload and processing
- Modern React-based user interface
- Flask backend for video processing
- Nginx server for static file serving and API proxying

## Prerequisites

- Docker installed on your system
- Google API Key for video processing

## Building the Application

1. Clone the repository:
```bash
git clone https://github.com/ryan0980/20250502_bot_docker_version.git
cd 20250502_bot_docker_version
```

2. Build the Docker image with your Google API Key:
```bash
docker build --build-arg GOOGLE_API_KEY=your_api_key_here -t video-processing-bot .
```

Replace `your_api_key_here` with your actual Google API Key.

// ... existing code ...
