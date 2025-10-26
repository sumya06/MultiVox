---

### 🔹 Role of MERN Stack (MongoDB, Express, React, Node)

The MERN stack handles the **web platform** for MultiVox.

* **React.js**:
  Frontend user interface for uploading audio/video, viewing subtitles, playback control, and project dashboards.

* **Node.js + Express.js**:
  Backend APIs for handling file uploads, user authentication, and communication with the Python services.

* **MongoDB**:
  Database for storing user profiles, movie metadata, subtitles, dubbing projects, and processed audio records.

The MERN side focuses on **user experience, data management, and multimedia workflow control**.

---

### 🔹 Role of Python

Python is used for **AI-based dubbing and media processing**.

Typical functionalities include:

* **Speech-to-Text**: Extract dialogue from the original movie
* **Text-to-Speech**: Generate dubbed audio in a new language
* **Voice Cloning**: Preserve actor tone or create custom AI voices
* **Lip-sync automation**: Sync generated audio with character lip movements
* **Audio cleanup**: Noise filtering, pitch adjustment, timing correction
* Libraries: PyTorch, TensorFlow, Whisper, OpenCV, ffmpeg, etc.

Python focuses on **intelligent audio-visual transformation**.

---

### ✅ Combined Workflow Example

1. User uploads movie through React UI.
2. Node.js server transfers video or audio to Python processing.
3. Python performs dubbing, voice synthesis, and lip-sync.
4. Results are saved into MongoDB through Node.
5. Processed dubbed movie becomes available in the browser interface.

---
