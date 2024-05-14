# Cleanup Old Container
docker container stop self-registration
docker container rm self-registration

# Build and Run New Container
docker build . --file Dockerfile.local -t self-registration
docker run -d -p 8000:8000 --name self-registration self-registration