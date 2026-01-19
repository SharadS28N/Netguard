'use client'

import { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import gsap from 'gsap'
import ScrollTrigger from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export default function Manifesto() {
  const containerRef = useRef(null)

  useEffect(() => {
    const ctx = gsap.context(() => {
      const lines = gsap.utils.toArray('.manifesto-line')

      lines.forEach((line: any) => {
        gsap.from(line, {
          scrollTrigger: {
            trigger: line,
            start: 'top 80%',
            end: 'top 50%',
            scrub: 1,
            markers: false,
          },
          opacity: 0,
          x: -30,
          duration: 1,
        })
      })
    }, containerRef)

    return () => ctx.revert()
  }, [])

  return (
    <section ref={containerRef} id="manifesto" className="relative py-32 px-6">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <h2 className="text-4xl md:text-6xl font-light tracking-tight mb-16 text-center">
            Our Manifesto
          </h2>

          <div className="space-y-8 text-lg font-light leading-relaxed text-muted-foreground">
            <p className="manifesto-line text-xl md:text-2xl">
              In a world where wireless networks are everywhere, the threat is invisible.
              Evil Twin attacks masquerade as legitimate networks, intercepting your data,
              stealing credentials, and compromising security.
            </p>

            <p className="manifesto-line text-xl md:text-2xl">
              This is not tomorrow&apos;s problem. It&apos;s happening now.
            </p>

            <p className="manifesto-line text-accent text-xl md:text-2xl font-light">
              NetGuard Nepal exists to ensure that you see the threat before it sees you.
            </p>

            <p className="manifesto-line text-lg">
              Our multi-layered detection system uses advanced machine learning, network
              analysis, and behavioral intelligence to identify and neutralize evil twin
              networks in real-time. We don&apos;t just warn you—we protect you.
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
