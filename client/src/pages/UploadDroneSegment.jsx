import React, { useState, useRef, useEffect } from 'react';
import { TextButton, Loader, Toggle, NumberInput } from '../components';
import { backendURL } from '../constants';
import { ResultsPage } from '../sections';
import { info } from '../assets/icons';

const UploadDroneSegment = ({ setAlert }) => {
  const [loading, setLoading] = useState(false);
  const [scaleFactor, setScaleFactor] = useState('');
  const [file, setFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [uploaded, setUploaded] = useState(false);
  const [results, setResults] = useState(null);
  const fileInput = useRef(null);

  const uploadFile = () => {
    setScaleFactor('');

    if (file == null) {
      alert("Please upload an image file")
      return;
    }
    if (scaleFactor == '') {
      alert("Please enter an estimate scale factor")
      return;
    }

    setUploaded(true);

    setLoading(true);
    const formData = new FormData();
    formData.append('Cred', 'TestCred');
    formData.append('file', file);
    formData.append('scale_factor', scaleFactor);

    fetch(backendURL + '/api/upload/drone/seg', {
      method: 'POST',
      body: formData,
      credentials: 'include'
    })
      .then(response => {
        if (response.status >= 400 && response.status < 500) {
          setFile(null);
          setAlert({ title: "Uh-oh", body: "We were not able to segment your data. Please try uploading another image." })
          return null;
        } else if (response.status >= 500 && response.status < 600) {
          setFile(null);
          setAlert({ title: "Uh-oh", body: "Something went wrong on our server." })
          return null;
        }

        return response.json();
      })
      .then(async result => {
        if (result === null) return;
        
        const final_image = await replaceBlackWithTransparent(result.result_image);
        setResults({
          imageBG: result.original_image,
          imageFG: final_image,
          data: result.maps
        });
      })
      .catch(error => alert(error.message))
      .finally(() => setLoading(false))
  };

  const handleFileChange = async (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const processedFile = e.target.files[0]
      setFile(processedFile);

      const imageUrl = URL.createObjectURL(processedFile);
      setImagePreview(imageUrl);
    }
  };

  const replaceBlackWithTransparent = async (imageInput) => {
    const blob = base64ToBlob(imageInput);
    const img = await loadImageFromBlob(blob);

    const canvas = document.createElement('canvas');
    canvas.width = img.width;
    canvas.height = img.height;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(img, 0, 0);

    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;

    for (let i = 0; i < data.length; i += 4) {
      const [r, g, b, a] = [data[i], data[i + 1], data[i + 2], data[i + 3]];
      if (r === 0 && g === 0 && b === 0 && a === 255) {
        data[i + 3] = 0;
      }
    }

    ctx.putImageData(imageData, 0, 0);

    return canvas.toDataURL("image/png");
  };

  const base64ToBlob = (base64Input) => {
    let base64String, mimeType;

    if (base64Input.startsWith('data:')) {
      const [header, data] = base64Input.split(',');
      const mimeMatch = header.match(/data:(.*?);base64/);
      if (!mimeMatch) throw new Error('Invalid base64 header');
      mimeType = mimeMatch[1];
      base64String = data;
    } else {
      mimeType = 'image/png';
      base64String = base64Input;
    }

    const byteCharacters = atob(base64String);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    return new Blob([byteArray], { type: mimeType });
  }

  const loadImageFromBlob = (blob) => {
    return new Promise((resolve, reject) => {
      const url = URL.createObjectURL(blob);
      const img = new Image();
      img.onload = () => {
        URL.revokeObjectURL(url);
        resolve(img);
      };
      img.onerror = reject;
      img.src = url;
    });
  }

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
          <ResultsPage results={results} setFile={setFile} setAlert={setAlert} />
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
              DRONE SEGMENTATION
            </div>
            <div className='flex flex-col gap-6'>
              {file ? (
                <div className='bg-primary self-center rounded-3xl overflow-hidden border-white border-[3px]'>
                  <img src={imagePreview} alt="" className="max-w-32 max-h-32" />
                </div>
              ) : (
                <TextButton onClick={() => fileInput.current.click()} text={"Select file"} />
              )}
              <NumberInput numberInput={scaleFactor} setNumberInput={setScaleFactor} title={'Enter a resolution estimation:'} units={'cm/pixel'} />
              <button className='bg-white rounded-full whitespace-normal self-center' onClick={() => setAlert({ title: "Resolution Estimation", body: "Enter an resolution estimation for your uploaded image. The resolution should be in the form of centimeters of space represented by one pixel. The closer your estimate, the more accurate the species classification will be." })}>
                <img src={info} className='w-12 h-12' />
              </button>
            </div>
            <button onClick={() => uploadFile()} className='self-center bg-primary hover:bg-white border-white border-[3px] text-white hover:text-primary text-xl font-semibold ease-in-out duration-300 px-4 py-2 rounded-3xl shadow-3xl hover:scale-125'>
              SEGMENT IMAGE
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadDroneSegment;
