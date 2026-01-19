'use client'

import { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import gsap from 'gsap'
import ScrollTrigger from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export default function HowItWorks() {
  const containerRef = useRef(null)
  const [activeStep, setActiveStep] = useState(0)

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.from('.step-item', {
        scrollTrigger: {
          trigger: containerRef.current,
          start: 'top 60%',
          end: 'top 30%',
          scrub: 1,
          markers: false,
        },
        opacity: 0,
        y: 40,
        stagger: 0.15,
      })
    }, containerRef)

    return () => ctx.revert()
  }, [])

  const steps = [
    {
      number: '01',
      title: 'Network Scanning',
      description:
        'NetGuard continuously scans for nearby WiFi networks, collecting signal characteristics and metadata.',
      details: [
        'Passive RF monitoring',
        'SSID and BSSID analysis',
        'Signal strength mapping',
      ],
    },
    {
      number: '02',
      title: 'Pattern Recognition',
      description:
        'Our AI analyzes network patterns to identify anomalies that indicate evil twin activity.',
      details: [
        'Behavioral comparison',
        'Temporal analysis',
        'Spoofing detection',
      ],
    },
    {
      number: '03',
      title: 'Threat Assessment',
      description:
        'Multi-layer decision engine evaluates threat level and determines appropriate response.',
      details: [
        'Risk scoring',
        'Context evaluation',
        'Confidence metrics',
      ],
    },
    {
      number: '04',
      title: 'Active Defense',
      description:
        'Once identified, the network is neutralized through active countermeasures and user notification.',
      details: [
        'User alerts',
        'Network blocking',
        'Incident logging',
      ],
    },
  ]

  return (
    <section
      ref={containerRef}
      id="how"
      className="relative py-32 px-6 border-t border-border"
    >
      <div className="max-w-6xl mx-auto">
        <motion.h2
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-4xl md:text-6xl font-light tracking-tight mb-4 text-center"
        >
          How It Works
        </motion.h2>

        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.1 }}
          viewport={{ once: true }}
          className="text-center text-lg font-light text-muted-foreground mb-20 max-w-2xl mx-auto"
        >
          A seamless four-step process that continuously protects you from evil twin attacks.
        </motion.p>

        {/* Desktop View - Horizontal Timeline */}
        <div className="hidden lg:block">
          <div className="relative mb-16">
            {/* Connection Line */}
            <div className="absolute top-8 left-0 right-0 h-0.5 bg-gradient-to-r from-accent via-card to-accent" />

            {/* Steps */}
            <div className="grid grid-cols-4 gap-4">
              {steps.map((step, index) => (
                <motion.div
                  key={step.number}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  onMouseEnter={() => setActiveStep(index)}
                  className="step-item group cursor-pointer"
                >
                  <div className="relative">
                    {/* Step Indicator */}
                    <div className="mb-6 flex justify-center">
                      <motion.div
                        whileHover={{ scale: 1.2 }}
                        className="relative z-10 w-16 h-16 flex items-center justify-center border-2 border-accent rounded-full bg-background group-hover:bg-accent group-hover:text-background transition-all duration-300"
                      >
                        <span className="text-xl font-light">{step.number}</span>
                      </motion.div>
                    </div>

                    {/* Content */}
                    <div className="p-6 border border-muted group-hover:border-accent transition-colors duration-300">
                      <h3 className="text-lg font-light tracking-wide mb-3">
                        {step.title}
                      </h3>
                      <p className="text-sm font-light text-muted-foreground mb-4">
                        {step.description}
                      </p>

                      {/* Details - Hidden by default */}
                      <motion.ul
                        initial={{ opacity: 0, height: 0 }}
                        animate={
                          activeStep === index
                            ? { opacity: 1, height: 'auto' }
                            : { opacity: 0, height: 0 }
                        }
                        transition={{ duration: 0.3 }}
                        className="space-y-1 text-xs text-accent"
                      >
                        {step.details.map((detail) => (
                          <li key={detail}>• {detail}</li>
                        ))}
                      </motion.ul>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>

        {/* Mobile View - Vertical Carousel */}
        <div className="lg:hidden">
          <div className="space-y-4">
            {steps.map((step, index) => (
              <motion.button
                key={step.number}
                onClick={() => setActiveStep(activeStep === index ? -1 : index)}
                className="step-item w-full text-left"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="p-6 border border-muted hover:border-accent transition-colors duration-300">
                  <div className="flex items-start gap-4 mb-4">
                    <span className="text-2xl font-light text-accent min-w-fit">
                      {step.number}
                    </span>
                    <h3 className="text-lg font-light tracking-wide">{step.title}</h3>
                  </div>

                  <AnimatePresence>
                    {activeStep === index && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        transition={{ duration: 0.3 }}
                      >
                        <p className="text-sm font-light text-muted-foreground mb-4">
                          {step.description}
                        </p>
                        <ul className="space-y-2 text-xs text-accent">
                          {step.details.map((detail) => (
                            <li key={detail}>• {detail}</li>
                          ))}
                        </ul>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </motion.button>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
