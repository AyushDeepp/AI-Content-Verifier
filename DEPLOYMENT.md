# Deployment Guide

## Frontend Deployment on Netlify

### Prerequisites
- GitHub repository with your code
- Netlify account

### Steps

1. **Push your code to GitHub** (if not already done)
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Connect to Netlify**
   - Go to [Netlify](https://www.netlify.com/)
   - Click "Add new site" → "Import an existing project"
   - Connect your GitHub account and select your repository

3. **Configure Build Settings**
   - Netlify will auto-detect the settings from `netlify.toml`
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/build`

4. **Set Environment Variables**
   In Netlify dashboard → Site settings → Environment variables, add:
   ```
   REACT_APP_API_BASE_URL=https://your-backend-api-url.com
   ```
   Replace `your-backend-api-url.com` with your actual backend API URL.

5. **Deploy**
   - Click "Deploy site"
   - Netlify will build and deploy your frontend

## Backend Deployment

Your backend (FastAPI) needs to be deployed separately. Recommended platforms:

### Option 1: Railway
1. Go to [Railway](https://railway.app/)
2. Create a new project from GitHub
3. Add environment variables:
   - `MONGO_URI`
   - `JWT_SECRET`
   - `HUGGINGFACE_API_KEY`
   - `CORS_ORIGINS` (comma-separated list, e.g., `http://localhost:3000,https://your-netlify-site.netlify.app`)

### Option 2: Render
1. Go to [Render](https://render.com/)
2. Create a new Web Service
3. Connect your GitHub repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables (same as Railway)

### Option 3: Heroku
1. Install Heroku CLI
2. Create `Procfile` in backend directory:
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
3. Deploy using Heroku CLI

## Important Notes

1. **CORS Configuration**: After deploying your backend, update the `CORS_ORIGINS` environment variable to include your Netlify frontend URL (e.g., `https://your-app.netlify.app`)

2. **Environment Variables**: Never commit `.env` files. Use platform-specific environment variable settings.

3. **API URL**: Update `REACT_APP_API_BASE_URL` in Netlify with your deployed backend URL.

4. **Database**: Ensure your MongoDB connection string is accessible from your backend hosting platform.

## Post-Deployment Checklist

- [ ] Frontend deployed on Netlify
- [ ] Backend deployed on chosen platform
- [ ] Environment variables set in both platforms
- [ ] CORS configured to allow Netlify domain
- [ ] API URL updated in Netlify environment variables
- [ ] Test authentication flow
- [ ] Test content detection features
- [ ] Verify all API endpoints are working

