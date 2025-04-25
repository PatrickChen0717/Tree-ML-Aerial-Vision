import React from 'react'
import { HelpSection } from '../sections'

const Help = ({ title, list }) => {
  return (
    <div className='flex flex-col w-screen h-full pb-16'>
      <div className='text-center self-center text-white text-4xl font-bold max-w-[80vw]'>
        {title}
      </div>
      <div className="flex flex-col gap-8 pt-4 lg:pt-8">
        {list.map((item) => (
          <HelpSection key={item.title} item={item} />
        ))}
      </div>
    </div>
  )
}

export default Help