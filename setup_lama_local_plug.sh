{\rtf1\ansi\ansicpg1252\cocoartf2708
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww34360\viewh21040\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 #!/bin/bash\
\
# Shell script to set up Code Llama locally for Java, Spring Boot, MySQL, AWS, and Kubernetes with IntelliJ IDEA integration.\
\
# Step 1: Install Homebrew (macOS package manager) if not already installed\
if ! command -v brew &> /dev/null; then\
    echo "Installing Homebrew (dependency manager)..."\
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || \{\
        echo "Homebrew installation failed!"\
        exit 1\
    \}\
fi\
\
# Step 2: Install required dependencies: CMake, Python, and Git\
echo "Installing dependencies: CMake, Python3, and Git..."\
brew install cmake python git || \{\
    echo "Dependency installation failed!"\
    exit 1\
\}\
\
# Step 3: Clone and build Llama.cpp (lightweight inference library for LLaMA models)\
echo "Cloning and building Llama.cpp for running Code Llama locally..."\
git clone https://github.com/ggerganov/llama.cpp.git || \{\
    echo "Failed to clone Llama.cpp repository!"\
    exit 1\
\}\
cd llama.cpp || exit 1\
make || \{\
    echo "Build process failed! Ensure you have the required build tools."\
    exit 1\
\}\
\
# Step 4: Download the suitable Code Llama model for Java/Spring Boot/MySQL/AWS/Kubernetes\
# Recommended model: Code Llama 13B GGML quantized (balanced for accuracy and performance)\
MODEL_PATH="./models/CodeLlama-13B.ggml.q4_0.bin"\
mkdir -p models\
echo "Downloading the quantized Code Llama 13B model..."\
curl -L -o "$MODEL_PATH" "https://huggingface.co/TheBloke/CodeLlama-13B-GGML/resolve/main/CodeLlama-13B.ggml.q4_0.bin" || \{\
    echo "Failed to download the Code Llama model. Ensure you have an active internet connection for this step."\
    exit 1\
\}\
\
# Step 5: Test the downloaded Code Llama model locally\
echo "Testing the Code Llama model to verify installation..."\
./main -m "$MODEL_PATH" -p "Write a Spring Boot controller for managing users." || \{\
    echo "Code Llama execution failed! Please check your setup."\
    exit 1\
\}\
\
# Step 6: Install Tabby for IntelliJ IDEA plugin integration\
# Tabby allows IntelliJ to perform autocompletion by connecting to Llama.cpp locally.\
echo "Setting up Tabby for IntelliJ IDEA integration..."\
TABBY_DIR="./tabby"\
git clone https://github.com/TabbyML/tabby.git "$TABBY_DIR" || \{\
    echo "Failed to clone Tabby repository!"\
    exit 1\
\}\
cd "$TABBY_DIR" || exit 1\
docker-compose up -d || \{\
    echo "Failed to start Tabby server using Docker!"\
    exit 1\
\}\
\
# Step 7: Configure IntelliJ IDEA plugin to connect to Tabby\
echo "Open IntelliJ IDEA, install the Tabby plugin from 'File > Settings > Plugins > Tabby', and set the server endpoint to:"\
echo "http://localhost:5000"\
\
# Final Message\
echo "Setup Complete! Code Llama with Tabby integration for IntelliJ is now ready."\
echo "Start writing code in IntelliJ, and the autocompletion with Code Llama will work offline and locally."}