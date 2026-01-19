'use client'

import { motion, Variants } from 'framer-motion'

export default function DetectionTechnology() {
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

  /**
   * Uses cubic-bezier easing to satisfy TypeScript
   */
  const layerVariants: Variants = {
    hidden: (i: number) => ({
      opacity: 0,
      y: 20 + i * 6,
    }),
    visible: (i: number) => ({
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
        delay: i * 0.1,
        ease: [0.16, 1, 0.3, 1],
      },
    }),
  }

  return (
    <section
      id="technology"
      className="relative py-32 px-6 border-t border-border"
    >
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{
            duration: 0.8,
            ease: [0.16, 1, 0.3, 1],
          }}
          className="mb-20"
        >
          <h2 className="text-4xl md:text-6xl font-light tracking-tight mb-6">
            Detection Technology
          </h2>
          <p className="text-lg font-light text-muted-foreground max-w-2xl">
            Four-layer AI-powered detection system that identifies evil twin
            networks through signal analysis, network behavior, machine
            learning, and threat intelligence.
          </p>
        </motion.div>

        {/* Detection Stack */}
        <div className="space-y-4 mb-20">
          {detectionLayers.map((layer, index) => (
            <motion.div
              key={layer.name}
              custom={index}
              variants={layerVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: '-80px' }}
              className="group relative"
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
                    whileHover={{ scale: 1.5 }}
                    transition={{ duration: 0.2 }}
                    className="w-2 h-2 bg-accent rounded-full"
                  />
                </div>
              </div>

              {/* Connector */}
              {index < detectionLayers.length - 1 && (
                <motion.div
                  aria-hidden
                  animate={{ opacity: [0.3, 1, 0.3] }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: 'linear',
                  }}
                  className="absolute -bottom-4 left-8 w-0.5 h-4 bg-gradient-to-b from-accent to-transparent"
                />
              )}
            </motion.div>
          ))}
        </div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{
            duration: 0.8,
            ease: [0.16, 1, 0.3, 1],
          }}
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
              <p className="text-4xl font-light text-accent mb-2">
                {stat.value}
              </p>
              <p className="text-sm font-light tracking-wide mb-1">
                {stat.label}
              </p>
              <p className="text-xs text-muted-foreground">{stat.desc}</p>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
