# Quick Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/misrac-analyzer)

## 🚀 One-Click Deployment

1. Click the "Deploy with Vercel" button above
2. Connect your GitHub account
3. Configure environment variables:
   - `REACT_APP_BACKEND_URL` - Your backend API URL
4. Click "Deploy"

## 📦 Manual Deployment

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Login
```bash
vercel login
```

### Step 3: Deploy
```bash
# From project root
vercel

# For production
vercel --prod
```

## 🔧 Local Development

### Frontend
```bash
cd frontend
npm install --legacy-peer-deps
npm start
```

The app will open at `http://localhost:3000`

### Backend (Optional - for full functionality)
```bash
cd backend
pip install -r requirements.txt
python server.py
```

The API will run at `http://localhost:8001`

## 📝 Environment Variables

Create `frontend/.env`:
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

For production, update this to your deployed backend URL.

## 🌐 Live Demo

Once deployed, your app will be available at:
- `https://your-project.vercel.app`

## 📚 Full Documentation

See [DEPLOYMENT.md](./DEPLOYMENT.md) for comprehensive deployment instructions.

---

**Note**: This deploys only the frontend. You'll need to deploy the backend separately (see DEPLOYMENT.md for options).
