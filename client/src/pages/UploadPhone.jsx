import React, { useState, useRef, useEffect } from 'react';
import heic2any from "heic2any";
import { TextButton, Loader, Toggle } from '../components';
import { backendURL } from '../constants';
import { ResultsPage } from '../sections'
import { info } from '../assets/icons'

const UploadPhone = ({ setAlert }) => {
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [uploaded, setUploaded] = useState(false);
  const fileInput = useRef(null);
  const [speciesGenus, setSpeciesGenus] = useState('Species');
  const [partialFull, setPartialFull] = useState('Full');
  const [imagePreview, setImagePreview] = useState(null);
  const [results, setResults] = useState(null);

  const genusArr = [
    'Birch',
    'Oak',
    'Spruce',
    'Maple',
    'Ash',
    'Beech',
    'Larch',
    'Elm',
    'Hophornbeam',
    'Aspen',
    'Pine',
    'Hemlock',
    'Fir',
    'Cedar',
  ];

  const speciesArr = [
    'Yellow Birch',
    'White Birch',
    'Northern Red Oak',
    'White Spruce',
    'Black Spruce',
    'Norway Spruce',
    'Red Spruce',
    'Red Maple',
    'Sugar Maple',
    'White Ash',
    'American Beech',
    'Eastern Larch',
    'American Elm',
    'American Hophornbeam',
    'Quaking Aspen',
    'Eastern White Pine',
    'Red Pine',
    'Eastern Hemlock',
    'Balsam Fir',
    'Northern White Cedar',
  ];

  const genusArrPartial = [
    'Birch',
    'Oak',
    'Spruce',
    'Maple',
    'Ash',
    'Elm',
    'Pine',
    'Fir',
    'Cedar',
  ];

  const speciesArrPartial = [
    'Yellow Birch',
    'White Birch',
    'Northern Red Oak',
    'White Spruce',
    'Black Spruce',
    'Norway Spruce',
    'Red Spruce',
    'Red Maple',
    'Sugar Maple',
    'White Ash',
    'American Elm',
    'Eastern White Pine',
    'Red Pine',
    'Balsam Fir',
    'Northern White Cedar',
  ];

  const allTrees = [
    {
      title: 'Genus',
      list: genusArr
    },
    {
      title: 'Species',
      list: speciesArr
    },
    {
      title: 'Genus Partial',
      list: genusArrPartial
    },
    {
      title: 'Species Partial',
      list: speciesArrPartial
    },
  ]

  const uploadFile = () => {
    if (file == null) {
      setAlert({ body: "Please upload an image file" })
      return;
    }

    setUploaded(true);
    setLoading(true);

    const formData = new FormData();
    formData.append('Cred', 'TestCred');
    formData.append('file', file);
    formData.append('genus', speciesGenus);
    formData.append('partial', partialFull);

    fetch(backendURL + '/api/upload/phone', {
      method: 'POST',
      body: formData,
      credentials: 'include'
    })
      .then(response => {
        if (response.status >= 400 && response.status < 500) {
          setFile(null);
          setAlert({ title: "Uh-oh", body: "We were not able to classify your data. Please try uploading another image." })
          return null;
        } else if (response.status >= 500 && response.status < 600) {
          setFile(null);
          setAlert({ title: "Uh-oh", body: "Something went wrong on our server." })
          return null;
        }

        return response.json();
      })
      .then(result => {
        if (result === null) return;
        
        if (result.combined && result.predictions) {
          setResults({
            predictions: result.predictions,
            image: result.combined,
            // prediction: result.prediction,
            patches: result.patches,
            resizedHeight: result.resized_height,
            resizedWidth: result.resized_width,
            plainImage: result.raw_image,
            genus: result.genus,
            partial: result.partial
          })
        } else {
          setAlert({
            title: 'We were unable to classify your image',
            body: 'It seems that the image you uploaded can not be classified. Ensure that you are standing ideally 1-2 meters from the tree and the tree trunk takes up as much of the image as possible.'
          });
          setFile(null);
        }

      })
      .catch(error => setAlert({
        title: "Alert",
        body: error
      }))
      .finally(() => setLoading(false))

    setSpeciesGenus('Species');
    setPartialFull('Full');
  };

  const handleFileChange = async (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const processedFile = await convertAndResizeImage(e.target.files[0]);
      setFile(processedFile);

      const imageUrl = URL.createObjectURL(processedFile);
      setImagePreview(imageUrl);
    }
  };

  const convertAndResizeImage = async (file, maxWidth = 1600, maxHeight = 1600, quality = 0.8) => {
    return new Promise(async (resolve) => {
      if (file.type === "image/heic" || file.name.endsWith(".heic")) {
        try {
          file = new File([
            await heic2any({ blob: file, toType: "image/jpeg" })
          ], file.name.replace(/\.heic$/, ".jpg"), { type: "image/jpeg" });
        } catch (error) {
          console.error("HEIC conversion error:", error);
          resolve(file);
        }
      }

      const reader = new FileReader();
      reader.readAsDataURL(file);

      reader.onload = (event) => {
        const img = new Image();
        img.src = event.target.result;

        img.onload = () => {
          let width = img.width;
          let height = img.height;

          if (width > maxWidth || height > maxHeight) {
            const aspectRatio = width / height;
            if (width > height) {
              width = maxWidth;
              height = maxWidth / aspectRatio;
            } else {
              height = maxHeight;
              width = maxHeight * aspectRatio;
            }
          }

          const canvas = document.createElement("canvas");
          canvas.width = width;
          canvas.height = height;
          const ctx = canvas.getContext("2d");
          ctx.drawImage(img, 0, 0, width, height);

          canvas.toBlob((blob) => {
            resolve(new File([blob], "processed.jpg", { type: "image/jpeg" }));
          }, "image/jpeg", quality);
        };
      };
    });
  };

  useEffect(() => {
    if (!file) {
      setUploaded(false);
    }
  }, [file])

  return (
    <div className='flex-1 flex flex-col justify-center items-center pb-12 lg:pb-16'>
      {uploaded ? (
        loading ? (
          <div className='absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-white'>
            <div className='relative flex flex-col scale-150 text-sm gap-2'>
              <Loader />
              PROCESSING
            </div>
          </div>
        ) : (
          <ResultsPage setFile={setFile} setAlert={setAlert} results={results} />
        )
      ) : (
        <div className='w-min h-min flex flex-col justify-center'>
          <input
            type="file"
            name='file'
            ref={fileInput}
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
          <div className='self-center whitespace-nowrap group ease-in-out duration-300 flex flex-col justify-center gap-16'>
            <div className='flex text-4xl text-white font-bold whitespace-nowrap h-min w-min self-center z-10 ease-in-out duration-500 pointer-events-none'>
              PHONE
            </div>
            <div className='flex flex-col gap-6'>
              {file ? (
                <>
                  <div className='bg-primary self-center rounded-3xl overflow-hidden border-white border-[3px]'>
                    <img src={imagePreview} alt="" className="max-w-32 max-h-32" />
                  </div>
                  <TextButton onClick={() => fileInput.current.click()} text={"Select file"} />
                </>
              ) : (
                <TextButton onClick={() => fileInput.current.click()} text={"Select file"} />
              )}
              <Toggle setState={setSpeciesGenus} state={speciesGenus} option1={'Species'} option2={'Genus'} />
              <Toggle setState={setPartialFull} state={partialFull} option1={'Full'} option2={'Partial'} />
              <button className='bg-white rounded-full whitespace-normal self-center' onClick={() => setAlert({
                list: {
                  title: `You are currently using ${speciesGenus == 'Species' ? (partialFull == 'Full' ? allTrees[1].title : allTrees[3].title) : (partialFull == 'Full' ? allTrees[0].title : allTrees[2].title)} which includes:`,
                  list: speciesGenus == 'Species' ? (partialFull == 'Full' ? allTrees[1].list : allTrees[3].list) : (partialFull == 'Full' ? allTrees[0].list : allTrees[2].list)
                }, title: "Full vs. Partial", body: "When set to full, your uploaded image will be classified between all the species or genuses we support. When set to partial, your uploaded image will only be classified between the best performing species or genuses that we support. Flip the toggles under the image upload to change which set to use."
              })}>
                <img src={info} className='w-12 h-12' />
              </button>
            </div>
            <button onClick={() => uploadFile()} className='self-center bg-black/50 hover:bg-white border-white border-[3px] text-white hover:text-primary text-xl font-semibold ease-in-out duration-300 px-4 py-2 rounded-3xl shadow-3xl hover:scale-125'>
              CLASSIFY IMAGE
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadPhone;