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

```
.
├── Dockerfile              # Main Docker configuration
├── nginx.conf             # Nginx server configuration
├── start.sh               # Container startup script
├── uploads/               # Directory for uploaded videos
└── separated_videos/      # Directory for processed video outputs
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

- `GOOGLE_API_KEY`: Required for video processing
- `FLASK_APP`: Set to `app.py` for Flask application
- `FLASK_ENV`: Set to `production` for production environment

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
   - API Key issues: Verify your Google API Key is valid
   - Storage issues: Check available disk space
   - Memory issues: Ensure sufficient RAM is available

## Security Notes

- The Google API Key is embedded in the Docker image during build time
- Do not share the built image with others
- Keep your API key secure and rotate it regularly
- Use HTTPS in production environments
- Implement proper authentication for API endpoints

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
