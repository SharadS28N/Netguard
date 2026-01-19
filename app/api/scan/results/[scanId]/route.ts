import { NextRequest, NextResponse } from 'next/server'

const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || 'http://localhost:5000'

export async function GET(
  request: NextRequest,
  context: { params: { scanId: string } }
) {
  const scanId = context.params.scanId

  if (!scanId) {
    return NextResponse.json({ error: 'scanId is required' }, { status: 400 })
  }

  try {
    const response = await fetch(`${PYTHON_BACKEND_URL}/api/scan/results/${scanId}`)
    const data = await response.json().catch(() => null)

    if (!response.ok) {
      return NextResponse.json(
        { error: data?.error || 'Failed to get scan results' },
        { status: response.status }
      )
    }

    return NextResponse.json(data, { status: 200 })
  } catch (error) {
    return NextResponse.json(
      { error: 'Scan results failed', details: String(error) },
      { status: 500 }
    )
  }
}

