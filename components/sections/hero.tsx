'use client'

import { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import gsap from 'gsap'

export default function Hero() {
  const containerRef = useRef(null)

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.from('.hero-word', {
        duration: 1.2,
        opacity: 0,
        y: 30,
        stagger: 0.15,
        ease: 'power2.out',
      })

      gsap.from('.hero-subtitle', {
        duration: 1,
        opacity: 0,
        y: 20,
        delay: 0.4,
        ease: 'power2.out',
      })
    }, containerRef)

    return () => ctx.revert()
  }, [])

  return (
    <section
      ref={containerRef}
      className="relative min-h-screen w-full flex items-center justify-center pt-24 px-6"
    >
      {/* Subtle background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-background via-background to-card opacity-40 pointer-events-none" />

      <div className="relative z-10 max-w-5xl mx-auto text-center">
        <div className="mb-8 overflow-hidden">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8 }}
            className="flex flex-wrap justify-center gap-4 md:gap-6"
          >
            {['Detect', 'Defend', 'Secure'].map((word) => (
              <span key={word} className="hero-word text-5xl md:text-7xl font-light tracking-tight">
                {word}
              </span>
            ))}
          </motion.div>
        </div>

        <div className="mb-12 overflow-hidden">
          <h1 className="hero-word text-6xl md:text-8xl font-light tracking-tight leading-tight">
            Evil Twin Attacks
          </h1>
        </div>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="hero-subtitle max-w-2xl mx-auto text-lg md:text-xl font-light text-muted-foreground mb-12 leading-relaxed"
        >
          NetGuard Nepal detects and neutralizes evil twin WiFi networks in real-time.
          Enterprise-grade security for your connected world.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.8 }}
          className="flex flex-col sm:flex-row gap-4 justify-center items-center"
        >
        <motion.a
          href="/dashboard"
          whileHover={{ scale: 1.05, backgroundColor: '#dc2626' }}
          whileTap={{ scale: 0.95 }}
          className="px-8 py-3 border border-accent text-accent hover:text-background font-light tracking-wide transition-colors inline-block cursor-pointer"
        >
          Start Detection
        </motion.a>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-8 py-3 border border-muted text-muted-foreground hover:border-foreground hover:text-foreground font-light tracking-wide transition-colors"
          >
            Learn More
          </motion.button>
        </motion.div>

        {/* Scroll indicator */}
        <motion.div
          animate={{ y: [0, 8, 0] }}
          transition={{ duration: 2, repeat: Number.POSITIVE_INFINITY }}
          className="relative mt-12"
        >
          <div className="flex flex-col items-center gap-2">
            <p className="text-xs font-light tracking-widest text-muted-foreground">SCROLL</p>
            <div className="w-0.5 h-8 border-l border-muted" />
          </div>
        </motion.div>
      </div>
    </section>
  )
}
