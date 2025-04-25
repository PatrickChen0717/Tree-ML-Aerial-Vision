import React from 'react'
import { MainSection, AboutKorotu } from '../sections'
import { help, mainUploadLinks } from '../constants'
import { UploadLink } from '../components'

const Main = () => {
  return (
    <div className='w-full flex flex-col gap-8 py-8 lg:py-16 items-center'>
      <div className='flex flex-col w-full max-w-[90vw] lg:max-w-[1152px]'>
        <div className='w-full text-6xl text-white font-bold'>
          Hello!
        </div>
        <div className='w-full text-2xl text-white font-bold'>
          Welcome to the Tree Species Identification App
        </div>
      </div>
      <div className='flex flex-col w-full max-w-[90vw] lg:max-w-[1152px] border-[3px] border-black/80 bg-white/80 shadow-3xl p-8 lg:p-16 rounded-3xl text-primary gap-8'>
        <div className='w-full text-2xl text-black font-bold'>
          Choose how you'd like to start:
        </div>
        <div className='flex flex-wrap justify-center gap-4'>
          {mainUploadLinks.map((link, i) => (
            <UploadLink key={link + i} link={link} />
          ))}
        </div>
      </div>
      <AboutKorotu />
      {help.map((item, i) => (
        <MainSection key={item + i} item={item} />
      ))}
    </div>
  )
}

export default Main