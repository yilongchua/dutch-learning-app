# YL Unified Application Frontend

A modern, fast, and feature-rich unified frontend interface built with **React Router v7** and styled with a sleek glassmorphic design and **TailwindCSS** compatible conventions.

## 🚀 Features & Modules

This frontend successfully integrates the backend decoupled micro-apps into a single user interface:

- **The News**: Auto-generated news reading feeds.
- **Dutch B1**: An interactive portal for writing, speaking, and listening exercises.
- **Scheduler (Tasks)**: A dynamic form to manage, deploy, and delete `APScheduler` background cron jobs dynamically.
- **Media Gallery**: An infinite-scroll gallery to view all generated images and `.mp4` videos with native CSS transitions.
- **Graphics Generator**: An endpoint UI to generate isolated text-to-image/video prompts dynamically.

## 📁 Project Structure

```text
frontend/
├── app/
│   ├── components/
│   │   ├── layout/        # Defines the overarching Navbar
│   │   ├── dutch/         # UI sections isolated for Dutch logic
│   │   └── thenews/       # UI sections isolated for TheNews logic
│   ├── routes/            # Core React Router pages mapped to endpoints
│   ├── services/          # Axios API layers abstracting logic
│   ├── root.tsx           # Base Root component
│   └── routes.ts          # Central React Router mappings
├── public/                # Static assets
└── package.json
```

## 🛠 Getting Started

### Installation

Install the dependencies:

```bash
npm install
```

### Development

Start the development server with HMR:

```bash
npm run dev
```

Your application will be available at `http://localhost:5173`. Make sure the Python Fast API server is already running to consume data.

### Styling System
This platform explicitly uses native DOM configurations mixed with a heavy emphasis on dynamic glassmorphism. See `index.css` for the complete token layout.

---
Built seamlessly to orchestrate multiple backend micro-apps gracefully.
