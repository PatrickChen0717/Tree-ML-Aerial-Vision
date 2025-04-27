import { treeline } from '../assets/images'
import { TextButton } from '../components'

import about_background from '../assets/images/about_background.jpg'

const About = () => {
  return (
    <div id="about" className='relative w-full flex flex-col items-center justify-center text-center py-24 px-6 overflow-hidden'>

      {/* Background Image */}
      <img 
        src={about_background} 
        alt="Background" 
        className="absolute inset-0 w-full h-full object-cover opacity-50" 
      />

      {/* Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/40 to-primary/30" />

      {/* Content */}
      <div className='relative flex flex-col items-center justify-center gap-8 max-w-4xl'>

        {/* Main Title */}
        <h1 className='text-4xl lg:text-5xl font-extrabold text-white leading-tight drop-shadow-lg'>
          About Tree Aerial Vision
        </h1>

        {/* Subtext / Mission */}
        <p className='text-lg lg:text-2xl text-white/80 max-w-2xl leading-relaxed'>
          We harness the power of ML and Aerial / Satellite imagery to protect, classify, and preserve the forests of our future.
        </p>

        {/* Discover More Button */}
        <div className='pt-6'>
          <TextButton 
            text="Discover More" 
            onClick={() => window.location.href = "https://github.com/PatrickChen0717/Tree-ML-Aerial-Vision"} 
          />
        </div>

      </div>
    </div>
  )
}
export default About;
