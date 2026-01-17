# 🖼️ Smart Gallery

A production-ready, AI-powered photo gallery built with Next.js 14, featuring face recognition, object detection, and semantic search.

![Smart Gallery](https://via.placeholder.com/800x400/0a0a0b/f97316?text=Smart+Gallery)

## ✨ Features

- **🤖 AI-Powered Analysis**
  - **Face Detection & Recognition** - InsightFace buffalo_l model
  - **Object Detection** - YOLOv8x trained on COCO dataset
  - **Semantic Search** - CLIP embeddings for natural language photo search

- **📸 Gallery Features**
  - Multiple view modes (Grid, Masonry, Timeline)
  - Drag & drop photo uploads
  - Photo lightbox with keyboard navigation
  - Face clustering (group photos by person)
  - Object categorization

- **🎨 Modern UI/UX**
  - Dark theme with orange accents
  - Smooth animations with Framer Motion
  - Responsive design for all devices
  - Accessible components

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Smart Gallery API backend running (see below)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd smart-gallery

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Edit .env.local with your API URL
# NEXT_PUBLIC_API_URL=https://your-ngrok-url.ngrok-free.dev

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Backend Setup

The frontend connects to a FastAPI backend running in Google Colab. The backend provides:

- `/photos/upload` - Upload and process photos
- `/photos` - List all photos
- `/photos/{id}` - Get photo details
- `/photos/{id}/image` - Get full image
- `/photos/{id}/thumbnail` - Get thumbnail
- `/clusters` - Get face clusters (people)
- `/categories` - Get object categories
- `/stats` - Get gallery statistics

## 📁 Project Structure

```
smart-gallery/
├── app/
│   ├── globals.css      # Global styles & Tailwind
│   ├── layout.tsx       # Root layout
│   └── page.tsx         # Main gallery page
├── components/
│   ├── Header.tsx       # Navigation header
│   ├── Sidebar.tsx      # Side navigation
│   ├── PhotoCard.tsx    # Photo thumbnail card
│   ├── PhotoGrid.tsx    # Photo grid layouts
│   ├── PhotoViewer.tsx  # Lightbox viewer
│   ├── UploadModal.tsx  # Upload dialog
│   ├── StatsCards.tsx   # Statistics display
│   ├── PeopleGrid.tsx   # Face clusters grid
│   └── CategoriesGrid.tsx # Object categories
├── lib/
│   ├── api.ts           # API client
│   ├── store.ts         # Zustand state management
│   └── utils.ts         # Utility functions
├── types/
│   └── index.ts         # TypeScript definitions
└── public/              # Static assets
```

## 🛠️ Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Animations**: Framer Motion
- **File Upload**: react-dropzone
- **Notifications**: Sonner
- **Icons**: Lucide React

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |

### Tailwind Theme

The app uses a custom dark theme defined in `tailwind.config.ts`:

```js
colors: {
  gallery: {
    bg: '#0a0a0b',
    surface: '#141416',
    elevated: '#1c1c1f',
    border: '#2a2a2e',
    muted: '#71717a',
    text: '#fafafa',
    accent: '#f97316',
  }
}
```

## 📱 Responsive Breakpoints

- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: 1024px - 1280px
- **Large Desktop**: > 1280px

## 🔧 Development

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

## 🚢 Deployment

### Vercel (Recommended)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)

1. Push your code to GitHub
2. Import project in Vercel
3. Add environment variable `NEXT_PUBLIC_API_URL`
4. Deploy

### Docker

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [InsightFace](https://github.com/deepinsight/insightface) - Face recognition
- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) - Object detection
- [OpenAI CLIP](https://github.com/openai/CLIP) - Image embeddings
- [Vercel](https://vercel.com) - Deployment platform

---

Built with ❤️ by Danish Afridi
