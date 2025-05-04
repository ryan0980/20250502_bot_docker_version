# Video Processing Bot

A combined web application that provides video processing capabilities with a modern React frontend and Flask backend. This application allows users to upload videos and process them using Google's video processing API.

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/ryan0980/20250502_bot_docker_version)

## Features

- Video upload and processing
- Modern React-based user interface
- Flask backend for video processing
- Nginx server for static file serving and API proxying
- Docker containerization for easy deployment
- Real-time processing status updates

## Prerequisites

- Docker installed on your system
- Google API Key for video processing
- Git (for cloning the repository)
- At least 4GB of RAM (recommended for video processing)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/ryan0980/20250502_bot_docker_version.git
cd 20250502_bot_docker_version
```

2. Build the Docker image:

```bash
docker build -t video-processing-bot .
```

## Running the Application

1. Start the container with your Google API Key:

```bash
docker run -p 80:80 -p 5000:5000 -e GOOGLE_API_KEY=your_api_key_here video-processing-bot
```

Replace `your_api_key_here` with your actual Google API Key.

2. Access the application:

- Frontend: `http://localhost`
- Backend API: `http://localhost:5000`

## Directory Structure

```
.
├── Dockerfile              # Main Docker configuration
├── nginx.conf             # Nginx server configuration
├── start.sh               # Container startup script
├── frontend/             # React frontend application
├── backend/              # Flask backend application
├── uploads/              # Directory for uploaded videos
└── separated_videos/     # Directory for processed video outputs
```

## API Endpoints

All API endpoints are prefixed with `/api/`:

- `POST /api/upload` - Upload a video file

  - Content-Type: multipart/form-data
  - Returns: Processing ID

- `GET /api/status/:id` - Check processing status

  - Returns: Current status and progress

- `GET /api/download/:id` - Download processed video
  - Returns: Processed video file

## Development

### Frontend Development

The frontend is built with React and is served through Nginx. All API requests from the frontend should be prefixed with `/api/`.

### Backend Development

The backend is built with Flask and runs on port 5000. It handles video processing and file management.

## Environment Variables

The following environment variables are required:

- `GOOGLE_API_KEY`: Required for video processing. Must be provided when running the container.
- `FLASK_APP`: Set to `app.py` for Flask application (automatically set in Dockerfile)
- `FLASK_ENV`: Set to `production` for production environment (automatically set in Dockerfile)

Example of running with environment variables:

```bash
docker run -p 80:80 -p 5000:5000 \
  -e GOOGLE_API_KEY=your_api_key_here \
  video-processing-bot
```

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

3. Common issues:
   - Port conflicts: Ensure ports 80 and 5000 are not in use
   - API Key issues: Verify your Google API Key is valid and properly set
   - Storage issues: Check available disk space
   - Memory issues: Ensure sufficient RAM is available

## Security Notes

- Never commit your Google API Key to version control
- Keep your API key secure and rotate it regularly
- Use HTTPS in production environments
- Implement proper authentication for API endpoints
- Consider using Docker secrets or environment files for sensitive data

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [React](https://reactjs.org/)
- [Flask](https://flask.palletsprojects.com/)
- [Nginx](https://nginx.org/)
- [Docker](https://www.docker.com/)
