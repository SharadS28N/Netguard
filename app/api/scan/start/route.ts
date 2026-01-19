import { NextRequest, NextResponse } from 'next/server'

const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || 'http://localhost:5000'
const PYTHON_SCAN_INTERFACE =
  process.env.PYTHON_SCAN_INTERFACE || process.env.SCAN_INTERFACE || 'Wi-Fi'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({}))
    const scan_type = body.scan_type || 'passive'
    const duration = typeof body.duration === 'number' ? body.duration : 30
    const interfaceName = body.interface || PYTHON_SCAN_INTERFACE

    const response = await fetch(`${PYTHON_BACKEND_URL}/api/scan/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        interface: interfaceName,
        scan_type,
        duration
      })
    })

    const data = await response.json().catch(() => null)

    if (!response.ok) {
      return NextResponse.json(
        {
          error: data?.error || 'Failed to start scan'
        },
        { status: response.status }
      )
    }

    return NextResponse.json(data, { status: 200 })
  } catch (error) {
    return NextResponse.json(
      { error: 'Scan start failed', details: String(error) },
      { status: 500 }
    )
  }
}

