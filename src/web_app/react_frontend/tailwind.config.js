/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#b9e6fe',
          300: '#7cd3fd',
          400: '#36befa',
          500: '#0ca6eb',
          600: '#0087cc',
          700: '#0169a3',
          800: '#065986',
          900: '#0b4a6f',
          950: '#072f4a',
        },
        secondary: {
          50: '#f6f9f9',
          100: '#ecf0f1',
          200: '#d6dfe1',
          300: '#b2c4c7',
          400: '#88a4a8',
          500: '#6a898d',
          600: '#557074',
          700: '#455b5f',
          800: '#3c4d50',
          900: '#354245',
          950: '#232c2e',
        },
        'dark-blue': '#000115',
      },
      keyframes: {
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' },
        },
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
      },
    },
  },
  plugins: [],
}
