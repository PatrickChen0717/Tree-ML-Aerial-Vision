import React, { useState, useRef, useEffect } from 'react';
import { TextButton, Loader, Toggle, NumberInput } from '../components';
import { backendURL } from '../constants';
import { ResultsPage } from '../sections';
import { info } from '../assets/icons';

const Satellite = ({ setAlert }) => {
  const [loading, setLoading] = useState(false);
  const [speciesGenus, setSpeciesGenus] = useState('Species');
  const [lat, setLat] = useState('');
  const [long, setLong] = useState('');
  const [uploaded, setUploaded] = useState(false);
  const [results, setResults] = useState(null);

  const uploadFile = () => {
    setUploaded(true);

    setLoading(true);
    const formData = new FormData();
    formData.append('Cred', 'TestCred');
    formData.append('genus_species', speciesGenus);
    formData.append('latitude', Number(lat));
    formData.append('longitude', Number(long));

    fetch(backendURL + '/api/upload/drone/coord', {
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
    setLat('');
    setLong('');
  };

  useEffect(() => {
    if (!uploaded) {
      setSpeciesGenus('Species');
      setLat('');
      setLong('');
      setResults(null)
    }
  }, [uploaded])


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
            <ResultsPage results={results} setFile={setUploaded} setAlert={setAlert} />
          </div>
        )
      ) : (
        <div className='w-min h-min flex flex-col justify-center'>
          <div className='self-center whitespace-nowrap group ease-in-out duration-300 flex flex-col justify-center gap-16'>
            <div className='flex text-4xl text-white font-bold h-min w-min self-center z-10 ease-in-out duration-500 pointer-events-none whitespace-normal text-center'>
              SATELLITE
            </div>
            <div className='flex flex-col gap-6'>
              <Toggle setState={setSpeciesGenus} state={speciesGenus} option1={'Species'} option2={'Genus'} />

              {/* New horizontal layout for Latitude + Longitude */}
              <div className='flex flex-row flex-wrap gap-4 justify-center'>
                <NumberInput numberInput={lat} setNumberInput={setLat} title={'Enter a latitude:'} />
                <NumberInput numberInput={long} setNumberInput={setLong} title={'Enter a longitude:'} />
              </div>
            </div>
            <button onClick={() => uploadFile()} className='self-center bg-black/50 hover:bg-white border-white border-[3px] text-white hover:text-primary text-xl font-semibold ease-in-out duration-300 px-4 py-2 rounded-3xl shadow-3xl hover:scale-125'>
              CLASSIFY
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default Satellite