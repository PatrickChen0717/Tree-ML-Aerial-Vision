import React from 'react'
import { droneOptions } from '../constants'
import { DroneLink } from '../components'

const Drone = ({ setAlert }) => {
  return (
    <div className='flex-1 flex flex-col justify-center items-center w-full lg:px-16 pb-12 lg:pb-16'>
      <div className='max-w-[80vw] lg:max-w-[1152px] flex flex-col gap-8 items-center w-full'>
        <div className='text-white font-bold text-3xl lg:text-4xl text-center leading-tight'>
          WHAT TYPE OF DRONE CLASSIFICATION WOULD YOU LIKE?
        </div>
        <div className='flex flex-col lg:flex-row border-[3px] border-white bg-black/50 shadow-3xl p-12 lg:p-16 rounded-3xl text-white gap-8 justify-center items-center w-full'>
          {droneOptions.map((option, i) => (
            <DroneLink key={option + i} link={option} />
          ))}
        </div>
      </div>
    </div>
  )
}

export default Drone