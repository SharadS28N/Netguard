'use client'

import React from 'react'
import { motion } from 'framer-motion'

interface AnimatedCardProps {
  title: string
  description: string
  icon?: React.ReactNode
  index?: number
  onClick?: () => void
  className?: string
  hoverScale?: number
}

export function AnimatedCard({
  title,
  description,
  icon,
  index = 0,
  onClick,
  className = '',
  hoverScale = 1.05,
}: AnimatedCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      whileHover={{ scale: hoverScale }}
      transition={{
        duration: 0.4,
        delay: index * 0.1,
      }}
      viewport={{ once: true }}
      onClick={onClick}
      className={`border border-border rounded-lg p-6 bg-card hover:border-accent transition-colors cursor-pointer ${className}`}
    >
      {icon && (
        <motion.div
          initial={{ scale: 0 }}
          whileInView={{ scale: 1 }}
          transition={{ delay: 0.2 + index * 0.1 }}
          className="mb-4 text-accent text-2xl"
        >
          {icon}
        </motion.div>
      )}

      <h3 className="text-lg font-light tracking-tight mb-2">
        {title}
      </h3>

      <p className="text-sm font-light text-muted-foreground leading-relaxed">
        {description}
      </p>
    </motion.div>
  )
}

interface AnimatedGradientCardProps extends AnimatedCardProps {
  gradient?: string
}

export function AnimatedGradientCard({
  title,
  description,
  icon,
  index = 0,
  onClick,
  className = '',
  gradient = 'from-accent/10 to-transparent',
}: AnimatedGradientCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      whileInView={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.05, y: -5 }}
      transition={{
        duration: 0.4,
        delay: index * 0.1,
      }}
      viewport={{ once: true }}
      onClick={onClick}
      className={`relative border border-accent/20 rounded-lg p-8 bg-gradient-to-br ${gradient} hover:border-accent/50 transition-all cursor-pointer overflow-hidden group ${className}`}
    >
      {/* Animated background blur */}
      <motion.div
        className="absolute inset-0 bg-accent/5 opacity-0 group-hover:opacity-100 transition-opacity"
        animate={{
          background: [
            'radial-gradient(circle at 0% 0%, rgba(220, 38, 38, 0.1) 0%, transparent 50%)',
            'radial-gradient(circle at 100% 100%, rgba(220, 38, 38, 0.1) 0%, transparent 50%)',
          ],
        }}
        transition={{
          duration: 4,
          repeat: Number.POSITIVE_INFINITY,
        }}
      />

      <div className="relative z-10">
        {icon && (
          <motion.div
            initial={{ scale: 0, rotate: -90 }}
            whileInView={{ scale: 1, rotate: 0 }}
            transition={{ delay: 0.2 + index * 0.1, type: 'spring' }}
            className="mb-4 text-accent text-3xl"
          >
            {icon}
          </motion.div>
        )}

        <h3 className="text-xl font-light tracking-tight mb-3">
          {title}
        </h3>

        <p className="text-sm font-light text-muted-foreground leading-relaxed">
          {description}
        </p>
      </div>
    </motion.div>
  )
}
