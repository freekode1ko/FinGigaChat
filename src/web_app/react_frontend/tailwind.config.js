/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        'bg-color': 'var(--bg-color)',
        'text-color': 'var(--text-color)',
        'hint-color': 'var(--hint-color)',
        'link-color': 'var(--link-color)',
        'button-color': 'var(--button-color)',
        'button-text-color': 'var(--button-text-color)',
        'secondary-bg-color': 'var(--secondary-bg-color)',
        'header-bg-color': 'var(--header-bg-color)',
        'accent-text-color': 'var(--accent-text-color)',
        'section-bg-color': 'var(--section-bg-color)',
        'section-header-text-color': 'var(--section-header-text-color)',
        'section-separator-color': 'var(--section-separator-color)',
        'subtitle-text-color': 'var(--subtitle-text-color)',
        'destructive-text-color': 'var(--destructive-text-color)',
      },
    },
  },
  plugins: [],
}
