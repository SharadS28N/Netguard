import { NextRequest, NextResponse } from 'next/server'

interface MLModelInput {
  features: number[]
  model_type?: 'signature' | 'behavior' | 'traffic' | 'ensemble'
}

interface MLModelOutput {
  prediction: string
  confidence: number
  model_used: string
  processing_time_ms: number
}

export async function POST(request: NextRequest) {
  try {
    const startTime = performance.now()
    const body: MLModelInput = await request.json()
    const { features, model_type = 'ensemble' } = body

    if (!features || !Array.isArray(features) || features.length === 0) {
      return NextResponse.json(
        { error: 'Invalid features array' },
        { status: 400 }
      )
    }

    let result: MLModelOutput

    switch (model_type) {
      case 'signature':
        result = runSignatureModel(features)
        break
      case 'behavior':
        result = runBehaviorModel(features)
        break
      case 'traffic':
        result = runTrafficModel(features)
        break
      case 'ensemble':
      default:
        result = runEnsembleModel(features)
    }

    result.processing_time_ms = Math.round(performance.now() - startTime)

    return NextResponse.json(result, { status: 200 })
  } catch (error) {
    return NextResponse.json(
      { error: 'Model inference failed', details: String(error) },
      { status: 500 }
    )
  }
}

function runSignatureModel(features: number[]): Omit<MLModelOutput, 'processing_time_ms'> {
  // Signature-based detection model
  // Features: [beacon_anomaly, encryption_weakness, ssid_similarity, channel_anomaly]
  const weights = [0.3, 0.25, 0.25, 0.2]
  const threshold = 0.5

  const score = features.reduce((sum, f, i) => sum + f * (weights[i] || 0), 0)

  return {
    prediction: score > threshold ? 'evil_twin' : 'legitimate',
    confidence: Math.min(Math.abs(score - threshold) + 0.5, 1),
    model_used: 'Signature Detection Model'
  }
}

function runBehaviorModel(features: number[]): Omit<MLModelOutput, 'processing_time_ms'> {
  // Behavior analysis model
  // Features: [wps_enabled, rate_anomaly, power_anomaly, frequency_deviation]
  const weights = [0.3, 0.25, 0.25, 0.2]
  const threshold = 0.45

  const score = features.reduce((sum, f, i) => sum + f * (weights[i] || 0), 0)

  return {
    prediction: score > threshold ? 'suspicious' : 'safe',
    confidence: Math.abs(score - threshold) + 0.4,
    model_used: 'Behavior Analysis Model'
  }
}

function runTrafficModel(features: number[]): Omit<MLModelOutput, 'processing_time_ms'> {
  // Traffic pattern analysis model
  // Features: [beacon_frequency, association_rate, data_rate, client_count]
  const weights = [0.25, 0.3, 0.25, 0.2]
  const threshold = 0.55

  const score = features.reduce((sum, f, i) => sum + f * (weights[i] || 0), 0)

  return {
    prediction: score > threshold ? 'anomaly_detected' : 'normal',
    confidence: Math.min(Math.abs(score) + 0.3, 1),
    model_used: 'Traffic Pattern Model'
  }
}

function runEnsembleModel(features: number[]): Omit<MLModelOutput, 'processing_time_ms'> {
  // Ensemble meta-model combining all three models
  // Splits features into three groups for each sub-model
  const sigFeatures = features.slice(0, 4)
  const behFeatures = features.slice(4, 8)
  const traFeatures = features.slice(8, 12)

  const sig = runSignatureModel(sigFeatures)
  const beh = runBehaviorModel(behFeatures)
  const tra = runTrafficModel(traFeatures)

  // Weighted voting
  const sigConfidence = sig.prediction === 'evil_twin' ? sig.confidence : 1 - sig.confidence
  const behConfidence = beh.prediction === 'suspicious' ? beh.confidence : 1 - beh.confidence
  const traConfidence = tra.prediction === 'anomaly_detected' ? tra.confidence : 1 - tra.confidence

  const ensembleScore = (sigConfidence * 0.4 + behConfidence * 0.35 + traConfidence * 0.25)

  return {
    prediction: ensembleScore > 0.6 ? 'evil_twin_detected' : 'legitimate_network',
    confidence: Math.min(ensembleScore, 1),
    model_used: 'Ensemble Meta-Model (Signature + Behavior + Traffic)'
  }
}
