import React, { useState, useEffect } from 'react'
import { backendURL } from '../constants';
import { dashboardLinks } from '../constants';
import { DashboardCard } from '../components';

const Dashboard = () => {
  const [user, setUser] = useState('');

  useEffect(() => {
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
      .catch(error => console.log(error))
  }, [])

  return (
    <div className='w-full flex flex-col justify-center items-center gap-8'>
      {user && (
        <>
          <div className="whitespace-nowrap font-bold text-3xl lg:text-6xl text-white max-w-[90vw] lg:max-w-[1152px] text-start w-full">
            Hello, {user}!
          </div>
          <div className='w-full max-w-[90vw] lg:max-w-[1152px] flex flex-col border-[3px] border-white bg-black/50 shadow-3xl p-8 lg:p-16 rounded-3xl text-white gap-8 justify-center items-center'>
            {dashboardLinks.map((link, i) => (
              <DashboardCard key={link + i} link={link} />
            ))}
          </div>
        </>
      )}
    </div>
  )
}

export default Dashboard
