import React from 'react'
import { TextButton } from '../components'
import { backendURL } from '../constants'
import { garbage_icon } from '../assets/icons'

const HistoryCard = ({ item, setSelected, getHistory }) => {
  const types = {
    "ground": "Phone Classification",
    "drone_rgb": "Drone RGB Classification",
    "drone_coord": "Satellite Classification", 
    "drone_segment": "Drone Segmented Classification", 
  }

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp * 1000);

    const options = {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    };

    return date.toLocaleString('en-US', options);
  }

  const deleteSingleHistory = () => {
    fetch(`${backendURL}/api/history/delete_one?type=${item.type}&timestamp=${item.timestamp}`, {
      method: 'DELETE',
      credentials: 'include'
    })
      .then(response => response.json())
      .then(result => {
        getHistory()
      })
      .catch(error => console.error("Error deleting history item:", error));
  };

  return (
    <div className='w-full flex flex-col gap-4 lg:gap-0 lg:flex-row justify-between items-center bg-white/80 border-[3px] border-black text-black p-4 rounded-xl'>
      <div className='flex flex-col lg:flex-row gap-4 w-full lg:w-2/3 self-center items-center justify-center'>
        <div className='w-full lg:w-1/2 text-center lg:text-start font-bold text-xl'>
          {types[item.type]}
        </div>
        <div className='w-full lg:w-1/2 text-center lg:text-start font-bold text-base lg:text-xl'>
          {formatTimestamp(item.timestamp)}
        </div>
      </div>
      <div className='w-full lg:w-1/3 flex flex-row justify-center lg:justify-end items-center gap-4 lg:gap-8 flex-wrap'>
        <TextButton text={'View Results'} onClick={() => setSelected(item)} />
        <button onClick={deleteSingleHistory} className='flex flex-col justify-center items-center'>
          <img src={garbage_icon} className='w-8 h-8 brightness-0 hover:scale-125 ease-in-out duration-300' />
        </button>
      </div>
    </div>
  )
}

export default HistoryCard