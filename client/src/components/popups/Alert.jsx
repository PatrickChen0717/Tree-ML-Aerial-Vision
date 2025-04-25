import React from 'react'

const Alert = ({ alert, setAlert }) => {
  return (
    <div className="pointer-events-auto w-screen h-screen bg-black/70 fixed top-0 left-0 z-[60]">
      <div className={`max-h-[100vh] min-w-[100vw] lg:min-w-[30vw] px-8 py-8 z-20 fixed top-1/2 -translate-y-1/2 left-1/2 -translate-x-1/2 flex flex-col gap-4 pointer-events-none`}>
        <button onClick={() => setAlert(false)} className='self-center w-12 h-12 min-w-[48px] min-h-[48px] lg:w-16 lg:h-16 lg:min-w-[64px] lg:min-h-[64px] rounded-full bg-white top-6 right-6 font-bold text-xl lg:text-3xl text-primary lg:hover:scale-110 ease-in-out duration-300 pointer-events-auto'>
          X
        </button>
        <div className='w-full h-full max-h-[800px] bg-white rounded-3xl overscroll-contain overflow-y-scroll pointer-events-auto'>
          <div className='p-8 lg:p-16 flex flex-col gap-4 text-lg lg:text-2xl'>
            {alert.title && (
              <div className='text-2xl lg:text-4xl font-semibold self-center text-center capitalize'>
                {alert.title}
              </div>
            )}
            {alert.body}
            {alert.list && (
              <div className='flex flex-col items-start justify-center gap-4 pt-4'>
                {alert.list.title && (
                  <div className='text-xl lg:text-2xl font-bold leading-none'>
                    {alert.list.title}
                  </div>
                )}
                {alert.list.list && (
                  <div className='flex flex-col items-start justify-center gap-2 pl-4'>
                    {alert.list.list.map((item, i) => (
                      <div key={item + i} className=''>
                        - {item}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Alert