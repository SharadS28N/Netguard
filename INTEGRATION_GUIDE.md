# NetGuard Nepal - Integration Guide

## Pre-Hackathon Checklist

### Environment Setup
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run production build locally
npm start
```

## Database Integration (When Ready)

### MongoDB Setup
When you're ready to connect to a real database:

1. **Update `/app/api/logs/route.ts`**:
```typescript
import { MongoClient } from 'mongodb'

const client = new MongoClient(process.env.MONGODB_URI)
const db = client.db('netguard')
const logsCollection = db.collection('detection_logs')

// Replace in-memory array with MongoDB operations
export async function GET(request: NextRequest) {
  const logs = await logsCollection
    .find({})
    .sort({ timestamp: -1 })
    .limit(parseInt(searchParams.get('limit') || '50'))
    .toArray()
  // ... rest of implementation
}
```

2. **Update environment variables**:
```env
MONGODB_URI=your_mongodb_connection_string
```

## Real ML Model Integration

### Python Backend Setup
When integrating with real ML models:

1. **Create Python server** for model inference
2. **Update `/app/api/model/route.ts`**:
```typescript
export async function POST(request: NextRequest) {
  const { features, model_type } = await request.json()
  
  // Call Python backend
  const response = await fetch(process.env.ML_MODEL_SERVER_URL, {
    method: 'POST',
    body: JSON.stringify({ features, model_type })
  })
  
  const result = await response.json()
  return NextResponse.json(result)
}
```

## WiFi Scanning Library Integration

### Replace Mock Network Data
Currently, `/components/dashboard/scan-interface.tsx` uses mock data. To use real WiFi scanning:

1. **Install WiFi scanning library**:
```bash
npm install node-wifi
# or
npm install wifiscanner
```

2. **Update scan logic**:
```typescript
import wifi from 'node-wifi'

const handleStartScan = async () => {
  try {
    const networks = await wifi.scan()
    // Send real networks to detection API
    const response = await fetch('/api/detect', {
      method: 'POST',
      body: JSON.stringify({ networks })
    })
  } catch (error) {
    console.error('Scan error:', error)
  }
}
```

## Authentication Integration (Optional)

### Supabase Setup
If you need user authentication:

1. **Install Supabase**:
```bash
npm install @supabase/supabase-js
```

2. **Create auth context**:
```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
)
```

3. **Add login page**:
- Create `/app/login/page.tsx`
- Implement sign-in with Supabase Auth
- Add middleware to protect `/dashboard`

## API Rate Limiting

### When Ready for Production
Add rate limiting to `/app/api/middleware.ts`:

```typescript
import { Ratelimit } from '@upstash/ratelimit'
import { Redis } from '@upstash/redis'

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(100, '1 h'),
})

export async function POST(request: NextRequest) {
  const { success } = await ratelimit.limit(request.ip)
  if (!success) return new Response('Rate limited', { status: 429 })
  // ... rest of handler
}
```

## Analytics Integration

### Vercel Analytics (Already Added)
The app includes `@vercel/analytics`. Data will auto-collect on deployment.

### Custom Events
Track important actions:
```typescript
import { trackEvent } from '@vercel/analytics'

const handleScanComplete = (results) => {
  trackEvent('scan_completed', {
    threat_level: results.overall_threat,
    networks_found: results.networks.length
  })
}
```

## Error Tracking (Sentry)

When ready for production monitoring:

```bash
npm install @sentry/nextjs
```

Initialize in `/app/layout.tsx`:
```typescript
import * as Sentry from "@sentry/nextjs"

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
})
```

## Deployment Checklist

### Before Going Live:
- [ ] Environment variables set in Vercel dashboard
- [ ] Database connected (if using MongoDB)
- [ ] ML model server running (if using custom model)
- [ ] CORS configured for external APIs
- [ ] SSL certificate valid
- [ ] Analytics key set
- [ ] Error tracking configured
- [ ] Rate limiting implemented
- [ ] API documentation reviewed

### Vercel Deployment:
```bash
# Push to GitHub
git push origin main

# Deploy automatically or manually
vercel --prod

# Check deployment
vercel --prod --open
```

### AWS Deployment Alternative:
```bash
# Build
npm run build

# Deploy to EC2/ECS with:
- Docker containerization
- PM2 for process management
- Nginx reverse proxy
- SSL with Let's Encrypt
```

## Post-Deployment Monitoring

### Health Checks
Set up monitoring for:
- `/api/detect` - detection API
- `/api/logs` - logging API
- `/api/model` - ML inference

### Performance Metrics
Monitor:
- API response times
- Error rates
- User session duration
- Theme preference distribution
- Popular network patterns

## Feature Flags (For Future Development)

Add feature flags to `/lib/features.ts`:
```typescript
export const features = {
  realTimeScanning: process.env.NEXT_PUBLIC_REAL_TIME_SCAN === 'true',
  advancedAnalytics: process.env.NEXT_PUBLIC_ADVANCED_ANALYTICS === 'true',
  userAuthentication: process.env.NEXT_PUBLIC_AUTH_ENABLED === 'true',
}

// Use in components:
{features.realTimeScanning && <RealTimeScanner />}
```

## Scaling Considerations

### As Traffic Increases:

1. **Database**: Use connection pooling (PgBouncer for PostgreSQL)
2. **API**: Implement caching with Redis
3. **Frontend**: Enable CDN caching for static assets
4. **ML Model**: Use load balancer for multiple model servers
5. **Logs**: Archive old logs to cold storage

## Development Tips

### Debugging
```typescript
// Enable debug logging
const DEBUG = process.env.DEBUG === 'true'

if (DEBUG) console.log(' ...message')
```

### Testing
```bash
# Unit tests
npm test

# Integration tests
npm run test:integration

# E2E tests
npm run test:e2e
```

### Performance Profiling
```bash
# Analyze bundle size
npm run analyze

# Check performance
npm run lighthouse
```

## Support & Troubleshooting

### Common Issues:

**ThemeProvider Error**
- Make sure `ThemeProvider` wraps all children in `layout.tsx`
- Check that `useTheme()` is only called within `ThemeProvider`

**API Call Failures**
- Check browser console for CORS errors
- Verify API route path is correct
- Ensure POST/GET methods match route handler

**Animation Lag**
- Check for heavy computations in render
- Use `will-change` CSS for animated elements
- Profile with Chrome DevTools Performance tab

**Mobile Issues**
- Clear cache and reload
- Check viewport meta tag in layout.tsx
- Test on actual device, not just DevTools simulation

## Next Steps for Hackathon

1. **Week 1**: Integrate real WiFi scanning library
2. **Week 2**: Connect to MongoDB for persistent logs
3. **Week 3**: Deploy ML model inference server
4. **Week 4**: Add user authentication and dashboards
5. **Week 5**: Performance optimization and polish
6. **Week 6**: Final testing and deployment

The current implementation provides a complete foundation. Each integration step will enhance functionality without breaking existing features.
