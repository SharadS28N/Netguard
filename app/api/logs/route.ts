import { NextRequest, NextResponse } from 'next/server'

// In-memory storage for demo (in production use MongoDB)
let detectionLogs: any[] = []
const MAX_LOGS = 1000

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const limit = parseInt(searchParams.get('limit') || '50')
    const offset = parseInt(searchParams.get('offset') || '0')
    const threat_level = searchParams.get('threat_level')

    let filtered = [...detectionLogs].reverse()

    if (threat_level && threat_level !== 'all') {
      filtered = filtered.filter(
        (log) => log.detection_result?.overall_threat === threat_level
      )
    }

    const paginated = filtered.slice(offset, offset + limit)

    return NextResponse.json(
      {
        logs: paginated,
        total: filtered.length,
        limit,
        offset
      },
      { status: 200 }
    )
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch logs', details: String(error) },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { detection_result, user_action } = body

    const logEntry = {
      id: `log_${Date.now()}`,
      timestamp: Date.now(),
      detection_result,
      user_action,
      created_at: new Date().toISOString()
    }

    detectionLogs.push(logEntry)

    // Keep only recent logs
    if (detectionLogs.length > MAX_LOGS) {
      detectionLogs = detectionLogs.slice(-MAX_LOGS)
    }

    return NextResponse.json(logEntry, { status: 201 })
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to create log', details: String(error) },
      { status: 500 }
    )
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const days = parseInt(searchParams.get('older_than_days') || '30')

    const cutoffTime = Date.now() - days * 24 * 60 * 60 * 1000
    const initialCount = detectionLogs.length
    detectionLogs = detectionLogs.filter((log) => log.timestamp > cutoffTime)

    return NextResponse.json(
      {
        message: `Deleted ${initialCount - detectionLogs.length} old logs`,
        remaining: detectionLogs.length
      },
      { status: 200 }
    )
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to delete logs', details: String(error) },
      { status: 500 }
    )
  }
}
