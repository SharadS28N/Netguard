'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'

export default function CTA() {
  return (
    <section className="relative py-32 px-6 border-t border-border">
      <div className="max-w-4xl mx-auto text-center">
        <motion.h2
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-4xl md:text-6xl font-light tracking-tight mb-6"
        >
          Ready to Secure Your Network?
        </motion.h2>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.1 }}
          viewport={{ once: true }}
          className="text-lg font-light text-muted-foreground mb-12 leading-relaxed"
        >
          Start your free trial today. NetGuard Nepal detects evil twin networks
          automatically, protecting your organization from day one. No credit card required.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          viewport={{ once: true }}
          className="flex flex-col sm:flex-row gap-4 justify-center items-center"
        >
          <Link href="/dashboard">
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-8 py-3 border border-accent text-accent hover:bg-accent hover:text-background font-light tracking-wide transition-colors cursor-pointer"
            >
              Start Free Trial
            </motion.div>
          </Link>
          <motion.a
            href="mailto:demo@netguard.np"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-8 py-3 border border-muted text-muted-foreground hover:border-foreground hover:text-foreground font-light tracking-wide transition-colors"
          >
            Schedule Demo
          </motion.a>
        </motion.div>

        {/* Trust Indicators */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          viewport={{ once: true }}
          className="mt-16 pt-12 border-t border-border"
        >
          <p className="text-sm font-light tracking-widest text-muted-foreground mb-6">
            TRUSTED BY ORGANIZATIONS WORLDWIDE
          </p>
          <div className="flex flex-wrap justify-center gap-8">
            {['ENTERPRISE', 'GOVERNMENT', 'EDUCATION', 'FINANCE'].map((label) => (
              <div
                key={label}
                className="h-12 border border-muted flex items-center px-4 rounded"
              >
                <span className="text-xs font-light tracking-wider text-muted-foreground">
                  {label}
                </span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  )
}
