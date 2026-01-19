'use client'

import React, { useEffect, useRef } from 'react'
import gsap from 'gsap'
import ScrollTrigger from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

interface ScrollRevealProps {
  children: React.ReactNode
  direction?: 'up' | 'down' | 'left' | 'right'
  delay?: number
  duration?: number
  className?: string
}

export function ScrollReveal({
  children,
  direction = 'up',
  delay = 0,
  duration = 0.8,
  className = '',
}: ScrollRevealProps) {
  const ref = useRef(null)

  useEffect(() => {
    if (!ref.current) return

    const fromVars: any = {
      opacity: 0,
      duration,
      scrollTrigger: {
        trigger: ref.current,
        start: 'top 80%',
        end: 'top 30%',
        scrub: 0.5,
        markers: false,
      },
    }

    switch (direction) {
      case 'up':
        fromVars.y = 50
        break
      case 'down':
        fromVars.y = -50
        break
      case 'left':
        fromVars.x = 50
        break
      case 'right':
        fromVars.x = -50
        break
    }

    if (delay) {
      fromVars.delay = delay
    }

    gsap.from(ref.current, fromVars)

    return () => {
      ScrollTrigger.getAll().forEach((trigger) => trigger.kill())
    }
  }, [direction, delay, duration])

  return (
    <div ref={ref} className={className}>
      {children}
    </div>
  )
}

interface PinSectionProps {
  children: React.ReactNode
  className?: string
}

export function PinSection({ children, className = '' }: PinSectionProps) {
  const ref = useRef(null)

  useEffect(() => {
    if (!ref.current) return

    ScrollTrigger.create({
      trigger: ref.current,
      start: 'top top',
      end: 'bottom top',
      pin: true,
      pinSpacing: false,
      markers: false,
    })

    return () => {
      ScrollTrigger.getAll().forEach((trigger) => trigger.kill())
    }
  }, [])

  return (
    <div ref={ref} className={className}>
      {children}
    </div>
  )
}

interface ParallaxProps {
  children: React.ReactNode
  speed?: number
  className?: string
}

export function Parallax({ children, speed = 0.5, className = '' }: ParallaxProps) {
  const ref = useRef(null)

  useEffect(() => {
    if (!ref.current) return

    gsap.to(ref.current, {
      y: () => window.innerHeight * speed,
      scrollTrigger: {
        trigger: ref.current,
        start: 'top center',
        scrub: 0.5,
        markers: false,
      },
    })

    return () => {
      ScrollTrigger.getAll().forEach((trigger) => trigger.kill())
    }
  }, [speed])

  return (
    <div ref={ref} className={className}>
      {children}
    </div>
  )
}
