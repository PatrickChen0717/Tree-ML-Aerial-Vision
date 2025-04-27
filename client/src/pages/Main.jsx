import React from 'react'
import { MainSection, About } from '../sections'
import { help, mainUploadLinks } from '../constants'
import { UploadLink } from '../components'

const Main = () => {
  return (
      <div className='w-full flex flex-col items-center'>

        {/* --- First section: fills exactly one screen height --- */}
        <div className='w-full flex flex-col gap-10 py-10 lg:py-20 items-center bg-gradient-to-b from-primary to-accent min-h-screen'>
          <div className='flex flex-col w-full max-w-[90vw] lg:max-w-[1152px] items-center text-center'>
            <div className='w-full text-6xl text-white font-extrabold drop-shadow-md animate-fadeIn'>
              Hello!
            </div>
            <div className='w-full text-2xl text-tertiary font-bold mt-4'>
              Welcome to the Tree Species Identification App
            </div>
          </div>
          <div className='flex flex-col w-full max-w-[90vw] lg:max-w-[1152px] border-2 border-primary bg-gradient-to-br from-white/80 to-tertiary/10 shadow-3xl p-8 lg:p-16 rounded-3xl text-primary gap-10 animate-fadeIn backdrop-blur-sm'>
          <div className='w-full text-3xl text-tertiary font-bold tracking-wide text-center animate-slideIn'>
            Choose how you'd like to start:
          </div>
          <div className='flex flex-wrap justify-center gap-8'>
            {mainUploadLinks.map((link, i) => (
              <UploadLink key={link + i} link={link} />
            ))}
          </div>
        </div>

        {/* Scroll Down Indicator */}

        <a href="#about" className="flex flex-col items-center gap-1 py-6">
          <div className="text-white text-lg font-semibold group-hover:text-tertiary transition">
            More Info
          </div>
          <div className="flex justify-center items-center py-6 animate-dropBounce">
            <svg s
              className="w-8 h-8 text-white" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="4" 
              viewBox="0 0 24 24" 
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7"></path>
            </svg>
          </div>
        </a>

      </div>
      
      {/* --- After scrolling, new section starts --- */}
      <About />
      
      {help.map((item, i) => (
        <MainSection key={item + i} item={item} />
      ))}
    </div>
  )
}

export default Main