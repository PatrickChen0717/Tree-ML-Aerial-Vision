import React from 'react'
import { TextButton } from '../components'

const HelpSection = ({ item }) => {
  return (
    <div className="w-screen flex flex-col justify-center items-center">
      {item.sections ? (
        <div className={`w-full max-w-[90vw] lg:max-w-[1152px] flex flex-col border-[3px] border-white bg-black/50 shadow-3xl p-8 lg:p-16 rounded-3xl text-white gap-8 justify-center items-start`}>
          {item.title && (
            <div className="text-3xl font-bold text-center leading-tight">
              {item.title}
            </div>
          )}
          {item.sections.map((section, i) => (
            <div key={section + i} className={`flex ${section.reverse ? 'lg:flex-row-reverse' : 'lg:flex-row'} flex-col gap-8 lg:gap-16 justify-center items-center`}>
              <div className="flex flex-col justify-center items-center lg:justify-start lg:items-start gap-2">
                {section.title && (
                  <div className="text-xl font-bold text-center leading-tight">
                    {section.title}
                  </div>
                )}
                {section.body && (
                  <div className="text-xl">
                    {section.body}
                  </div>
                )}
                {section.link && (
                  <div className="pt-4">
                    <TextButton onClick={() => window.location.href = section.link} text={"CLCIK HERE FOR HELP"} />
                  </div>
                )}
              </div>
              {section.icon && (
                <div className="min-w-32 min-h-32">
                  <img src={section.icon} className="brightness-0 invert w-32 h-32" />
                </div>
              )}
              {section.image && (
                <div className="flex justify-center items-center">
                  <img src={section.image} className="w-[70vw] min-w-[70vw] max-w-[70vw] lg:w-64 lg:min-w-64 lg:max-w-64 h-auto object-cover" />
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="w-full max-w-[90vw] lg:max-w-[1152px] flex flex-col-reverse lg:flex-row border-[3px] border-white bg-black/50 shadow-3xl p-8 lg:p-16 rounded-3xl text-white gap-8 lg:gap-16 justify-center items-center">
          <div className="flex flex-col justify-center items-center lg:justify-start lg:items-start gap-4">
            {item.title && (
              <div className="text-3xl font-bold text-center leading-tight">
                {item.title}
              </div>
            )}
            {item.body && (
              <div className="text-xl">
                {item.body}
              </div>
            )}
            {item.link && (
              <div className="pt-4">
                <TextButton onClick={() => window.location.href = item.link} text={"CLCIK HERE FOR HELP"} />
              </div>
            )}
          </div>
          {item.icon && (
            <div className="min-w-32 min-h-32">
              <img src={item.icon} className="brightness-0 invert w-32 h-32" />
            </div>
          )}
          {item.image && (
            <div className="flex justify-center items-center">
              <img src={item.image} className="w-[70vw] lg:w-64 h-auto object-contain" />
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default HelpSection