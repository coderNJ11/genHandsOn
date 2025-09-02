{\rtf1\ansi\ansicpg1252\cocoartf2708
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww34360\viewh21040\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 #!/bin/bash\
\
# Shell script to install and run Code Llama 13B model locally on macOS for offline, interactive code generation.\
\
# Step 1: Install Homebrew if not already installed\
if ! command -v brew &> /dev/null; then\
  echo "Installing Homebrew... (macOS package manager)"\
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || exit 1\
fi\
\
# Step 2: Install necessary dependencies (CMake, Python, Git)\
echo "Installing required dependencies: cmake, python, and git..."\
brew install cmake python git || exit 1\
\
# Step 3: Clone llama.cpp repository (lightweight inference library for LLaMA models)\
echo "Cloning Llama.cpp repository..."\
git clone https://github.com/ggerganov/llama.cpp.git || exit 1\
cd llama.cpp || exit 1\
\
# Step 4: Build llama.cpp (compiles the necessary binaries to run the Code Llama model)\
echo "Building llama.cpp..."\
make || exit 1\
cd ..\
\
# Step 5: Download Code Llama 13B GGML model (supports code generation for Java, Spring Boot, Kubernetes, Docker, and AWS)\
echo "Downloading the Code Llama 13B model from Hugging Face..."\
curl -L -o "./llama.cpp/models/CodeLlama-13B.ggmlv3.q4_0.bin" "https://huggingface.co/TheBloke/CodeLlama-13B-GGML/resolve/main/CodeLlama-13B.ggmlv3.q4_0.bin"\
\
# Step 6: Clone text-generation-webui for running an interactive UI\
echo "Cloning interactive UI repository (text-generation-webui)..."\
git clone https://github.com/oobabooga/text-generation-webui.git || exit 1\
cd text-generation-webui || exit 1\
\
# Step 7: Install Python dependencies for text-generation-webui\
echo "Installing dependencies for the interactive UI..."\
pip3 install -r requirements.txt || exit 1\
\
# Step 8: Place the downloaded Code Llama model in the UI's model directory\
echo "Setting up the interactive UI with the Code Llama model..."\
mkdir -p models\
mv ../llama.cpp/models/CodeLlama-13B.ggmlv3.q4_0.bin models/\
\
# Step 9: Run the interactive UI with the specified model\
echo "Starting the interactive web UI for Code Llama 13B..."\
python3 server.py --model CodeLlama-13B.ggmlv3.q4_0.bin}