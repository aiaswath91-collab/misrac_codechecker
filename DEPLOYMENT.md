# Deployment Guide for MISRA C Analyzer

## 🚀 Quick Start - Deploy to Vercel

### Prerequisites
- GitHub account
- Vercel account (free tier works)
- Backend API deployed separately (see Backend Deployment section)

### Frontend Deployment Steps

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/misrac-analyzer.git
   git push -u origin main
   ```

2. **Deploy to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "Add New Project"
   - Import your GitHub repository
   - Vercel will auto-detect the configuration from `vercel.json`
   - Click "Deploy"

3. **Configure Environment Variables**
   After deployment, add these environment variables in Vercel dashboard:
   - `REACT_APP_BACKEND_URL` = Your backend API URL (e.g., `https://your-backend.onrender.com`)

### Alternative: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# For production deployment
vercel --prod
```

## 🔧 Backend Deployment Options

Since Vercel is optimized for frontend/serverless, deploy your FastAPI backend separately:

### Option 1: Render.com (Recommended - Free Tier Available)

1. Create a `render.yaml` in the backend directory:
```yaml
services:
  - type: web
    name: misra-analyzer-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn server:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: MONGO_URL
        value: your-mongodb-connection-string
```

2. Push to GitHub and connect to Render
3. Copy the deployed URL and use it as `REACT_APP_BACKEND_URL`

### Option 2: Railway.app

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Deploy:
```bash
cd backend
railway login
railway init
railway up
```

### Option 3: Heroku

1. Create `Procfile` in backend directory:
```
web: uvicorn server:app --host 0.0.0.0 --port $PORT
```

2. Deploy:
```bash
cd backend
heroku create misra-analyzer-api
git push heroku main
```

### Option 4: DigitalOcean App Platform

1. Create app via DigitalOcean dashboard
2. Connect GitHub repository
3. Configure build and run commands
4. Deploy

## 📝 Environment Variables

### Frontend (.env)
```env
REACT_APP_BACKEND_URL=https://your-backend-url.com
```

### Backend (.env)
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=misra_analyzer
CORS_ORIGINS=https://your-frontend-url.vercel.app
```

## 🔒 Security Considerations

1. **CORS Configuration**: Update `CORS_ORIGINS` in backend to match your Vercel domain
2. **API Keys**: Never commit `.env` files to Git
3. **MongoDB**: Use MongoDB Atlas for production database
4. **Rate Limiting**: Consider adding rate limiting to your API

## 📊 Monitoring

- **Vercel**: Built-in analytics and logs
- **Backend**: Use logging services like:
  - Sentry for error tracking
  - LogRocket for session replay
  - Datadog for APM

## 🧪 Testing Before Deployment

1. **Build locally**:
```bash
cd frontend
npm run build
```

2. **Test production build**:
```bash
npx serve -s build
```

3. **Verify all features work** with production backend URL

## 🔄 Continuous Deployment

Vercel automatically deploys when you push to GitHub:
- `main` branch → Production
- Other branches → Preview deployments

## 📱 Custom Domain (Optional)

1. Go to Vercel project settings
2. Navigate to "Domains"
3. Add your custom domain
4. Update DNS records as instructed

## 🐛 Troubleshooting

### Build Fails
- Check Node.js version compatibility
- Verify all dependencies are in `package.json`
- Check build logs in Vercel dashboard

### API Connection Issues
- Verify `REACT_APP_BACKEND_URL` is set correctly
- Check CORS settings on backend
- Ensure backend is running and accessible

### Environment Variables Not Working
- Prefix all React env vars with `REACT_APP_`
- Redeploy after adding new environment variables
- Clear build cache if needed

## 📚 Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Render Documentation](https://render.com/docs)
- [Railway Documentation](https://docs.railway.app)
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)

---

**Note**: For a complete full-stack deployment on a single platform, consider using:
- **DigitalOcean App Platform** (supports both frontend and backend)
- **AWS Amplify** with Lambda functions
- **Google Cloud Run** (containerized deployment)
