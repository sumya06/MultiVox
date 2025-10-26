🎬 MultiVox | AI-Powered Movie Dubbing Platform

MultiVox is an intelligent movie dubbing platform that combines the MERN stack and Python-based AI to create high-quality dubbed content. Users can upload videos, generate AI voices in different languages, and achieve automatic lip-syncing through advanced speech processing.

🔹 MERN Stack Responsibilities

The MERN stack manages the web application and user interaction layer.

React.js
Provides an intuitive UI for uploading media, managing subtitles, playback control, and project dashboards.

Node.js + Express.js
Manages file uploads, user authentication, and server-side communication with Python AI services.

MongoDB
Stores user accounts, movie metadata, subtitles, dubbing history, and generated audio files.

Focus areas: User experience, media workflow control, secure data handling

🔹 Python Responsibilities

Python powers AI-driven audio-visual transformation.

Key capabilities include:

Speech-to-Text for extracting original dialogues
Text-to-Speech for generating dubbed audio in selected languages
Voice cloning for actor-like voice output
Lip-sync automation to align mouth movements with dubbed audio
Audio enhancement: noise reduction, pitch correction, timing fixes
Technologies: PyTorch, TensorFlow, Whisper, OpenCV, ffmpeg
Focus area: AI voice synthesis and automated dubbing

✅ Workflow Overview

User uploads movie via React UI
Node.js backend sends audio/video to Python engine
Python generates dubbed audio and lip-syncs with video
Results are saved in MongoDB
User previews and downloads processed video in browser

💡 Objective

To deliver a seamless, AI-assisted dubbing experience that reduces manual effort and increases dubbing quality for filmmakers, content creators, and studios.
