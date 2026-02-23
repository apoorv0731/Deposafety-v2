# DepoSafety V2 Frontend

React web application for property management with 3D model viewing and evidence reporting.

## Tech Stack

- React 18 + Vite
- Three.js + React Three Fiber (3D viewer)
- Supabase client (Auth + Database)
- Tailwind CSS
- React Query (data fetching)
- Zustand (state management)

## Features

- User authentication (Login/Register)
- Property management dashboard
- Video upload with progress tracking
- Interactive 3D model viewer
- Evidence report viewer with PDF download
- Profile settings
- Mobile-responsive design

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file:
```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

3. Run development server:
```bash
npm run dev
```

4. Build for production:
```bash
npm run build
```

## Project Structure

```
src/
├── components/       # Reusable UI components
├── pages/           # Page components
├── hooks/           # Custom React hooks
├── stores/          # Zustand state stores
├── lib/             # Utility functions and clients
└── App.jsx          # Main app component
```