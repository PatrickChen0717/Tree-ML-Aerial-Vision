import React, { useState, useEffect } from 'react'
import { backendURL } from '../constants';
import { HistoryCard, TextButton } from '../components';
import { Loader } from '../components';
import { ResultsPage } from '../sections';

const History = ({ setAlert }) => {
  const [user, setUser] = useState('');
  const [history, setHistory] = useState({});
  const [result, setResult] = useState(null);
  const [selected, setSelected] = useState(null);

  const getHistory = () => {
    fetch(backendURL + '/api/auth/check', {
      method: 'GET',
      credentials: 'include'
    })
      .then(response => response.json())
      .then(result => {
        return new Promise((resolve, reject) => {
          if (result && result.logged_in) {
            setUser(result.user);
            resolve()
          }
          else {
            window.location.href = "/";
            reject('user not logged in');
          }
        })
      })
      .then(() => fetch(backendURL + '/api/history', {
        method: 'GET',
        credentials: 'include'
      }))
      .then(response => response.json())
      .then(result => {
        setHistory({ ...result })
      })
      .catch(error => console.log(error))
  }

  const fetchSelected = () => {
    fetch(backendURL + '/api/history?' + new URLSearchParams({
      type: selected.type,
      timestamp: selected.timestamp,
    }).toString())
      .then(response => response.json())
      .then(async result => {
        if (result.original_image && result.result_image && result.maps) {
          result.result_image = await replaceBlackWithTransparent(result.result_image);
        }
        setResult(result)
      })
  }

  const deleteAllHistory = () => {
    fetch(`${backendURL}/api/history/delete_all`, {
      method: 'DELETE',
      credentials: 'include'
    })
      .then(response => response.json())
      .then(result => {
        getHistory()
      })
      .catch(error => console.error("Error deleting all history items:", error));
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
    if (selected) {
      fetchSelected()
    } else {
      setResult(null)
    }
  }, [selected])

  useEffect(() => {
    getHistory()
  }, [])

  return (
    <div className='w-full flex flex-col justify-center items-center gap-8 pb-16'>
      {user && (
        <>
          {history != null &&
            <div className={`w-full max-w-[90vw] flex flex-col border-[3px] border-white bg-black/50 shadow-3xl p-8 lg:p-16 rounded-3xl text-white gap-8 justify-center items-center`}>
              {selected ? (
                <>
                  {result ? (
                    <>
                      {result.combined && result.predictions && (
                        <ResultsPage setFile={setSelected} setAlert={setAlert} results={{
                          predictions: result.predictions,
                          image: result.combined,
                          plainImage: result.raw_image
                        }} />
                      )}
                      {result.result_image && result.label_percentage && result.shader_grid && result.genus_species == "Species" && (
                        <ResultsPage setFile={setSelected} setAlert={setAlert} results={{
                          image: result.result_image,
                          labelPercentage: result.label_percentage,
                          shaderGridSpecies: result.shader_grid
                        }} />
                      )}
                      {result.result_image && result.label_percentage && result.shader_grid && result.genus_species == "Genus" && (
                        <ResultsPage setFile={setSelected} setAlert={setAlert} results={{
                          image: result.result_image,
                          labelPercentage: result.label_percentage,
                          shaderGridGenus: result.shader_grid
                        }} />
                      )}
                      {result.original_image && result.result_image && result.maps && (
                        <ResultsPage setFile={setSelected} setAlert={setAlert} results={{
                          imageBG: result.original_image,
                          imageFG: result.result_image,
                          data: result.maps
                        }} />
                      )}
                    </>
                  ) : (
                    <Loader />
                  )}
                </>
              ) : (
                <>
                  <div className='w-full text-start font-bold text-4xl'>
                    HISTORY
                  </div>
                  {history.no_history ? (
                    <div className='text-white text-lg'>
                      You do not have any history.
                    </div>
                  ) : (
                    <>
                      <div className='w-full flex flex-col gap-2 justify-center items-center'>
                        {Object.values(history).slice().reverse().map((classification, i) => (
                          <HistoryCard item={classification} setSelected={setSelected} getHistory={getHistory} />
                        ))}
                      </div>
                      <TextButton onClick={deleteAllHistory} text={"Delete All History"} />
                    </>
                  )}
                </>
              )}
            </div>
          }
        </>
      )}
    </div>
  )
}

export default History