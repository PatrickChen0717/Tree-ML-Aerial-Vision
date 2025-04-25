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
        palanquin: ['Palanquin', 'sans-serif'],
        montserrat: ['Montserrat', 'sans-serif'],
      },
      colors: {
        "primary": "#357960",
        'secondary': "#1e4436",
        "tertiary": "#4cae8a",
      },
      boxShadow: {
        '3xl': '0 10px 40px rgba(0, 0, 0, 0.1)'
      },
      backgroundImage: {
        'hero': "url('assets/images/collection-background.png')",
      },
      screens: {
        "wide": "1440px"
      },
      keyframes: {
        wiggle: {
          '0%, 100%': { transform: 'translateY(-25%)' },
          '50%': { transform: 'translateY(0)' },
        },
        dropBounce: {
          '0%, 100%': { 
            transform: 'translateY(0%) rotate(45deg)'
          },
          '50%': { 
            transform: 'translateY(-25%) rotate(45deg)'
          }
        }
      },
      animation: {
        dropBounce: 'dropBounce 1s ease-in-out infinite',
      }
    },
  },
  plugins: [tailwind_scrollbar_hide],
}