# Deployment Configuration for Render

# Backend: render.yaml
services:
  - type: web
    name: road-its-backend
    env: python
    plan: free
    buildCommand: "pip install -r backend/requirements.txt"
    startCommand: "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: "3.10"

# Frontend: Deploy separately to Vercel
# 1. Connect GitHub repo to Vercel
# 2. Set root directory to "frontend/"
# 3. Add environment variable:
#    NEXT_PUBLIC_API_URL = https://your-backend-app.onrender.com
# 4. Deploy

---

## Deployment Steps

### Backend on Render

1. Push code to GitHub
2. Sign in to Render (render.com)
3. Create new "Web Service"
4. Connect GitHub repository
5. Select branch (main)
6. Configure:
   - Environment: Python 3
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
7. Create Web Service
8. Wait for deployment (copy backend URL)

### Frontend on Vercel

1. Sign in to Vercel (vercel.com)
2. Import GitHub project
3. Set "Root Directory" to `frontend`
4. Add Environment Variable:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://your-render-backend-url.onrender.com`
5. Deploy

---

## Alternative Deployments

### Railway (railway.app)
- Create new project, connect GitHub
- Deploy both as services
- Automatically detect Python and Node environments
- Configure environment variables in dashboard

### AWS / GCP / Azure
- Use containers (Dockerfile provided)
- Deploy with Docker + container orchestration
- Set `NEXT_PUBLIC_API_URL` in frontend environment

### Heroku (legacy)
- Deploy backend with Procfile
- Deploy frontend to Vercel or Heroku

---

## Environment Variables

Set these in your hosting platform's dashboard:

**Backend:**
```
PORT=8000
PYTHONUNBUFFERED=1
```

**Frontend:**
```
NEXT_PUBLIC_API_URL=https://your-backend-url
```

---

## Monitoring & Debugging

### Render Backend Logs
- Dashboard → Web Service → Logs

### Vercel Frontend Logs
- Dashboard → Deployments → Logs

### Health Checks
- Backend: `GET https://your-backend/docs` (Swagger UI)
- Frontend: Check deployment status in Vercel dashboard

---

## Cost Estimates

- **Render (Backend)**: Free tier available (limited resources)
- **Vercel (Frontend)**: Free tier with generous limits
- **Total**: Can run free with some limitations

For production, consider paid tiers for better performance/uptime.
