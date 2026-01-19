# NetGuard Nepal - Quick Start Guide

Get up and running with the Evil Twin Detection Platform in 5 minutes.

## 1. Install & Run (2 minutes)

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The application runs at **http://localhost:3000**

## 2. Explore the Home Page (1 minute)

- Notice the dark theme (toggle moon icon in top-right)
- Scroll down to see smooth animations
- Read the manifesto and detection methodology
- Click "Get Started" button

## 3. Test the Dashboard (2 minutes)

1. Click **"Get Started"** button or navigate to `/dashboard`
2. Select **"Network Scan"** tab
3. Choose scan type: **Active** or **Passive**
4. Click **"Start Scan"**
5. Wait ~2 seconds for results
6. View threat analysis with confidence scores

## 4. Try Other Dashboard Features

### Detection Results Tab
- View detailed threat information
- See multi-layer analysis scores
- Check recommendations for each network

### Detection Logs Tab
- Filter by threat level (danger/suspicious/safe)
- View complete scan history
- Check timestamps and details

### Statistics Tab
- See aggregated metrics
- View detection method breakdown
- Review AI/ML layer architecture

## 5. Theme Toggle

Click the **moon/sun icon** in the top-right to switch between dark and light modes. Your preference is saved automatically.

---

## Key Screens

### Home Page
- Hero with "Detect, Defend, Secure" messaging
- Manifesto section
- Evil Twin threat explanation
- Detection methodology
- How-it-works visualization
- Call-to-action to dashboard

### Dashboard
- **Scan Interface**: Configure and start network scans
- **Results**: Real-time threat analysis with confidence scores
- **Logs**: Browse complete detection history
- **Stats**: View detection metrics and AI/ML breakdown

---

## API Testing (Optional)

### Test Detection Endpoint

```bash
curl -X POST http://localhost:3000/api/detect \
  -H "Content-Type: application/json" \
  -d '{
    "networks": [{
      "ssid": "Free WiFi",
      "bssid": "AA:BB:CC:DD:EE:FF",
      "signal_strength": -45,
      "channel": 6,
      "encryption": "Open",
      "beacon_interval": 100,
      "supported_rates": [1, 2, 5.5, 11],
      "wps_enabled": true,
      "last_seen": 1704067200000
    }]
  }'
```

### Test Logs Endpoint

```bash
# Get recent logs
curl http://localhost:3000/api/logs?limit=10

# Get danger threats
curl http://localhost:3000/api/logs?threat_level=danger
```

### Test ML Model

```bash
curl -X POST http://localhost:3000/api/model \
  -H "Content-Type: application/json" \
  -d '{
    "features": [0.3, 0.25, 0.15, 0.2],
    "model_type": "ensemble"
  }'
```

---

## Production Deploy (5 minutes)

### Deploy to Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Login and deploy
vercel

# For production
vercel --prod
```

Visit your domain in browser!

### Alternative: Deploy to Netlify

1. Push code to GitHub
2. Connect GitHub repo to Netlify
3. Netlify auto-deploys on push

---

## Common Commands

```bash
# Start development
npm run dev

# Build production
npm run build

# Start production
npm start

# Lint code
npm run lint
```

---

## File & Folder Guide

### Key Files to Know

| Path | Purpose |
|---|---|
| `/app/page.tsx` | Home page |
| `/app/dashboard/page.tsx` | Detection dashboard |
| `/app/api/detect/route.ts` | Detection endpoint |
| `/app/api/logs/route.ts` | Logs API |
| `/app/globals.css` | Theme and styles |

### Component Organization

| Folder | Content |
|---|---|
| `/components/sections` | Page sections |
| `/components/dashboard` | Dashboard components |
| `/components/ui` | Reusable UI elements |
| `/components/animations` | GSAP animations |

---

## Theme Customization

Edit `/app/globals.css` to change colors:

```css
:root {
  --background: #0a0a0a;      /* Main background */
  --foreground: #ffffff;       /* Text color */
  --primary: #dc2626;          /* Accent color */
  --muted: #333333;            /* Subtle backgrounds */
  --border: #333333;           /* Border color */
}

:root:not(.dark) {
  --background: #ffffff;       /* Light mode bg */
  --foreground: #0a0a0a;       /* Light mode text */
  /* ... other light mode colors ... */
}
```

---

## Troubleshooting

### Port 3000 in use?
```bash
PORT=3001 npm run dev
```

### Animations not smooth?
- Close browser extensions
- Check browser DevTools Performance tab
- Try different browser

### Theme not persisting?
- Clear browser cache (Ctrl+Shift+Delete)
- Check localStorage enabled
- Check browser privacy settings

---

## What's Next?

### Learn More
- Read [SETUP.md](./SETUP.md) for detailed setup
- Check [API.md](./API.md) for API details
- Review [DEPLOYMENT.md](./DEPLOYMENT.md) for production

### Extend the App
- Integrate real WiFi scanning library
- Add MongoDB database
- Implement user authentication
- Build admin dashboard
- Add webhook notifications

### Customize
- Change colors in globals.css
- Modify animations in components
- Add new pages
- Integrate with your services

---

## Key URLs

| URL | Purpose |
|---|---|
| http://localhost:3000 | Home page |
| http://localhost:3000/dashboard | Detection dashboard |
| http://localhost:3000/api/detect | Detection API |
| http://localhost:3000/api/logs | Logs API |
| http://localhost:3000/api/model | ML model API |

---

## Performance Tips

1. **Use the dashboard** - Optimized for real-time detection
2. **Browser DevTools** - Check performance (F12 → Performance)
3. **API response** - Typically <50ms
4. **Detection** - Takes ~2 seconds for demo data
5. **Animations** - Smooth 60fps on modern browsers

---

## Security Notes

- No authentication in development mode
- Add API keys for production
- Use HTTPS in production
- Enable CORS restrictions
- Implement rate limiting

---

## Support

Got stuck? Check these:

1. **Installation issues** → [SETUP.md](./SETUP.md#troubleshooting)
2. **API questions** → [API.md](./API.md)
3. **Deployment help** → [DEPLOYMENT.md](./DEPLOYMENT.md)
4. **General info** → [README.md](./README.md)

---

## Quick Checklist

- [ ] Run `npm install`
- [ ] Run `npm run dev`
- [ ] Visit http://localhost:3000
- [ ] Try dashboard scan
- [ ] Toggle theme
- [ ] Check detection results
- [ ] Test APIs with curl

---

**Happy detecting!**

For production deployment, head to [DEPLOYMENT.md](./DEPLOYMENT.md)
