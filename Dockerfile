FROM ollama/ollama

LABEL maintainer="AI Project Team"
LABEL description="Ollama instance for AI project"
LABEL version="1.0"

# Set working directory
WORKDIR /root

# Expose Ollama API port
EXPOSE 11434

#web ui
#docker pull ghcr.io/open-webui/open-webui:main