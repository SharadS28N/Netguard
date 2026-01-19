// import { NextRequest, NextResponse } from 'next/server'

// const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || 'http://localhost:5000'
// const PYTHON_SCAN_INTERFACE =
//   process.env.PYTHON_SCAN_INTERFACE || process.env.SCAN_INTERFACE || 'Wi-Fi'

// export async function POST(request: NextRequest) {
//   try {
//     const body = await request.json().catch(() => ({}))
//     const scan_type = body.scan_type || 'passive'
//     const duration = typeof body.duration === 'number' ? body.duration : 30
//     const interfaceName = body.interface || PYTHON_SCAN_INTERFACE

//     const response = await fetch(`${PYTHON_BACKEND_URL}/api/scan/start`, {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'application/json'
//       },
//       body: JSON.stringify({
//         interface: interfaceName,
//         scan_type,
//         duration
//       })
//     })

//     const data = await response.json().catch(() => null)

//     if (!response.ok) {
//       return NextResponse.json(
//         {
//           error: data?.error || 'Failed to start scan'
//         },
//         { status: response.status }
//       )
//     }

//     return NextResponse.json(data, { status: 200 })
//   } catch (error) {
//     return NextResponse.json(
//       { error: 'Scan start failed', details: String(error) },
//       { status: 500 }
//     )
//   }
// }




import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:5000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    console.log('[API] Forwarding scan request to backend...');
    
    // Forward to Python backend
    const response = await fetch(`${BACKEND_URL}/api/scan/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.message || 'Backend error' },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    
    console.log('[API] Scan started:', data.scan_id);
    
    return NextResponse.json(data);
    
  } catch (error: any) {
    console.error('[API] Error:', error);
    
    return NextResponse.json(
      { 
        error: 'Failed to connect to backend',
        details: error.message,
        backend_url: BACKEND_URL
      },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const scanId = searchParams.get('scanId');
    
    const response = await fetch(
      `${BACKEND_URL}/api/scan/status/${scanId}`,
      { method: 'GET' }
    );
    
    const data = await response.json();
    return NextResponse.json(data);
    
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}