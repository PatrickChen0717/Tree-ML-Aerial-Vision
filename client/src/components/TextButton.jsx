import React from 'react'

const TextButton = ({ onClick, text }) => {
  return (
    <button onClick={onClick} className='self-center bg-black/50 hover:bg-white border-white border-[3px] text-white hover:text-primary text-xl font-semibold ease-in-out duration-300 px-4 py-2 rounded-3xl shadow-3xl hover:scale-125'>
      {text}
    </button>
  )
}

export default TextButton