import React, { useState, useRef, useEffect } from 'react';
import { TextButton, Loader, Toggle, NumberInput } from '../components';
import { backendURL } from '../constants';
import { ResultsPage } from '../sections';
import { info } from '../assets/icons';

const UploadDroneRGB = ({ setAlert }) => {
  const [loading, setLoading] = useState(false);
  const [speciesGenus, setSpeciesGenus] = useState('Species');
  const [estimateRes, setEstimateRes] = useState('');
  const [file, setFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [uploaded, setUploaded] = useState(false);
  const [results, setResults] = useState(null);
  const fileInput = useRef(null);

  const uploadFile = () => {
    if (file == null) {
      setAlert({ body: "Please upload an image file" })
      return;
    }
    if (estimateRes == '') {
      setAlert({ body: "Please enter an estimate resolution" })
      return;
    }

    setUploaded(true);

    setLoading(true);
    const formData = new FormData();
    formData.append('Cred', 'TestCred');
    formData.append('file', file);
    formData.append('genus_species', speciesGenus);
    formData.append('estimate_res', Number(estimateRes));

    fetch(backendURL + '/api/upload/drone/rgb', {
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

        if (speciesGenus == 'Species') {
          setResults({
            image: result.result_image,
            labelPercentage: result.label_percentage,
            shaderGridSpecies: result.shader_grid,
            genusSpecies: result.genus_species,
            estimateRes: result.estimate_res,
          })
        } else {
          setResults({
            image: result.result_image,
            labelPercentage: result.label_percentage,
            shaderGridGenus: result.shader_grid,
            genusSpecies: result.genus_species,
            estimateRes: result.estimate_res,
          })
        }
      })
      .catch(error => alert(error))
      .finally(() => setLoading(false))


    setSpeciesGenus('Species');
    setEstimateRes('');
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
      setSpeciesGenus('Species');
      setResults(null)
    }
  }, [file])


  return (
    <div className='flex-1 flex flex-col justify-center items-center pb-12 lg:pb-16 bg-gradient-to-b from-primary to-accent min-h-screen w-full'>
      {uploaded ? (
        loading ? (
          <div className='absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-white'>
            <div className='relative flex flex-col scale-150 text-sm gap-2'>
              <Loader />
              PROCESSING
            </div>
          </div>
        ) : (
          <div className='pb-16'>
            <ResultsPage results={results} setFile={setFile} setAlert={setAlert} />
          </div>
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
              DRONE GRID CLASSIFICATION
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
              <NumberInput numberInput={estimateRes} setNumberInput={setEstimateRes} title={'Enter a resolution estimation:'} units={'cm/pixel'} />
              <button className='bg-white rounded-full whitespace-normal self-center' onClick={() => setAlert({ title: "Resolution Estimation", body: "Enter an resolution estimation for your uploaded image. The resolution should be in the form of centimeters of space represented by one pixel. The closer your estimate, the more accurate the species classification will be." })}>
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

export default UploadDroneRGB;
