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

## Running the Application

1. Start the container:

```bash
docker run -p 80:80 -p 5000:5000 video-processing-bot
```

2. Access the application:

- Frontend: `http://localhost`
- Backend API: `http://localhost:5000`

## Directory Structure

- `/uploads` - Directory for uploaded videos
- `/separated_videos` - Directory for processed video outputs

## API Endpoints

All API endpoints are prefixed with `/api/`:

- `POST /api/upload` - Upload a video file
- `GET /api/status/:id` - Check processing status
- `GET /api/download/:id` - Download processed video

## Development

### Frontend Development

The frontend is built with React and is served through Nginx. All API requests from the frontend should be prefixed with `/api/`.

### Backend Development

The backend is built with Flask and runs on port 5000. It handles video processing and file management.

## Troubleshooting

If you encounter any issues:

1. Check if the container is running:

```bash
docker ps
```

2. View container logs:

```bash
docker logs <container-id>
```

3. Ensure ports 80 and 5000 are not in use by other applications.

## Security Notes

- The Google API Key is embedded in the Docker image during build time
- Do not share the built image with others
- Keep your API key secure and rotate it regularly

