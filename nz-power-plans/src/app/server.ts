// server.ts
type Express = any

type Request = any
type Response = any

type Middleware = (req: Request, res: Response, next: Function) => void

type ErrorHandler = (err: any, req: Request, res: Response, next: Function) => void

const express: any = require('express')
const helmet: any = require('helmet')
const rateLimit: any = require('express-rate-limit')

const app: Express = express()

// Middleware
app.use(helmet())
app.use(express.json())

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests'
})
app.use(limiter as Middleware)

// CORS
const cors: any = require('cors')
const corsOptions: any = {
  origin: process.env.CORS_ORIGINS?.split(',') || ['*'],
  credentials: true,
}
app.use(cors(corsOptions) as any)

// Routes
app.get('/api/health', (req: Request, res: Response) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() })
})

// API route handlers will be added here

const PORT = process.env.PORT || 3001

app.listen(PORT, () => {
  console.log(`API server running on port ${PORT}`)
  console.log(`CORS origins: ${process.env.CORS_ORIGINS || '*'}`)
  console.log(`HA URL: ${process.env.HA_URL || 'NOT_CONFIGURED'}`)
})