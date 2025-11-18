/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Military-themed color palette
        tactical: {
          bg: '#0a0e12',
          surface: '#111827',
          border: '#1f2937',
          hover: '#1e293b',
          text: '#e5e7eb',
          muted: '#9ca3af',
        },
        threat: {
          low: '#10b981',
          medium: '#f59e0b',
          high: '#ef4444',
          critical: '#dc2626',
        },
        status: {
          green: '#10b981',
          amber: '#f59e0b',
          red: '#ef4444',
          black: '#374151',
        },
        tactical: {
          primary: '#22c55e',
          secondary: '#f59e0b',
          accent: '#3b82f6',
        },
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Courier New', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'ping-slow': 'ping 2s cubic-bezier(0, 0, 0.2, 1) infinite',
      },
    },
  },
  plugins: [],
}
