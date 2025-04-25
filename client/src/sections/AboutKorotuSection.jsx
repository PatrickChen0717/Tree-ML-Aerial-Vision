import React from 'react'

const AboutKorotuSection = ({ section }) => {
  return (
    <div className="w-screen flex flex-col justify-center items-center">
      {section.sections ? (
        <div className={`w-full max-w-[90vw] lg:max-w-[1152px] flex flex-col px-8 lg:px-16 rounded-3xl text-white gap-8 justify-center items-center`}>
          {section.title && (
            <div className="text-3xl font-bold text-center leading-tight">
              {section.title}
            </div>
          )}
          {section.sections.map((section, i) => (
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
                <div className="min-w-[70vw] min-h-[70vw] lg:min-w-64 lg:min-h-64">
                  <img src={section.image} className="w-[70vw] h-[70vw] lg:w-64 lg:h-64" />
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="w-full max-w-[90vw] lg:max-w-[1152px] flex flex-col-reverse lg:flex-row px-8 lg:px-16 rounded-3xl text-white gap-8 lg:gap-16 justify-center items-center">
          <div className="flex flex-col justify-center items-center lg:justify-start lg:items-start gap-4">
            {section.title && (
              <div className="text-3xl font-bold text-center leading-tight">
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
            <div className="min-w-32 min-h-32">
              <img src={section.image} className="brightness-0 invert w-32 h-32" />
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default AboutKorotuSection