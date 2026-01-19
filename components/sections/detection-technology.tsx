'use client'

import { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import gsap from 'gsap'
import ScrollTrigger from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export default function DetectionTechnology() {
  const containerRef = useRef(null)
  const stackRef = useRef(null)

  useEffect(() => {
    const ctx = gsap.context(() => {
      const layers = gsap.utils.toArray('.detection-layer')

      layers.forEach((layer: any, index: number) => {
        gsap.from(layer, {
          scrollTrigger: {
            trigger: containerRef.current,
            start: 'top center',
            end: 'center center',
            scrub: 1,
            markers: false,
          },
          opacity: 0,
          y: 20 + index * 5,
          duration: 0.8,
        })
      })
    }, containerRef)

    return () => ctx.revert()
  }, [])

  const detectionLayers = [
    {
      name: 'Signal Analysis',
      description: 'Real-time RF pattern recognition and anomaly detection',
      icon: '⚡',
    },
    {
      name: 'Network Fingerprinting',
      description: 'Behavioral analysis of network characteristics and topology',
      icon: '🔍',
    },
    {
      name: 'AI Decision Engine',
      description: 'Machine learning model with 99.2% accuracy on trained datasets',
      icon: '🧠',
    },
    {
      name: 'Threat Intelligence',
      description: 'Real-time threat feeds and collective defense mechanisms',
      icon: '🛡️',
    },
  ]

  return (
    <section
      ref={containerRef}
      id="technology"
      className="relative py-32 px-6 border-t border-border"
    >
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="mb-20"
        >
          <h2 className="text-4xl md:text-6xl font-light tracking-tight mb-6">
            Detection Technology
          </h2>
          <p className="text-lg font-light text-muted-foreground max-w-2xl">
            Four-layer AI-powered detection system that identifies evil twin networks
            through signal analysis, network behavior, machine learning, and threat intelligence.
          </p>
        </motion.div>

        {/* Detection Stack */}
        <div ref={stackRef} className="space-y-4 mb-20">
          {detectionLayers.map((layer, index) => (
            <motion.div
              key={layer.name}
              initial={{ opacity: 0, x: -40 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="detection-layer group relative"
            >
              <div className="p-6 border border-muted hover:border-accent transition-all duration-300 hover:bg-card/50 cursor-pointer">
                <div className="flex items-start gap-4">
                  <div className="text-2xl">{layer.icon}</div>
                  <div className="flex-1">
                    <h3 className="text-xl font-light tracking-wide mb-2">
                      Layer {index + 1}: {layer.name}
                    </h3>
                    <p className="text-muted-foreground font-light">
                      {layer.description}
                    </p>
                  </div>
                  <motion.div
                    className="w-2 h-2 bg-accent rounded-full group-hover:scale-150"
                    transition={{ duration: 0.2 }}
                  />
                </div>
              </div>

              {/* Layer connector */}
              {index < detectionLayers.length - 1 && (
                <motion.div
                  animate={{ opacity: [0.3, 1, 0.3] }}
                  transition={{ duration: 2, repeat: Number.POSITIVE_INFINITY }}
                  className="absolute -bottom-4 left-8 w-0.5 h-4 bg-gradient-to-b from-accent to-transparent"
                />
              )}
            </motion.div>
          ))}
        </div>

        {/* Key Stats */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="grid md:grid-cols-3 gap-8 pt-12 border-t border-border"
        >
          {[
            {
              label: 'Detection Accuracy',
              value: '99.2%',
              desc: 'On trained datasets',
            },
            {
              label: 'Response Time',
              value: '<100ms',
              desc: 'Real-time threat neutralization',
            },
            {
              label: 'False Positives',
              value: '<0.1%',
              desc: 'Minimal user impact',
            },
          ].map((stat) => (
            <div key={stat.label} className="text-center">
              <p className="text-4xl font-light text-accent mb-2">{stat.value}</p>
              <p className="text-sm font-light tracking-wide mb-1">{stat.label}</p>
              <p className="text-xs text-muted-foreground">{stat.desc}</p>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
