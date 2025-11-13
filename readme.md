# ✋ Hand Volume Controller 🔊  
### Control system volume using hand gestures — touchless & seamless!

![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A smart and fun Computer Vision project that allows you to control your system's volume **without touching the keyboard or mouse**
Show your hand to the webcam and control audio with intuitive gestures.

## 🖼️ Screenshots
    > ![Demo](assets/image.png)


## Features

- Real-time hand tracking (MediaPipe)
- Single-hand control: thumb + index finger distance
- Dual-hand mode: left thumb ↔ right index
- Smooth interpolation-based volume control
- Live UI overlay (volume bar & fingertip connection)
- Logging for debugging and performance

## 🧰 Tech Stack

| Technology | Purpose |
|------------|---------|
| Python     | Core language |
| MediaPipe  | Hand landmark detection |
| OpenCV     | Camera processing & UI overlays |
| PyCaw      | Windows system volume control |
| NumPy      | Distance calculations & interpolation |

## 📂 Project Structure

hand-volume-controller/
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
└── src/
├── volume_controller.py
├── hand_detector.py
├── audio/
│ └── volume_manager.py
├── ui/
│ └── overlay.py
└── utils/
└── logger.py
├── assests/
│ └── image.png


## ⚙️ Installation

### 1. Clone
git clone https://github.com/YOUR_USERNAME/hand-volume-controller.git
cd hand-volume-controller

### 2. Create Environment
python -m venv venv
# Windows
venv\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Run application
python main.py


## ✋ Gesture Controls

| Gesture | Action |
|--------:|--------|
| Thumb + Index (same hand) | Smooth volume control (either hand) |
| Left Thumb + Right Index   | Dual-hand volume control |
| Fingers move apart         | Increase volume 🔊 |
| Fingers move close         | Decrease volume 🔉 |
| No gesture                 | Volume remains stable |


## 🔍 How It Works

1. MediaPipe detects hands and returns 21 landmarks per hand.  
2. We track thumb tip (#4) and index tip (#8).  
3. Compute Euclidean distance between active fingertips.  
4. Map distance to volume percentage using `np.interp`.  
5. Apply volume with PyCaw and show UI overlay in real-time.

## 👨‍💻 Author

**Shubham Shinde**  
AI • ML • Computer Vision Enthusiast  
shinde.ashubham@gmail.com

## ⭐ Show your support

If you like the project, please star the repo — it helps a lot!
