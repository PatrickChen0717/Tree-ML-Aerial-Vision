import React from 'react'

const UploadLink = ({ link }) => {
  return (
    <button onClick={() => window.location.href = link.link} className='flex-1 flex flex-col justify-center items-center gap-2 hover:scale-125 ease-in-out duration-300'>
      <img src={link.icon} className='w-12 h-12 lg:w-16 lg:h-16  brightness-0' />
      <div className='text-center text-black font-bold text-2xl lg:text-2xl'>
        {link.label}
      </div>
    </button>
  )
}

export default UploadLink