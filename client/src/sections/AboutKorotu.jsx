import React from 'react'
import { aboutKorotuSections } from '../constants'
import { AboutKorotuSection } from '.'
import { treeline } from '../assets/images'
import { TextButton } from '../components'

const AboutKorotu = () => {
  return (
    <div className='flex flex-col w-full justify-center items-center gap-0 py-8 lg:py-16'>
      <img src={treeline} className='w-[100vw] h-[10vw] brightness-0 opacity-60' />
      <div className='flex flex-col w-full justify-center items-center gap-8 pt-16 pb-20 lg:pb-32 bg-black/60'>
        <div className='w-full text-start max-w-[90vw] lg:max-w-[1152px] text-white font-bold text-6xl'>
          About Korotu
        </div>
        {aboutKorotuSections.map((section, i) => (
          <AboutKorotuSection key={section + i} section={section} />
        ))}
        <TextButton text={"Discover More"} onClick={() => window.location.href = "https://www.korotu.com/home"} />
      </div>
    </div>
  )
}

export default AboutKorotu