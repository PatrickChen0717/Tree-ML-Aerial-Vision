import tailwind_scrollbar_hide from 'tailwind-scrollbar-hide';

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    fontSize: {
      xs: ['12px', '16px'],
      sm: ['14px', '20px'],
      base: ['16px', '19.5px'],
      lg: ['18px', '21.94px'],
      xl: ['20px', '24.38px'],
      '2xl': ['24px', '29.26px'],
      '3xl': ['28px', '50px'],
      '4xl': ['48px', '58px'],
      '5xl': ['60px', '72px'],
      '6xl': ['72px', '87px'],
      '8xl': ['96px', '106px']
    },
    extend: {
      fontFamily: {
        palanquin: ['Poppins', 'sans-serif'],  // Changed font
        montserrat: ['Raleway', 'sans-serif'], // Changed font
      },
      colors: {
        "primary": "#81cc70",
        'secondary': "#1e4436",
        "tertiary": "#357960",
        "accent": "#469e7e",
      },
      boxShadow: {
        '3xl': '0 20px 60px rgba(0, 0, 0, 0.2)', // Stronger shadow
      },
      backgroundImage: {
        'hero': "url('assets/images/new-hero-background.png')", // Assume you change bg image
      },
      screens: {
        "wide": "1440px",
      },
      keyframes: {
        wiggle: {
          '0%, 100%': { transform: 'rotate(-5deg)' }, // Different wiggle effect
          '50%': { transform: 'rotate(5deg)' },
        },
        dropBounce: {
          '0%, 100%': { transform: 'translateY(0%) rotate(0deg)' },
          '50%': { transform: 'translateY(-15%) rotate(0deg)' },
        },
      },
      animation: {
        wiggle: 'wiggle 1s ease-in-out infinite',   // Added animated wiggle
        dropBounce: 'dropBounce 1.5s ease-in-out infinite',
      }
    },
  },
  plugins: [tailwind_scrollbar_hide],
}
