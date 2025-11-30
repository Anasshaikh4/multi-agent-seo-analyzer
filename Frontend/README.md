# SEO Analyzer Frontend

A modern, animated React frontend for the AI-powered SEO Analyzer built with Google ADK multi-agent system.

![React](https://img.shields.io/badge/React-18.3-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?logo=typescript)
![Vite](https://img.shields.io/badge/Vite-5.4-646CFF?logo=vite)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-06B6D4?logo=tailwindcss)

## ✨ Features

- **Modern UI/UX** - Sleek dark theme with glassmorphism effects
- **Real-time Progress** - Live agent status updates during analysis
- **Smooth Animations** - Powered by Framer Motion
- **PDF Export** - Download comprehensive SEO reports
- **Responsive Design** - Works on all screen sizes

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend server running on port 8000

### Installation

```bash
# Navigate to frontend directory
cd Frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

## 🏗️ Project Structure

```
Frontend/
├── src/
│   ├── components/
│   │   ├── WelcomeScreen.tsx    # Landing page with animations
│   │   ├── FormScreen.tsx       # URL input form
│   │   ├── AnalyzingScreen.tsx  # Agent progress display
│   │   ├── ResultsScreen.tsx    # PDF download screen
│   │   └── ParticleBackground.tsx
│   ├── api.ts                   # API client functions
│   ├── types.ts                 # TypeScript interfaces
│   ├── App.tsx                  # Main application
│   ├── main.tsx                 # Entry point
│   └── index.css                # Global styles
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## 🔌 API Integration

The frontend connects to the backend API:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/analyze` | POST | Start SEO analysis |
| `/api/analysis/{id}/progress` | GET | Get analysis progress |
| `/api/analysis/{id}` | GET | Get analysis results |
| `/api/analysis/{id}/pdf` | GET | Download PDF report |

## 🎨 Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool & dev server
- **TailwindCSS** - Utility-first CSS
- **Framer Motion** - Animations
- **Axios** - HTTP client
- **Lucide React** - Icons

## 🖥️ Screens

1. **Welcome Screen** - Animated landing with floating particles
2. **Form Screen** - URL input with validation
3. **Analyzing Screen** - Real-time 6-agent progress tracker
4. **Results Screen** - PDF download and completion status

## 🤖 AI Agents Tracked

The analyzing screen displays real-time status for:

| Agent | Purpose |
|-------|---------|
| Security | Website security analysis |
| On-Page | On-page SEO factors |
| Content | Content quality assessment |
| Performance | Page speed & Core Web Vitals |
| Indexability | Search engine accessibility |
| Report | Final report generation |

## 📝 License

MIT License

## 🔗 Related

- [Backend Documentation](../Project/README.md)
- [Google ADK](https://google.github.io/adk-docs/)
