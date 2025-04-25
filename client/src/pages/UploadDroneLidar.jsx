import React, { useState, useRef, useEffect } from 'react';
import { TextButton, Loader, Toggle, NumberInput } from '../components';
import { backendURL } from '../constants';
import { ResultsPage } from '../sections';
import { info } from '../assets/icons';

const UploadDroneLidar = ({ setAlert }) => {
  const [loading, setLoading] = useState(false);
  const [nPoints, setNPoints] = useState('');
  const [file, setFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [uploaded, setUploaded] = useState(false);
  const [results, setResults] = useState(null);
  const fileInput = useRef(null);

  const uploadFile = () => {
    if (file == null) {
      alert("Please upload an image file")
      return;
    }

    setUploaded(true);

    setLoading(true);
    const formData = new FormData();
    formData.append('Cred', 'TestCred');
    formData.append('file', file);
    formData.append('n_points', Number(nPoints));

    fetch(backendURL + '/api/upload/drone/lidar/single_tree', {
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
      .then(async result => {
        console.log(result)
        if (result.success) {
          setResults({
            prediction: result.prediction
          });
        } else {
          setAlert({ title: "Uh-oh", body: "We were not able to classify your data. Please try uploading another file." });
          setFile(null);
        }
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

  useEffect(() => {
    if (!file) {
      setUploaded(false);
      setNPoints('')
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
              DRONE LiDAR CLASSIFICATION
            </div>
            <div className='flex flex-col gap-6'>
              {file ? (
                <div className='bg-black/50 text-white px-16 py-3 rounded-3xl border-white border-[3px] font-semibold text-center max-w-xs truncate self-center'>
                  {file.name}
                </div>
              ) : (
                <TextButton onClick={() => fileInput.current.click()} text={"Select file"} />
              )}
              <NumberInput numberInput={nPoints} setNumberInput={setNPoints} title={'Enter the number of sample points:'} integersOnly={'True'} />
            </div>
            <button onClick={() => uploadFile()} className='self-center bg-primary hover:bg-white border-white border-[3px] text-white hover:text-primary text-xl font-semibold ease-in-out duration-300 px-4 py-2 rounded-3xl shadow-3xl hover:scale-125'>
              CLASSIFY FILE
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadDroneLidar;
