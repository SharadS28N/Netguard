import { NextRequest, NextResponse } from 'next/server'

const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || 'http://localhost:5000'

type BackendPrediction = {
  bssid?: string
  ssid?: string
  threat_level?: string
  confidence_score?: number
  model_scores?: {
    random_forest?: number
    gradient_boosting?: number
    ensemble?: number
  }
  is_threat?: boolean
}

type BackendResponse = {
  predictions: BackendPrediction[]
  summary?: {
    total_networks?: number
    threats_detected?: number
    critical?: number
    high?: number
    medium?: number
    low?: number
  }
  timestamp?: string
}

type UiNetworkThreat = 'danger' | 'suspicious' | 'safe'

type UiNetwork = {
  bssid: string
  ssid: string
  threat_level: UiNetworkThreat
  confidence: number
  details: {
    signature_score: number
    behavior_score: number
    traffic_score: number
    ensemble_decision: string
  }
  recommendations: string[]
}

type UiDetectionResult = {
  scan_id: string
  timestamp: number
  overall_threat: UiNetworkThreat
  networks: UiNetwork[]
}

const WHITELISTED_SSIDS = new Set<string>(['Home_Router', 'Corporate_Network'])
const WHITELISTED_BSSIDS = new Set<string>(['11:22:33:44:55:03', 'DD:EE:FF:AA:BB:02'])

function isWhitelisted(network: any) {
  const ssid = String(network.ssid || '')
  const bssid = String(network.bssid || '')
  return WHITELISTED_SSIDS.has(ssid) || WHITELISTED_BSSIDS.has(bssid)
}

function mapThreatLevel(
  backendLevel: string | undefined,
  ensembleScore: number,
  isThreat: boolean,
  whitelisted: boolean
): UiNetworkThreat {
  if (whitelisted) return 'safe'
  if (backendLevel === 'critical') return 'danger'
  if (backendLevel === 'high') return 'danger'
  if (backendLevel === 'medium') return 'suspicious'

  if (ensembleScore >= 0.7) return 'danger'
  if (ensembleScore >= 0.4) return 'suspicious'

  if (isThreat) return 'suspicious'
  return 'safe'
}

function buildRecommendations(threat: UiNetworkThreat, whitelisted: boolean): string[] {
  if (whitelisted) {
    return ['Known trusted network (whitelisted). Safe to use.']
  }

  if (threat === 'danger') {
    return [
      'High risk of evil twin detected. Disconnect from this network immediately.',
      'Avoid entering any sensitive information on this network.',
      'Prefer using a trusted VPN or a known secure WiFi instead.'
    ]
  }

  if (threat === 'suspicious') {
    return [
      'Suspicious signals detected that may indicate an emerging evil twin.',
      'Avoid using this network for banking or other critical tasks.',
      'Monitor for duplicate SSIDs or sudden signal changes.'
    ]
  }

  return ['No strong signs of evil twin detected. Continue to monitor periodically.']
}

function computeOverallThreat(networks: UiNetwork[]): UiNetworkThreat {
  if (networks.some((n) => n.threat_level === 'danger')) return 'danger'
  if (networks.some((n) => n.threat_level === 'suspicious')) return 'suspicious'
  return 'safe'
}

function buildUiResultFromBackend(networks: any[], backend: BackendResponse): UiDetectionResult {
  const backendPredictions = backend.predictions || []

  const uiNetworks: UiNetwork[] = networks.map((network, index) => {
    const prediction = backendPredictions[index] || {}
    const whitelisted = isWhitelisted(network)
    const ensembleScore =
      typeof prediction.model_scores?.ensemble === 'number'
        ? prediction.model_scores.ensemble
        : typeof prediction.confidence_score === 'number'
        ? prediction.confidence_score
        : 0

    const threatLevel = mapThreatLevel(
      prediction.threat_level,
      ensembleScore,
      Boolean(prediction.is_threat),
      whitelisted
    )

    const signatureScore =
      typeof prediction.model_scores?.random_forest === 'number'
        ? prediction.model_scores.random_forest
        : ensembleScore

    const behaviorScore =
      typeof prediction.model_scores?.gradient_boosting === 'number'
        ? prediction.model_scores.gradient_boosting
        : ensembleScore

    const trafficScore = ensembleScore

    const ensembleDecision =
      threatLevel === 'danger'
        ? 'Ensemble models agree on high evil twin risk.'
        : threatLevel === 'suspicious'
        ? 'Models detect early warning signs. Continue monitoring.'
        : 'Models consider this network low risk.'

    return {
      bssid: String(network.bssid || prediction.bssid || ''),
      ssid: String(network.ssid || prediction.ssid || ''),
      threat_level: threatLevel,
      confidence: ensembleScore,
      details: {
        signature_score: signatureScore,
        behavior_score: behaviorScore,
        traffic_score: trafficScore,
        ensemble_decision: ensembleDecision
      },
      recommendations: buildRecommendations(threatLevel, whitelisted)
    }
  })

  const filteredNetworks = uiNetworks.filter((n) => n.ssid || n.bssid)
  const networksForThreat = filteredNetworks.length > 0 ? filteredNetworks : uiNetworks

  const overall_threat = computeOverallThreat(networksForThreat)

  return {
    scan_id: `scan_${Date.now()}`,
    timestamp: Date.now(),
    overall_threat,
    networks: networksForThreat
  }
}

function buildHeuristicDetection(networks: any[]): UiDetectionResult {
  const uiNetworks: UiNetwork[] = networks.map((network) => {
    const whitelisted = isWhitelisted(network)

    const ssid = String(network.ssid || '')
    const encryption = String(network.encryption || 'Open')
    const signal = typeof network.signal_strength === 'number' ? network.signal_strength : -80

    let heuristicScore = 0

    if (encryption === 'Open' || encryption === 'WEP') heuristicScore += 0.4
    if (/free|airport|public|guest/i.test(ssid)) heuristicScore += 0.3
    if (signal > -50) heuristicScore += 0.15

    const threatLevel = mapThreatLevel(
      heuristicScore > 0.7 ? 'high' : heuristicScore > 0.4 ? 'medium' : 'low',
      heuristicScore,
      heuristicScore > 0.4,
      whitelisted
    )

    const signatureScore = Math.min(1, heuristicScore + 0.1)
    const behaviorScore = Math.min(1, heuristicScore + 0.05)
    const trafficScore = Math.min(1, heuristicScore)

    const ensembleDecision =
      threatLevel === 'danger'
        ? 'Rule-based heuristics indicate a highly risky evil twin candidate.'
        : threatLevel === 'suspicious'
        ? 'Heuristics show signs of possible evil twin behaviour.'
        : 'Heuristics do not indicate strong evil twin risk.'

    return {
      bssid: String(network.bssid || ''),
      ssid,
      threat_level: threatLevel,
      confidence: heuristicScore,
      details: {
        signature_score: signatureScore,
        behavior_score: behaviorScore,
        traffic_score: trafficScore,
        ensemble_decision: ensembleDecision
      },
      recommendations: buildRecommendations(threatLevel, whitelisted)
    }
  })

  const filteredNetworks = uiNetworks.filter((n) => n.ssid || n.bssid)
  const networksForThreat = filteredNetworks.length > 0 ? filteredNetworks : uiNetworks

  const overall_threat = computeOverallThreat(networksForThreat)

  return {
    scan_id: `scan_${Date.now()}`,
    timestamp: Date.now(),
    overall_threat,
    networks: networksForThreat
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { networks } = body

    if (!networks || !Array.isArray(networks)) {
      return NextResponse.json(
        { error: 'Invalid networks data' },
        { status: 400 }
      )
    }

    try {
      const response = await fetch(`${PYTHON_BACKEND_URL}/api/detection/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ networks })
      })

      if (response.ok) {
        const backend: BackendResponse = await response.json()
        const uiResult = buildUiResultFromBackend(networks, backend)
        return NextResponse.json(uiResult, { status: 200 })
      }
    } catch (error) {
      console.error('Python backend detection error:', error)
    }

    const fallbackResult = buildHeuristicDetection(networks)
    return NextResponse.json(fallbackResult, { status: 200 })
  } catch (error) {
    console.error('Detection API error:', error)
    return NextResponse.json(
      { error: 'Detection failed', details: String(error) },
      { status: 500 }
    )
  }
}
