'use client'

import { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import gsap from 'gsap'
import ScrollTrigger from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export default function EvilTwinThreat() {
  const containerRef = useRef(null)
  const contentRef = useRef(null)

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Parallax effect
      gsap.to(contentRef.current, {
        scrollTrigger: {
          trigger: containerRef.current,
          start: 'top center',
          end: 'bottom center',
          scrub: 1,
          markers: false,
        },
        y: 50,
        opacity: 1,
        duration: 1,
      })
    }, containerRef)

    return () => ctx.revert()
  }, [])

  const threats = [
    {
      title: 'Data Interception',
      description: 'Attackers intercept unencrypted traffic, capturing passwords and sensitive information.',
      impact: 'Critical',
    },
    {
      title: 'Man-in-the-Middle',
      description: 'Positioned between user and legitimate network, intercepting and modifying communications.',
      impact: 'Critical',
    },
    {
      title: 'Credential Theft',
      description: 'Fake networks harvest login credentials from unsuspecting users.',
      impact: 'High',
    },
    {
      title: 'Malware Distribution',
      description: 'Compromised networks deliver malicious payloads to connected devices.',
      impact: 'Critical',
    },
  ]

  return (
    <section
      ref={containerRef}
      id="threat"
      className="relative py-32 px-6 border-t border-border"
    >
      <div className="max-w-6xl mx-auto">
        <motion.h2
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-4xl md:text-6xl font-light tracking-tight mb-20 text-center"
        >
          The Evil Twin Threat
        </motion.h2>

        <div ref={contentRef} className="grid md:grid-cols-2 gap-8 lg:gap-12">
          {threats.map((threat, index) => (
            <motion.div
              key={threat.title}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="group p-6 border border-muted hover:border-accent transition-colors duration-300"
            >
              <div className="flex items-start gap-4 mb-4">
                <div className="w-1 h-12 bg-accent mt-2 group-hover:h-16 transition-all duration-300" />
                <div>
                  <h3 className="text-xl font-light tracking-wide mb-2">{threat.title}</h3>
                  <span
                    className={`inline-block text-xs font-light tracking-widest px-2 py-1 border ${
                      threat.impact === 'Critical'
                        ? 'border-accent text-accent'
                        : 'border-muted text-muted-foreground'
                    }`}
                  >
                    {threat.impact}
                  </span>
                </div>
              </div>
              <p className="text-muted-foreground font-light leading-relaxed">
                {threat.description}
              </p>
            </motion.div>
          ))}
        </div>

        {/* Statistics */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          viewport={{ once: true }}
          className="mt-20 pt-20 border-t border-border grid grid-cols-2 md:grid-cols-4 gap-8 text-center"
        >
          {[
            { number: '2.5B', label: 'WiFi Users at Risk' },
            { number: '87%', label: 'Unaware of Evil Twins' },
            { number: '60%', label: 'Public WiFi Networks Vulnerable' },
            { number: '$4.45M', label: 'Avg. Data Breach Cost' },
          ].map((stat) => (
            <div key={stat.label}>
              <p className="text-3xl md:text-4xl font-light text-accent mb-2">
                {stat.number}
              </p>
              <p className="text-xs md:text-sm font-light tracking-widest text-muted-foreground">
                {stat.label}
              </p>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
