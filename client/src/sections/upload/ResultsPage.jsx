import React, { useState } from 'react'
import html2canvas from 'html2canvas';
import JSZip from 'jszip';
import { saveAs } from 'file-saver';

import { CircleChart, TextButton } from '../../components';
import { info } from '../../assets/icons';
import { Toggle, Loader } from '../../components';

const ResultsPage = ({ results, setFile, setAlert }) => {
  const [imageUI, setImageUI] = useState('Show');
  const [downloading, setDownloading] = useState(false);

  const classesGenus = [
    "Fir",
    "Maple",
    "Alder",
    "Birch",
    "Cleared",
    "Beech",
    "Ash",
    "Larch",
    "Spruce",
    "Pine",
    "Douglas-fir",
    "Oak"
  ]

  const classesSpecies = [
    "Scots pine",
    "European beech",
    "Norway spruce",
    "Cleared",
    "English oak",
    "Sycamore maple",
    "Birch species",
    "Douglas fir",
    "European ash",
    "Sessile oak",
    "Alder species",
    "Northern red oak",
    "Japanese larch",
    "European larch",
    "Silver fir",
    "Eastern white pine",
    "Black pine"
  ]

  const colorsGenus = [
    "bg-red-500",
    "bg-yellow-400",
    "bg-green-500",
    "bg-blue-500",
    "bg-white",
    "bg-pink-500",
    "bg-orange-500",
    "bg-teal-500",
    "bg-indigo-500",
    "bg-lime-500",
    "bg-amber-500",
    "bg-rose-500"
  ];

  const colorsSpecies = [
    "bg-red-600",
    "bg-yellow-500",
    "bg-green-600",
    "bg-white",
    "bg-purple-600",
    "bg-pink-600",
    "bg-orange-600",
    "bg-teal-600",
    "bg-indigo-600",
    "bg-lime-600",
    "bg-amber-600",
    "bg-cyan-600",
    "bg-emerald-600",
    "bg-fuchsia-600",
    "bg-sky-600",
    "bg-violet-600",
    "bg-rose-600"
  ];

  const downloadResults = async () => {
    setDownloading(true);
    setImageUI('Show')

    await new Promise(res => setTimeout(res, 200));

    const zip = new JSZip();

    if (results.predictions) {
      zip.file('annotated_image.png', results.image, { base64: true });
      zip.file('raw_image.png', results.plainImage, { base64: true });

      const element = document.getElementById('print');

      const originalPadding = element.style.padding;
      element.style.padding = '64px';
      element.classList.add('bg-primary');

      await new Promise(res => setTimeout(res, 50));

      const canvas = await html2canvas(element, { useCORS: true });
      const dataUrl = canvas.toDataURL('image/jpeg', 1.0);
      const base64 = dataUrl.split(',')[1];

      zip.file('data_image.jpg', base64, { base64: true });

      element.style.padding = originalPadding;
      element.classList.remove('bg-primary');

      zip.generateAsync({ type: 'blob' }).then((content) => {
        saveAs(content, 'phone_classification_results.zip');
        setDownloading(false);
      });
    } else if (results.labelPercentage) {
      zip.file('raw_image.png', results.image, { base64: true });

      const img = new Image();
      img.src = `data:image/png;base64,${results.image}`;

      img.onload = async () => {
        const targetWidth = img.naturalWidth;
        const targetHeight = img.naturalHeight;

        const element_1 = document.getElementById('print');
        const originalPadding_1 = element_1.style.padding;
        element_1.style.padding = '64px';
        element_1.classList.add('bg-primary');
        const canvas_1 = await html2canvas(element_1, { useCORS: true });
        const dataUrl_1 = canvas_1.toDataURL('image/jpeg', 1.0);
        const base64_1 = dataUrl_1.split(',')[1];
        zip.file('data_image.jpg', base64_1, { base64: true });
        element_1.style.padding = originalPadding_1;
        element_1.classList.remove('bg-primary');

        const image = document.getElementById('download-image');
        const originalImageStyles = {
          width: image.style.width,
          height: image.style.height,
          maxWidth: image.style.maxWidth,
          maxHeight: image.style.maxHeight,
          objectFit: image.style.objectFit,
        };
        image.style.width = `${targetWidth}px`;
        image.style.height = `${targetHeight}px`;
        image.style.maxWidth = 'none';
        image.style.maxHeight = 'none';
        image.style.objectFit = 'contain';

        const element_2 = document.getElementById('print-overlay');
        const originalStyles = {
          width: element_2.style.width,
          height: element_2.style.height,
          transform: element_2.style.transform,
          transformOrigin: element_2.style.transformOrigin
        };
        element_2.style.width = `${targetWidth}px`;
        element_2.style.height = `${targetHeight}px`;
        element_2.style.transform = 'scale(1)';
        element_2.style.transformOrigin = 'top left';

        await new Promise(res => setTimeout(res, 50));

        const canvas_2 = await html2canvas(element_2, {
          width: targetWidth,
          height: targetHeight,
          useCORS: true
        });
        const dataUrl_2 = canvas_2.toDataURL('image/jpeg', 1.0);
        const base64_2 = dataUrl_2.split(',')[1];
        zip.file('annotated_image.jpg', base64_2, { base64: true });

        element_2.style.width = originalStyles.width;
        element_2.style.height = originalStyles.height;
        element_2.style.transform = originalStyles.transform;
        element_2.style.transformOrigin = originalStyles.transformOrigin;

        image.style.width = originalImageStyles.width;
        image.style.height = originalImageStyles.height;
        image.style.maxWidth = originalImageStyles.maxWidth;
        image.style.maxHeight = originalImageStyles.maxHeight;
        image.style.objectFit = originalImageStyles.objectFit;

        const zipName = results.estimateRes
          ? 'drone_RGB_classification_results.zip'
          : 'satellite_classification_results.zip';

        zip.generateAsync({ type: 'blob' }).then((content) => {
          saveAs(content, zipName);
        });
      }
    } else if (results.imageFG && results.imageBG) {
      const img = new Image();
      img.src = `data:image/png;base64,${results.imageBG}`;

      img.onload = async () => {
        const element_1 = document.getElementById('print');
        if (element_1) {
          const originalPadding_1 = element_1.style.padding;
          element_1.style.padding = '64px';
          element_1.classList.add('bg-primary');
          const canvas_1 = await html2canvas(element_1, { useCORS: true });
          const dataUrl_1 = canvas_1.toDataURL('image/jpeg', 1.0);
          const base64_1 = dataUrl_1.split(',')[1];
          zip.file('data_image.jpg', base64_1, { base64: true });
          element_1.style.padding = originalPadding_1;
          element_1.classList.remove('bg-primary');
        }

        const targetWidth = img.naturalWidth;
        const targetHeight = img.naturalHeight;

        zip.file('background_image.png', results.imageBG, { base64: true });

        const containerEl = document.getElementById('print-seg');
        const imageBGEl = document.getElementById('image-BG');
        const imageFGEl = document.getElementById('image-FG');

        if (!containerEl || !imageBGEl || !imageFGEl) {
          console.error('One or more elements (#print-seg, #image-BG, #image-FG) not found.');
          setDownloading(false);
          return;
        }

        const originalBGStyles = {
          width: imageBGEl.style.width,
          height: imageBGEl.style.height,
          maxWidth: imageBGEl.style.maxWidth,
          maxHeight: imageBGEl.style.maxHeight,
        };

        const originalFGStyles = {
          width: imageFGEl.style.width,
          height: imageFGEl.style.height,
          maxWidth: imageFGEl.style.maxWidth,
          maxHeight: imageFGEl.style.maxHeight,
        };

        const originalContainerStyles = {
          width: containerEl.style.width,
          height: containerEl.style.height,
        };

        imageBGEl.style.width = `${targetWidth}px`;
        imageBGEl.style.height = `${targetHeight}px`;
        imageBGEl.style.maxWidth = 'none';
        imageBGEl.style.maxHeight = 'none';

        imageFGEl.style.width = `${targetWidth}px`;
        imageFGEl.style.height = `${targetHeight}px`;
        imageFGEl.style.maxWidth = 'none';
        imageFGEl.style.maxHeight = 'none';

        containerEl.style.width = `${targetWidth}px`;
        containerEl.style.height = `${targetHeight}px`;

        await new Promise(res => setTimeout(res, 100));

        const canvas = await html2canvas(containerEl, {
          width: targetWidth,
          height: targetHeight,
          useCORS: true
        });

        const dataUrl = canvas.toDataURL('image/jpeg', 1.0);
        const base64 = dataUrl.split(',')[1];
        zip.file('overlay_image.jpg', base64, { base64: true });

        Object.assign(imageBGEl.style, originalBGStyles);
        Object.assign(imageFGEl.style, originalFGStyles);
        Object.assign(containerEl.style, originalContainerStyles);

        zip.generateAsync({ type: 'blob' }).then((content) => {
          saveAs(content, 'drone_seg_results.zip');
        });
      };
    } else if (results.prediction) {
      const element = document.getElementById('print');

      const originalPadding = element.style.padding;
      element.style.padding = '64px';
      element.classList.add('bg-primary');

      await new Promise(res => setTimeout(res, 50));

      const canvas = await html2canvas(element, { useCORS: true });
      const dataUrl = canvas.toDataURL('image/jpeg', 1.0);
      const base64 = dataUrl.split(',')[1];

      zip.file('data_image.jpg', base64, { base64: true });

      element.style.padding = originalPadding;
      element.classList.remove('bg-primary');

      zip.generateAsync({ type: 'blob' }).then((content) => {
        saveAs(content, 'phone_classification_results.zip');
        setDownloading(false);
      });
    }

    await new Promise(res => setTimeout(res, 1000));

    setDownloading(false);
  }

  return (
    <div className="flex flex-col items-center gap-8 pb-16">
      <div className={`${!downloading && 'opacity-0'} w-screen h-screen fixed top-0 left-0 flex flex-col justify-center items-center text-center z-[9999] bg-primary text-white font-bold text-xl gap-8 pointer-events-none`}>
        Downloading...
        <Loader />
      </div>
      <button onClick={() => setFile(null)} className='self-center rounded-full bg-white whitespace-nowrap px-4 py-2 font-bold text-xl lg:text-xl text-primary lg:hover:scale-110 ease-in-out duration-300 pointer-events-auto'>
        ← Back
      </button>
      <div className="flex flex-col lg:flex-row relative gap-8 lg:gap-16">
        {results.imageFG && results.imageBG && (
          <div className="flex flex-col items-center gap-4 relative max-w-[90vw]">
            <div id='print-seg' className="relative">
              <img
                id='image-BG'
                src={`data:image/png;base64,${results.imageBG}`}
                alt="Background"
                className="border-[3px] border-white rounded-lg shadow-lg max-h-[60vh] max-w-[90vw]"
              />
              {imageUI === 'Show' && (
                <>
                  <img
                    id='image-FG'
                    src={results.imageFG}
                    alt="Foreground Overlay"
                    className="absolute top-0 left-0 border-[3px] border-white rounded-lg shadow-lg max-h-[60vh] max-w-[90vw] opacity-70"
                  />
                </>
              )}
            </div>
            <div className="flex flex-col justify-center items-center gap-4 text-white font-bold text-xl lg:text-2xl">
              CLASSIFICATION OVERLAY
              <Toggle setState={setImageUI} state={imageUI} option1={'Show'} option2={'Hide'} />
            </div>
          </div>
        )}
        {results.imageFG && results.imageBG && results.data && (
          <div className="flex flex-col items-center">
            <div id='print' className='flex flex-col items-center gap-4'>
              <CircleChart predictions_seg={results.data} />
            </div>
          </div>
        )}
        {results.image && !results.shaderGridGenus && !results.shaderGridSpecies && (
          <div className="flex flex-col items-center gap-4 relative max-w-[90vw]">
            {imageUI == 'Show' ? (
              <div className='relative'>
                <button className='bg-white rounded-full whitespace-normal self-center absolute top-4 left-4' onClick={() => setAlert({ title: "Did we find the tree?", body: "Ensure that the red area in the image properly outlines the tree. If there is no red on the image, or if the red area fails to capture the tree you are trying to classify, please refer to our guide on how to take pictures of the tree and upload a new picture." })}>
                  <img src={info} className='w-8 h-8 lg:w-12 lg:h-12' />
                </button>
                <img src={`data:image/png;base64,${results.image}`} alt="result image" className="border-[3px] border-white rounded-lg shadow-lg max-h-[60vh] max-w-[90vw]" />
              </div>
            ) : (
              <>
                <img src={`data:image/png;base64,${results.plainImage}`} alt="result image" className="border-[3px] border-white rounded-lg shadow-lg max-h-[60vh] max-w-[80vw]" />
              </>
            )}
            <div className="flex flex-col justify-center items-center gap-4 text-white font-bold text-xl lg:text-2xl">
              CLASSIFICATION OVERLAY
              <Toggle setState={setImageUI} state={imageUI} option1={'Show'} option2={'Hide'} />
            </div>
          </div>
        )}
        {results.predictions && (
          <div className="flex flex-col items-center">
            <button className='bg-white rounded-full whitespace-normal self-center mb-4' onClick={() => setAlert({ title: "How Was My Image Classified?", body: `Your image was segmented according to the photo on the left, then cropped to contain only tree bark and resized to ${results.resizedWidth}x${results.resizedHeight} pixels. The image was split into ${results.patches} patches of 224x224 pixels, and each classified individually. If the model is unsure, it means less than 50% of the patches were in agreement.` })}>
              <img src={info} className='w-8 h-8 lg:w-12 lg:h-12' />
            </button>
            <div id='print' className='flex flex-col items-center gap-4'>
              <div className='text-white flex flex-col gap-2 max-w-[90vw]'>
                <div className='text-xl lg:text-2xl font-bold leading-tight'>
                  Classification Settings:
                </div>
                <div className='flex flex-col gap-2 pl-4'>
                  <div className='flex flex-row flex-wrap gap-2 font-bold text-base lg:text-lg'>
                    Level: <div className='font-normal'>{results.genus ? 'Genus' : 'Species'}</div>
                  </div>
                  <div className='flex flex-row flex-wrap gap-2 font-bold text-base lg:text-lg'>
                    Set: <div className='font-normal'>{results.partial ? 'Partial' : 'Full'}</div>
                  </div>
                </div>
              </div>
              <CircleChart predictions={results.predictions} />
            </div>
          </div>
        )}
        {results.prediction && (
          <div className="flex flex-col items-center">
            <div id='print' className='flex flex-col items-center gap-4'>
              <div className='text-white flex flex-col gap-2 max-w-[90vw]'>
                <div className='text-xl lg:text-2xl font-bold leading-tight'>
                  Classification:
                </div>
                <div className='flex flex-col gap-2 pl-4'>
                  <div className='flex flex-row flex-wrap gap-2 font-bold text-base lg:text-lg'>
                    Genus: <div className='font-normal'>{results.prediction.genus_pred}</div>
                  </div>
                  <div className='flex flex-row flex-wrap gap-2 font-bold text-base lg:text-lg'>
                    Genus Confidence: <div className='font-normal'>{results.prediction.genus_conf}</div>
                  </div>
                  <div className='flex flex-row flex-wrap gap-2 font-bold text-base lg:text-lg'>
                    Species: <div className='font-normal'>{results.prediction.species_pred}</div>
                  </div>
                  <div className='flex flex-row flex-wrap gap-2 font-bold text-base lg:text-lg'>
                    Species Confidence: <div className='font-normal'>{results.prediction.species_conf}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
        {results.shaderGridGenus && (
          <div className="flex flex-col justify-center items-center gap-8">
            <div className='border-[4px] border-white rounded-lg shadow-lg '>
              <div id='print-overlay' className="relative">
                <img
                  id="download-image"
                  src={`data:image/png;base64,${results.image}`}
                  alt="result image"
                  className="max-h-[60vh] max-w-[80vw]"
                />

                <div
                  className={`absolute inset-0`}
                  style={{
                    display: 'grid',
                    gridTemplateColumns: `repeat(${results.shaderGridGenus.length}, 1fr)`,
                    gridTemplateRows: `repeat(${results.shaderGridGenus.length}, 1fr)`,
                  }}
                >
                  {results.shaderGridGenus.flat().map((value, i) => (
                    <div key={i} className={`relative group border border-white ${imageUI == 'Show' ? 'flex' : 'hidden'}`}>
                      <div className={`flex-1 ${colorsGenus[value]} opacity-40 hover:opacity-60 relative`} />

                      <div className="hidden group-hover:flex p-6 absolute -bottom-2 -right-2 translate-x-full translate-y-full opacity-100 z-20 border-2 border-white bg-primary text-white rounded-xl text-xl capitalize">
                        {classesGenus[value]}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            <div className="flex flex-col justify-center items-center gap-4 text-white font-bold text-xl lg:text-2xl">
              CLASSIFICATION OVERLAY
              <Toggle setState={setImageUI} state={imageUI} option1={'Show'} option2={'Hide'} />
            </div>
          </div>
        )}
        {results.shaderGridSpecies && (
          <div className="flex flex-col justify-center items-center gap-8">
            <div className='border-[4px] border-white rounded-lg shadow-lg '>
              <div id='print-overlay' className="relative">
                <img
                  id="download-image"
                  src={`data:image/png;base64,${results.image}`}
                  alt="result image"
                  className="max-h-[60vh] max-w-[80vw]"
                />

                <div
                  className={`absolute inset-0`}
                  style={{
                    display: 'grid',
                    gridTemplateColumns: `repeat(${results.shaderGridSpecies.length}, 1fr)`,
                    gridTemplateRows: `repeat(${results.shaderGridSpecies.length}, 1fr)`,
                  }}
                >
                  {results.shaderGridSpecies.flat().map((value, i) => (
                    <div key={i} className={`relative group border border-white ${imageUI == 'Show' ? 'flex' : 'hidden'}`}>
                      <div className={`flex-1 ${colorsSpecies[value]} opacity-25 hover:opacity-70 relative`} />

                      <div className="hidden group-hover:flex p-2 lg:p-6 absolute -bottom-4 left-1/2 -translate-x-1/2 translate-y-full opacity-100 z-20 border-2 border-white bg-primary text-white rounded-xl text-base lg:text-xl text-center capitalize">
                        {classesSpecies[value]}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            <div className="flex flex-col justify-center items-center gap-4 text-white font-bold text-xl lg:text-2xl">
              CLASSIFICATION OVERLAY
              <Toggle setState={setImageUI} state={imageUI} option1={'Show'} option2={'Hide'} />
            </div>
          </div>
        )}
        {results.labelPercentage && results.shaderGridGenus && (
          <div className="flex flex-col items-center gap-4">
            <div id='print' className='flex flex-col items-center gap-4'>
              <div className='text-white flex flex-col gap-2 max-w-[90vw]'>
                <div className='text-xl lg:text-2xl font-bold leading-tight'>
                  Classification Settings:
                </div>
                <div className='flex flex-col gap-2 pl-4'>
                  {results.estimateRes &&
                    <div className='flex flex-row flex-wrap gap-2 font-bold text-base lg:text-lg'>
                      Resolution: <div className='font-normal'>{results.estimateRes} cm/pixel</div>
                    </div>
                  }
                  <div className='flex flex-row flex-wrap gap-2 font-bold text-base lg:text-lg'>
                    Level: <div className='font-normal'>{results.genusSpecies}</div>
                  </div>
                </div>
              </div>
              <CircleChart labelPercentage={results.labelPercentage} genus={true} />
            </div>
          </div>
        )}
        {results.labelPercentage && results.shaderGridSpecies && (
          <div className="flex flex-col items-center gap-4">
            <div id='print' className='flex flex-col items-center gap-4'>
              <div className='text-white flex flex-col gap-2 max-w-[90vw]'>
                <div className='text-xl lg:text-2xl font-bold leading-tight'>
                  Classification Settings:
                </div>
                <div className='flex flex-col gap-2 pl-4'>
                  {results.estimateRes &&
                    <div className='flex flex-row flex-wrap gap-2 font-bold text-base lg:text-lg'>
                      Resolution: <div className='font-normal'>{results.estimateRes} cm/pixel</div>
                    </div>
                  }
                  <div className='flex flex-row flex-wrap gap-2 font-bold text-base lg:text-lg'>
                    Level: <div className='font-normal'>{results.genusSpecies}</div>
                  </div>
                </div>
              </div>
              <CircleChart labelPercentage={results.labelPercentage} genus={false} />
            </div>
          </div>
        )}
      </div>
      <div className='w-full flex flex-col items-center pt-4'>
        <TextButton onClick={() => downloadResults()} text={downloading ? "Downloading" : "Download Results ↓"} />
      </div>
    </div>
  )
}

export default ResultsPage