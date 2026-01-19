'use client'

import { motion } from 'framer-motion'

export default function Footer() {
  const currentYear = new Date().getFullYear()

  const footerLinks = {
    Product: ['Features', 'Technology', 'Documentation', 'API'],
    Company: ['About', 'Blog', 'Careers', 'Contact'],
    Resources: ['Research', 'White Papers', 'Case Studies', 'Events'],
    Legal: ['Privacy', 'Terms', 'Security', 'Compliance'],
  }

  return (
    <footer className="relative border-t border-border bg-card/50">
      <div className="max-w-6xl mx-auto px-6 py-20">
        {/* Main Footer Content */}
        <div className="grid md:grid-cols-5 gap-12 mb-16">
          {/* Brand */}
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h3 className="text-xl font-light tracking-widest mb-4">NETGUARD</h3>
            <p className="text-sm font-light text-muted-foreground leading-relaxed">
              Enterprise-grade evil twin detection for the connected world.
            </p>
          </motion.div>

          {/* Links */}
          {Object.entries(footerLinks).map(([category, links], index) => (
            <motion.div
              key={category}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <h4 className="text-sm font-light tracking-widest mb-4">{category}</h4>
              <ul className="space-y-2">
                {links.map((link) => (
                  <li key={link}>
                    <a
                      href="#"
                      className="text-sm font-light text-muted-foreground hover:text-accent transition-colors"
                    >
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>

        {/* Divider */}
        <motion.div
          initial={{ scaleX: 0 }}
          whileInView={{ scaleX: 1 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="h-px bg-border origin-left mb-8"
        />

        {/* Bottom */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="flex flex-col md:flex-row items-center justify-between gap-4"
        >
          <p className="text-sm font-light text-muted-foreground">
            © {currentYear} NetGuard Nepal. All rights reserved.
          </p>

          {/* Social Links */}
          <div className="flex gap-6">
            {['Twitter', 'LinkedIn', 'GitHub'].map((social) => (
              <a
                key={social}
                href="#"
                className="text-sm font-light text-muted-foreground hover:text-accent transition-colors"
              >
                {social}
              </a>
            ))}
          </div>
        </motion.div>
      </div>
    </footer>
  )
}
