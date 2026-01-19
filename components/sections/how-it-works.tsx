'use client'

import { useState } from 'react'
import { motion, AnimatePresence, easeOut } from 'framer-motion'

const containerVariants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.15,
    },
  },
}

const itemVariants = {
  hidden: {
    opacity: 0,
    y: 40,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.6,
      ease: easeOut,
    },
  },
}

export default function HowItWorks() {
  const [activeStep, setActiveStep] = useState<number | null>(null)

  const steps = [
    {
      number: '01',
      title: 'Network Scanning',
      description:
        'NetGuard continuously scans for nearby WiFi networks, collecting signal characteristics and metadata.',
      details: ['Passive RF monitoring', 'SSID and BSSID analysis', 'Signal strength mapping'],
    },
    {
      number: '02',
      title: 'Pattern Recognition',
      description:
        'Our AI analyzes network patterns to identify anomalies that indicate evil twin activity.',
      details: ['Behavioral comparison', 'Temporal analysis', 'Spoofing detection'],
    },
    {
      number: '03',
      title: 'Threat Assessment',
      description:
        'Multi-layer decision engine evaluates threat level and determines appropriate response.',
      details: ['Risk scoring', 'Context evaluation', 'Confidence metrics'],
    },
    {
      number: '04',
      title: 'Active Defense',
      description:
        'Once identified, the network is neutralized through active countermeasures and user notification.',
      details: ['User alerts', 'Network blocking', 'Incident logging'],
    },
  ]

  return (
    <section id="how" className="relative py-32 px-6 border-t border-border">
      <div className="max-w-6xl mx-auto">
        {/* Heading */}
        <motion.h2
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: easeOut }}
          viewport={{ once: true }}
          className="text-4xl md:text-6xl font-light tracking-tight mb-4 text-center"
        >
          How It Works
        </motion.h2>

        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.1, ease: easeOut }}
          viewport={{ once: true }}
          className="text-center text-lg font-light text-muted-foreground mb-20 max-w-2xl mx-auto"
        >
          A seamless four-step process that continuously protects you from evil twin attacks.
        </motion.p>

        {/* Desktop View */}
        <div className="hidden lg:block">
          <div className="relative mb-16">
            <div className="absolute top-8 left-0 right-0 h-0.5 bg-gradient-to-r from-accent via-card to-accent" />

            <motion.div
              variants={containerVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: '-100px' }}
              className="grid grid-cols-4 gap-4"
            >
              {steps.map((step, index) => (
                <motion.div
                  key={step.number}
                  variants={itemVariants}
                  onMouseEnter={() => setActiveStep(index)}
                  onMouseLeave={() => setActiveStep(null)}
                  className="cursor-pointer"
                >
                  <div className="relative">
                    {/* Indicator */}
                    <div className="mb-6 flex justify-center">
                      <motion.div
                        whileHover={{ scale: 1.15 }}
                        className="w-16 h-16 flex items-center justify-center border-2 border-accent rounded-full bg-background transition-colors"
                      >
                        <span className="text-xl font-light">{step.number}</span>
                      </motion.div>
                    </div>

                    {/* Content */}
                    <div className="p-6 border border-muted hover:border-accent transition-colors">
                      <h3 className="text-lg font-light mb-3">{step.title}</h3>
                      <p className="text-sm text-muted-foreground mb-4">
                        {step.description}
                      </p>

                      <AnimatePresence>
                        {activeStep === index && (
                          <motion.ul
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            transition={{ duration: 0.3, ease: easeOut }}
                            className="space-y-1 text-xs text-accent overflow-hidden"
                          >
                            {step.details.map((detail) => (
                              <li key={detail}>• {detail}</li>
                            ))}
                          </motion.ul>
                        )}
                      </AnimatePresence>
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </div>

        {/* Mobile View */}
        <div className="lg:hidden space-y-4">
          {steps.map((step, index) => (
            <motion.button
              key={step.number}
              onClick={() => setActiveStep(activeStep === index ? null : index)}
              className="w-full text-left"
              whileTap={{ scale: 0.98 }}
            >
              <div className="p-6 border border-muted hover:border-accent transition-colors">
                <div className="flex items-start gap-4 mb-4">
                  <span className="text-2xl font-light text-accent">
                    {step.number}
                  </span>
                  <h3 className="text-lg font-light">{step.title}</h3>
                </div>

                <AnimatePresence>
                  {activeStep === index && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      transition={{ duration: 0.3, ease: easeOut }}
                      className="overflow-hidden"
                    >
                      <p className="text-sm text-muted-foreground mb-4">
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
    </section>
  )
}
