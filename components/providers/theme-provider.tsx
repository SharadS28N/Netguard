'use client'

import React, { createContext, useContext, useEffect, useState } from 'react'

type Theme = 'light' | 'dark'

interface ThemeContextType {
  theme: Theme
  toggleTheme: () => void
  mounted: boolean
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>('dark')
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    const stored = localStorage.getItem('netguard-theme') as Theme | null
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    const initialTheme = stored || (prefersDark ? 'dark' : 'light')
    
    setTheme(initialTheme)
    applyTheme(initialTheme)
    setMounted(true)
  }, [])

  const toggleTheme = () => {
    setTheme((prev) => {
      const newTheme = prev === 'dark' ? 'light' : 'dark'
      localStorage.setItem('netguard-theme', newTheme)
      applyTheme(newTheme)
      return newTheme
    })
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, mounted }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within ThemeProvider')
  }
  return context
}

function applyTheme(theme: Theme) {
  const html = document.documentElement
  if (theme === 'dark') {
    html.classList.add('dark')
  } else {
    html.classList.remove('dark')
  }

  // Update CSS variables for smooth transition
  const root = document.documentElement.style
  if (theme === 'light') {
    root.setProperty('--background', '#ffffff')
    root.setProperty('--foreground', '#0a0a0a')
    root.setProperty('--card', '#f5f5f5')
    root.setProperty('--card-foreground', '#0a0a0a')
    root.setProperty('--muted', '#e0e0e0')
    root.setProperty('--muted-foreground', '#333333')
    root.setProperty('--border', '#e0e0e0')
    root.setProperty('--input', '#f5f5f5')
  } else {
    root.setProperty('--background', '#0a0a0a')
    root.setProperty('--foreground', '#ffffff')
    root.setProperty('--card', '#1a1a1a')
    root.setProperty('--card-foreground', '#ffffff')
    root.setProperty('--muted', '#333333')
    root.setProperty('--muted-foreground', '#999999')
    root.setProperty('--border', '#333333')
    root.setProperty('--input', '#1a1a1a')
  }
}
