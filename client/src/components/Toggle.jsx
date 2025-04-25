import React, { useState } from 'react'

const Toggle = ({ setState, state, option1, option2 }) => {
  const flip = () => {
    if (state == option1) {
      setState(option2);
    } else if (state == option2) {
      setState(option1);
    }
  }

  return (
    <div className="self-center flex gap-4 text-white justify-center items-center w-full">
      <div className="flex-1 flex justify-end">
        <button onClick={() => setState(option1)} className="text-sm lg:text-xl font-semibold bg-black/50 border-white border-[3px] text-center h-min px-4 py-2 rounded-3xl shadow-3xl lg:hover:bg-white lg:hover:text-primary lg:hover:scale-125 ease-in-out duration-300 w-24 lg:w-40">
          {option1}
        </button>
      </div>
      <button onClick={() => flip()} className='w-20 h-10 lg:w-24 lg:h-12 rounded-full relative bg-primary border-white border-[4px] shadow-3xl'>
        <div className={`absolute ${state == option1 ? 'left-1' : ' left-[44px] lg:left-[52px]'} top-1 w-6 h-6 lg:w-8 lg:h-8 bg-white rounded-full ease-in-out duration-300`} />
      </button>
      <div className='flex-1 flex justify-start'>
        <button onClick={() => setState(option2)} className="text-sm lg:text-xl font-semibold bg-black/50 border-white border-[3px] text-center h-min px-4 py-2 rounded-3xl shadow-3xl lg:hover:bg-white lg:hover:text-primary lg:hover:scale-125 ease-in-out duration-300 w-24 lg:w-40">
          {option2}
        </button>
      </div>
    </div>
  )
}

export default Toggle