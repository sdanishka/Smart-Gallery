# 🖼️ Smart Gallery Backend

Production-ready FastAPI backend for AI-powered photo gallery with face recognition, object detection, and semantic search.

## ✨ Features

### AI Models
- **YOLO v8x** - State-of-the-art object detection (80+ COCO classes)
- **InsightFace buffalo_l** - Face detection, recognition, age/gender estimation
- **CLIP ViT-L-14** - Vision-language model for semantic search

### Capabilities
- 📸 Photo upload with automatic AI analysis
- 🔍 Semantic search using natural language
- 🖼️ Image similarity search
- 👥 Automatic face clustering (group photos by person)
- 🏷️ Object categorization and filtering
- 📊 Gallery statistics

## 🚀 Quick Start

### Option 1: Google Colab (Recommended)

1. Open `Smart_Gallery_Backend.ipynb` in Google Colab
2. Run all cells
3. Get your public ngrok URL

### Option 2: Local Installation

```bash
# Clone repository
git clone <repo-url>
cd smart-gallery-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run server
python run.py
```

## 📁 Project Structure

```
smart-gallery-backend/
├── app/
│   ├── api/                 # API routes
│   │   ├── photos.py        # Photo CRUD operations
│   │   ├── clusters.py      # Face clustering (people)
│   │   ├── search.py        # Semantic & face search
│   │   └── categories.py    # Object categories
│   ├── core/
│   │   ├── config.py        # Configuration
│   │   └── database.py      # Database connection
│   ├── models/
│   │   ├── database.py      # SQLAlchemy models
│   │   └── schemas.py       # Pydantic schemas
│   ├── services/
│   │   ├── ml_service.py    # YOLO, InsightFace, CLIP
│   │   ├── photo_service.py # Photo processing
│   │   ├── search_service.py # Search operations
│   │   ├── vector_service.py # FAISS vector index
│   │   └── clustering_service.py # Face clustering
│   ├── utils/
│   │   └── image.py         # Image processing
│   └── main.py              # FastAPI application
├── data/                    # Storage (auto-created)
│   ├── photos/              # Full-size images
│   ├── thumbnails/          # Thumbnails
│   └── embeddings/          # FAISS indices
├── requirements.txt
├── run.py
└── Smart_Gallery_Backend.ipynb
```

## 🔌 API Endpoints

### Photos
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/photos/upload` | Upload photos for processing |
| GET | `/photos` | List all photos |
| GET | `/photos/{id}` | Get photo details |
| GET | `/photos/{id}/image` | Get full image |
| GET | `/photos/{id}/thumbnail` | Get thumbnail |
| GET | `/photos/{id}/similar` | Find similar photos |
| DELETE | `/photos/{id}` | Delete photo |

### Search
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/search/text?q=` | Semantic search by text |
| POST | `/search/image` | Search by similar image |
| GET | `/search/face/{face_id}` | Find photos by face |
| GET | `/search/person/{cluster_id}` | Photos of a person |
| GET | `/search/object/{class}` | Photos with object type |

### People (Clusters)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/clusters` | List all people |
| GET | `/clusters/{id}` | Get person details |
| PATCH | `/clusters/{id}` | Name a person |
| GET | `/clusters/{id}/photos` | Photos of person |
| POST | `/clusters/{id}/merge/{other}` | Merge two people |

### Categories & Stats
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/categories` | List object categories |
| GET | `/categories/stats` | Gallery statistics |
| GET | `/stats` | Gallery statistics |
| GET | `/health` | Health check |

## ⚙️ Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `false` | Enable debug mode |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `DEVICE` | `cuda` | ML device (cuda/cpu) |
| `DATA_DIR` | `./data` | Data storage path |
| `YOLO_MODEL_PATH` | - | Custom YOLO model path |
| `YOLO_CONFIDENCE` | `0.25` | Detection confidence |
| `FACE_SIM_THRESH` | `0.6` | Face similarity threshold |

## 🔧 Using Custom Models

To use your own trained YOLO model:

```bash
export YOLO_MODEL_PATH=/path/to/your/best.pt
python run.py
```

Or in Colab:
```python
os.environ['YOLO_MODEL_PATH'] = '/content/drive/MyDrive/models/best.pt'
```

## 📝 Example Usage

### Upload Photos

```python
import requests

url = "https://your-ngrok-url.ngrok-free.dev"

with open("photo.jpg", "rb") as f:
    response = requests.post(
        f"{url}/photos/upload",
        files={"files": f}
    )
    
result = response.json()
print(f"Detected {len(result['photos'][0]['detections'])} objects")
print(f"Found {len(result['photos'][0]['faces'])} faces")
```

### Semantic Search

```python
# Search by description
response = requests.get(
    f"{url}/search/text",
    params={"q": "sunset on beach"}
)

for result in response.json()['results']:
    print(f"{result['photo']['original_filename']}: {result['similarity']:.2%}")
```

### Find Person's Photos

```python
# Get all clusters (people)
clusters = requests.get(f"{url}/clusters").json()

# Get photos of first person
person_id = clusters[0]['id']
photos = requests.get(f"{url}/clusters/{person_id}/photos").json()
```

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.109
- **Database**: SQLite + SQLAlchemy 2.0 (async)
- **Vector Search**: FAISS
- **ML**: PyTorch, Ultralytics, InsightFace, OpenCLIP
- **Image Processing**: OpenCV, Pillow

## 📄 License

MIT License

## 🙏 Acknowledgments

- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics)
- [InsightFace](https://github.com/deepinsight/insightface)
- [OpenCLIP](https://github.com/mlfoundations/open_clip)
- [FAISS](https://github.com/facebookresearch/faiss)

---
Built with ❤️ for the Smart Gallery project
