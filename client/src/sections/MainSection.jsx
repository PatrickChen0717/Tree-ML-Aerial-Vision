import React from 'react'
import { TextButton } from '../components'

const MainSection = ({ item }) => {
  return (
    <div className="w-full flex justify-center items-center bg-accent py-12 px-4">
      <div className="w-full max-w-[1152px] bg-white/90 backdrop-blur-md shadow-3xl rounded-3xl overflow-hidden">

        {/* Card content */}
        <div className="flex flex-col lg:flex-row gap-4 p-8 lg:p-12 items-center">

          {/* Text Section */}
          <div className="flex flex-col gap-6 text-tertiary w-full lg:w-2/3">
            {item.title && (
              <h2 className="text-4xl font-extrabold leading-tight text-center lg:text-left">
                {item.title}
              </h2>
            )}
            {item.body && (
              <p className="text-lg leading-relaxed text-center lg:text-left">
                {item.body}
              </p>
            )}
            {item.link && (
              <div className="pt-4 flex justify-center lg:justify-start">
                <TextButton onClick={() => window.location.href = item.link} text={"CLICK HERE FOR HELP"} />
              </div>
            )}
          </div>

          {/* Media Section */}
          <div className="flex flex-col gap-6 items-center w-full lg:w-1/2">
            {item.icon && (
              <img src={item.icon} alt="Icon" className="w-32 h-32" />
            )}
            {item.image && (
              <img src={item.image} alt="Image" className="w-full max-w-sm object-cover rounded-xl" />
            )}
          </div>

        </div>

        {/* If there are extra sections */}
        {item.sections && (
          <div className="flex flex-col gap-4 p-8 lg:p-16">
            {item.sections.map((section, index) => (
              <div key={index} className={`flex flex-col ${section.reverse ? 'lg:flex-row-reverse' : 'lg:flex-row'} gap-8 items-center`}>
                
                {/* Text for Subsection */}
                <div className="flex flex-col gap-4 text-primary w-full lg:w-1/2">
                  {section.title && (
                    <h3 className="text-2xl font-bold text-center lg:text-left">
                      {section.title}
                    </h3>
                  )}
                  {section.body && (
                    <p className="text-base text-center lg:text-left">
                      {section.body}
                    </p>
                  )}
                  {section.link && (
                    <div className="pt-2 flex justify-center lg:justify-start">
                      <TextButton onClick={() => window.location.href = section.link} text={"CLICK HERE FOR HELP"} />
                    </div>
                  )}
                </div>

                {/* Media for Subsection */}
                <div className="flex justify-center w-full lg:w-1/2">
                  {section.icon && (
                    <img src={section.icon} alt="Sub Icon" className="w-32 h-32" />
                  )}
                  {section.image && (
                    <img src={section.image} alt="Sub Image" className="w-full max-w-sm object-cover rounded-xl" />
                  )}
                </div>

              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}

export default MainSection