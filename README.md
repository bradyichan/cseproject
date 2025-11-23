# cse2102-fall25-Team22
**Team Members:**
- Brady Chan (bic22003)
- Samuel C Mason (scm21013)
- Alexander Wolven (ajw22023)

**Project Links:**
- Trello: https://trello.com/invite/b/68cb102bdbbb87fa46b1f1ee/ATTI83b4e0dfbd84da8c474af59e2a0e9236AA1CF706/semester-project-kanban
- Figma: https://www.figma.com/design/gEfqggCcsh3hUdkutAOcEb/Milestone-3-Group-22?node-id=1-4&t=40NAMzzLrXqF0yrV-1

## How to Run the Application

### Prerequisites
- Python 3.8+
- Node.js 20+
- Docker (optional)

### Backend Setup (Flask API)

#### Running Directly
```bash
pip install -r backend/requirements.txt
python3 -m backend.main
```
The backend API will be available at `http://127.0.0.1:6767`

#### Running with Docker
```bash
cd backend
docker build -t team22backend .
docker run -p 6767:6767 team22backend
```

### Frontend Setup (React/Vite)

#### Running Directly
```bash
cd frontend/swap-and-sell-team22
npm install
npm run dev
```
The frontend will be available at `http://127.0.0.1:5173`

#### Running with Docker
```bash
cd frontend/swap-and-sell-team22
docker build -t team22frontend .
docker run -p 5173:5173 team22frontend
```

### Running Both Services Together

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend/swap-and-sell-team22
npm run dev
```

Then open your browser to `http://127.0.0.1:5173`

## Features (Milestone 7)
- **Home Page**: Landing page with navigation to Buy and Sell pages
- **Buy Page**: Browse items fetched from backend API with search functionality
- **Sell Page**: List new items for sale via form submission to backend API
- **Steel Thread**: Complete data flow from frontend → backend API → database
- **Docker Support**: Both frontend and backend can run in containers
- **CI/CD Pipeline**: GitHub Actions for frontend linting and backend testing
