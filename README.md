# 🖼️ Smart Gallery

An AI-powered photo gallery application with automatic face recognition, object detection, and semantic search capabilities. Built with Next.js, FastAPI, and state-of-the-art machine learning models.

![Smart Gallery Banner](https://img.shields.io/badge/AI-Powered-orange?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=for-the-badge&logo=fastapi)

## ✨ Features

### 🤖 AI-Powered Analysis
- **Face Detection & Recognition** - Automatically detect faces using InsightFace and group them by person
- **Object Detection** - Identify objects in photos using YOLOv8 with custom-trained models
- **Semantic Search** - Search photos using natural language with CLIP embeddings
- **Smart Clustering** - Automatically group faces into people clusters

### 📸 Gallery Management
- **Beautiful UI** - Modern, responsive interface built with Next.js and Tailwind CSS
- **Photo Viewer** - Full-screen viewer with zoom, navigation, and metadata display
- **Bulk Upload** - Drag-and-drop multiple photos at once
- **Categories** - Browse photos by detected objects
- **People** - View all photos of a specific person with one click
- **Rename People** - Assign names to detected face clusters

### 🔍 Smart Features
- **EXIF Data Extraction** - Automatically extract and display photo metadata
- **Thumbnail Generation** - Fast loading with optimized thumbnails
- **Real-time Processing** - Photos are analyzed immediately after upload

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance async API framework |
| **SQLAlchemy** | Async ORM with SQLite |
| **YOLOv8** | Object detection |
| **InsightFace** | Face detection & recognition |
| **OpenCLIP** | Semantic image embeddings |
| **FAISS** | Vector similarity search |
| **Pillow/OpenCV** | Image processing |

### Frontend
| Technology | Purpose |
|------------|---------|
| **Next.js 14** | React framework with App Router |
| **TypeScript** | Type-safe development |
| **Tailwind CSS** | Utility-first styling |
| **Zustand** | Lightweight state management |
| **Framer Motion** | Smooth animations |
| **Lucide React** | Beautiful icons |

## 📋 Prerequisites

- **Python 3.10+** (3.11 recommended)
- **Node.js 18+**
- **CUDA** (optional, for GPU acceleration)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/smart-gallery.git
cd smart-gallery
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python run.py
```

The backend will start at `http://localhost:8000`

> **Note:** On first run, the ML models will be downloaded automatically (~2GB). This may take a few minutes.

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will start at `http://localhost:3000`

## 📁 Project Structure

```
smart-gallery/
├── backend/
│   ├── app/
│   │   ├── api/              # API route handlers
│   │   │   ├── photos.py     # Photo upload, delete, retrieve
│   │   │   ├── clusters.py   # Face cluster management
│   │   │   ├── categories.py # Object categories
│   │   │   └── search.py     # Semantic search
│   │   ├── core/             # Configuration & database
│   │   ├── models/           # SQLAlchemy models & Pydantic schemas
│   │   ├── services/         # Business logic
│   │   │   ├── ml_service.py        # ML model management
│   │   │   ├── photo_service.py     # Photo processing
│   │   │   ├── clustering_service.py # Face clustering
│   │   │   ├── vector_service.py    # FAISS index management
│   │   │   └── search_service.py    # Search functionality
│   │   └── utils/            # Utilities (image processing)
│   ├── data/                 # SQLite DB, photos, thumbnails, embeddings
│   ├── requirements.txt
│   └── run.py
│
├── frontend/
│   ├── app/                  # Next.js App Router
│   ├── components/           # React components
│   │   ├── PhotoGrid.tsx     # Main photo grid
│   │   ├── PhotoViewer.tsx   # Full-screen viewer
│   │   ├── PeopleGrid.tsx    # Face clusters view
│   │   ├── CategoriesGrid.tsx # Object categories
│   │   ├── UploadModal.tsx   # Photo upload
│   │   └── ...
│   ├── lib/                  # Utilities, API client, store
│   ├── types/                # TypeScript types
│   └── package.json
│
└── README.md
```

## 🔧 Configuration

### Backend Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Server
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/gallery.db

# ML Models
YOLO_MODEL_PATH=./app/services/best.pt  # Custom YOLO model (optional)
FACE_SIM_THRESHOLD=0.5                   # Face clustering threshold

# Storage
PHOTOS_DIR=./data/photos
THUMBNAILS_DIR=./data/thumbnails
EMBEDDINGS_DIR=./data/embeddings

# Image Processing
MAX_IMAGE_SIZE=4096
THUMBNAIL_SIZE=300
JPEG_QUALITY=85
```

### Frontend Environment Variables

Create a `.env.local` file in the `frontend` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📖 API Documentation

Once the backend is running, access the interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/photos` | List all photos |
| `POST` | `/photos/upload` | Upload a photo |
| `DELETE` | `/photos/{id}` | Delete a photo |
| `GET` | `/photos/{id}/image` | Get full image |
| `GET` | `/photos/{id}/thumbnail` | Get thumbnail |
| `GET` | `/clusters` | List face clusters (people) |
| `PATCH` | `/clusters/{id}` | Update cluster name |
| `GET` | `/categories` | List object categories |
| `GET` | `/search?q={query}` | Semantic search |
| `GET` | `/stats` | Gallery statistics |

## 🎯 Usage

### Uploading Photos
1. Click the **Upload** button in the header
2. Drag and drop photos or click to browse
3. Wait for AI processing to complete
4. Photos will appear in the gallery with detected faces and objects

### Viewing People
1. Click **People** in the sidebar
2. View all detected face clusters
3. Click the ✏️ pencil icon to rename a person
4. Click on a person to see all their photos

### Searching Photos
1. Use the search bar in the header
2. Type natural language queries like:
   - "beach sunset"
   - "people smiling"
   - "food on a table"
3. Results are ranked by semantic similarity

### Browsing Categories
1. Click **Categories** in the sidebar
2. View all detected object types
3. Click a category to see all photos containing that object

## 🔬 ML Models Used

| Model | Purpose | Size |
|-------|---------|------|
| **YOLOv8m** | Object detection | ~50MB |
| **InsightFace buffalo_l** | Face detection & recognition | ~300MB |
| **OpenCLIP ViT-L-14** | Semantic embeddings | ~900MB |

## ⚡ Performance Tips

### GPU Acceleration
For faster processing, install CUDA-enabled PyTorch:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install onnxruntime-gpu
```

### Memory Optimization
- The backend loads all ML models at startup (~4GB RAM)
- For lower memory usage, consider using smaller models:
  - YOLOv8n instead of YOLOv8m
  - InsightFace buffalo_s instead of buffalo_l
  - OpenCLIP ViT-B-32 instead of ViT-L-14

## 🐛 Troubleshooting

### Common Issues

**CORS Errors**
- Ensure the backend is running on `http://localhost:8000`
- Check that CORS middleware is properly configured

**Model Download Failures**
- Ensure stable internet connection
- Models are cached in `~/.insightface` and `~/.cache`

**SQLite Errors**
- The app uses SQLite-compatible functions
- If upgrading from PostgreSQL, check for `array_agg` → `group_concat`

**Memory Errors**
- Reduce `MAX_IMAGE_SIZE` in settings
- Use smaller ML models
- Process fewer photos at once

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ultralytics](https://github.com/ultralytics/ultralytics) for YOLOv8
- [InsightFace](https://github.com/deepinsight/insightface) for face recognition
- [OpenCLIP](https://github.com/mlfoundations/open_clip) for CLIP implementation
- [FAISS](https://github.com/facebookresearch/faiss) for vector search

---

<p align="center">
  Made with ❤️ and AI
</p>
