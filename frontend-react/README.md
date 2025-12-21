# PDF Buddy - React Frontend

Modern Material-UI frontend for the Question Paper Search system.

## Features

✨ **Dashboard**
- Overview statistics (total questions, documents, MCQs, descriptive)
- Quick stats cards with Material Design

📚 **Question Library**
- Full data table with all questions
- Sortable and filterable columns
- Detailed question view with metadata
- MCQ options display
- Source document tracking

🔍 **Search**
- Semantic search with natural language queries
- Rich result cards with similarity scores
- Metadata tags (Part, Unit, Question #, Marks)
- MCQ options in results

📤 **Upload**
- Drag & drop file upload
- Multi-file support
- Real-time job status monitoring
- Progress bar with percentage

## Tech Stack

- **React 18** + **TypeScript**
- **Material-UI (MUI)** - Google's Material Design
- **MUI X Data Grid** - Advanced data table
- **React Router** - Client-side routing
- **TanStack Query** - Data fetching and caching
- **Axios** - HTTP client
- **Vite** - Build tool
- **Bun** - Package manager

## Quick Start

### 1. Install Dependencies

```bash
cd frontend-react
bun install
```

### 2. Start Development Server

```bash
bun run dev
```

The app will be available at `http://localhost:5173`

### 3. Ensure Backend is Running

```bash
# Terminal 1: Backend API
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Celery Worker
cd backend
uv run celery -A app.tasks.celery_app worker --loglevel=info
```

## Project Structure

```
frontend-react/
├── src/
│   ├── api/
│   │   └── client.ts          # API client and types
│   ├── components/
│   │   └── Layout.tsx          # Main layout with navigation
│   ├── pages/
│   │   ├── Dashboard.tsx       # Dashboard with stats
│   │   ├── QuestionLibrary.tsx # Question data table
│   │   ├── Upload.tsx          # File upload page
│   │   └── Search.tsx          # Semantic search page
│   ├── App.tsx                 # Main app with routing
│   └── main.tsx                # Entry point
├── package.json
└── vite.config.ts
```

## API Endpoints Used

- `GET /health` - Health check
- `POST /api/v1/upload` - Upload PDFs
- `GET /api/v1/jobs/{id}` - Job status
- `GET /api/v1/search` - Semantic search
- `GET /api/v1/questions` - Get all questions
- `GET /api/v1/documents` - Get all documents

## Configuration

API URL is configured in `src/api/client.ts`:
```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

To change the API URL, set the `VITE_API_URL` environment variable.

## Build for Production

```bash
bun run build
```

The production build will be in the `dist/` directory.

## Development

### Adding New Pages

1. Create page component in `src/pages/`
2. Add route in `src/App.tsx`
3. Add menu item in `src/components/Layout.tsx`

### Adding New API Calls

1. Add TypeScript types in `src/api/client.ts`
2. Add API function in `src/api/client.ts`
3. Use with TanStack Query in components

## Material-UI Customization

Theme is configured in `src/App.tsx`:
```typescript
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});
```

## License

MIT
