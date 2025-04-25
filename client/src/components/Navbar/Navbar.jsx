import React, { useState, useEffect } from 'react';
import { Korotu_Logo_Icon } from '../../assets/images';
import { camera_icon_green, phone_icon_green, drone_icon_green, satellite_icon_green, login, create_account, logout, accounts, coords, help } from '../../assets/icons';
import { backendURL, mainUploadLinks } from '../../constants';

const Navbar = () => {
  const [dropdownCamera, setDropdownCamera] = useState(false);
  const [dropdownMenu, setDropdownMenu] = useState(false);
  const [signedIn, setSignedIn] = useState(false)

  const closeDropdowns = () => {
    setDropdownCamera(false);
  }

  const checkLogin = async () => {
    try {
      const response = await fetch(backendURL + '/api/auth/check', {
        method: 'GET',
        credentials: 'include'
      });

      const result = await response.json();

      if (result) {
        setSignedIn(result.logged_in)
      }
    } catch (error) {
      console.log(error)
    }
  };

  const logMeOut = async () => {
    try {
      const response = await fetch(backendURL + '/api/logout', {
        method: 'POST',
        credentials: 'include'
      });

      if (!response.ok) {
        setAlert({ title: 'Logout failed', body: "There was an error while trying to log you out. Please try again." });
      } else {
        window.location.href = "/";
      }
    } catch (error) {
      setAlert({ title: 'Logout failed', body: "There was an error while trying to log you out. Please try again." });
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    checkLogin()
  }, [])


  return (
    <div className='w-full p-4 sticky top-0 left-0 flex justify-center z-50 mb-4 lg:mb-8'>
      <div onClick={() => closeDropdowns()} className={`${dropdownCamera && "pointer-events-auto"} pointer-events-none w-screen h-screen absolute top-0 left bg-none`} />
      <div className='w-full max-w-[720px] h-min min-h-16 rounded-[24px] shadow-2xl relative overflow-hidden bg-white'>

        <div className={`${dropdownMenu ? 'h-48 pt-24 lg:pt-20' : 'h-0'} w-full bg-white rounded-[24px] ease-in-out duration-300 flex flex-row justify-between overflow-hidden items-start px-4 lg:px-8`}>
          {signedIn ? (
            <>
              <button onClick={() => {
                logMeOut()
              }} className='flex flex-col text-primary self-start gap-2 hover:scale-110 ease-in-out duration-300 w-min text-xs lg:text-base text-center items-center justify-center flex-1'>
                <img src={logout} className='h-6 w-6 lg:h-10 lg:w-10 self-center' />
                LOGOUT
              </button>
              <button onClick={() => {
                closeDropdowns();
                window.location.href = '/accounts/dashboard';
              }} className='flex flex-col text-primary self-start gap-2 hover:scale-110 ease-in-out duration-300 w-min text-xs lg:text-base text-center items-center justify-center flex-1'>
                <img src={accounts} className='h-6 w-6 lg:h-10 lg:w-10 self-center' />
                MY ACCOUNT
              </button>
              <button onClick={() => {
                closeDropdowns();
                window.location.href = '/help';
              }} className='flex flex-col text-primary self-start gap-2 hover:scale-110 ease-in-out duration-300 w-min text-xs lg:text-base text-center items-center justify-center flex-1'>
                <img src={help} className='h-6 w-6 lg:h-10 lg:w-10 self-center' />
                HELP
              </button>
            </>
          ) : (
            <>
              <button onClick={() => {
                closeDropdowns();
                window.location.href = '/login';
              }} className='flex flex-col text-primary self-start gap-2 hover:scale-110 ease-in-out duration-300 w-min text-xs lg:text-base text-center items-center justify-center flex-1'>
                <img src={login} className='h-6 w-6 lg:h-10 lg:w-10 self-center' />
                LOGIN
              </button>
              <button onClick={() => {
                closeDropdowns();
                window.location.href = '/accounts/create';
              }} className='flex flex-col text-primary self-start gap-2 hover:scale-110 ease-in-out duration-300 w-min text-xs lg:text-base text-center items-center justify-center flex-1'>
                <img src={create_account} className='h-6 w-6 lg:h-10 lg:w-10 self-center' />
                CREATE ACCOUNT
              </button>
              <button onClick={() => {
                closeDropdowns();
                window.location.href = '/help';
              }} className='flex flex-col text-primary self-start gap-2 hover:scale-110 ease-in-out duration-300 w-min text-xs lg:text-base text-center items-center justify-center flex-1'>
                <img src={help} className='h-6 w-6 lg:h-10 lg:w-10 self-center' />
                HELP
              </button>
            </>
          )}
        </div>

        <div className={`${dropdownCamera ? 'h-48 pt-24 lg:pt-20' : 'h-0'} w-full bg-white rounded-[24px] ease-in-out duration-300 flex flex-row justify-between px-8 lg:px-4 overflow-hidden items-start`}>
          {mainUploadLinks.map((link, i) => (
            <button key={link + i} onClick={() => {
              closeDropdowns();
              window.location.href = link.link;
            }} className='flex flex-col text-primary self-start gap-2 hover:scale-110 ease-in-out duration-300 w-min text-xs lg:text-base text-center items-center justify-center flex-1'>
              <img src={link.icon} className='h-6 w-6 lg:h-10 lg:w-10 self-center' />
              {link.label}
            </button>
          ))}
        </div>

        <div className='bg-white rounded-[24px] h-16 w-full flex flex-row justify-between absolute top-0 left-0'>
          <button onClick={() => {
            setDropdownMenu(false);
            setDropdownCamera(!dropdownCamera);
          }} className='pl-7 hover:scale-110 ease-in-out duration-300'>
            <img src={camera_icon_green} className='h-10 w-10 lg:h-14 lg:w-14' />
          </button>
          <button onClick={() => {
            closeDropdowns();
            window.location.href = '/';
          }} className='hover:scale-110 ease-in-out duration-300'>
            <img src={Korotu_Logo_Icon} className='h-14 w-14' />
          </button>
          <button onClick={() => {
            setDropdownCamera(false);
            setDropdownMenu(!dropdownMenu);
          }} className='rounded-full flex flex-col justify-center gap-[10px] lg:gap-3 pr-8  hover:scale-110 ease-in-out duration-300'>
            <div className='bg-primary w-8 h-[2px] lg:w-12 lg:h-[3px] self-center rounded-xl' />
            <div className='bg-primary w-8 h-[2px] lg:w-12 lg:h-[3px] self-center rounded-xl' />
            <div className='bg-primary w-8 h-[2px] lg:w-12 lg:h-[3px] self-center rounded-xl' />
          </button>
        </div>

      </div>
    </div>
  )
}

export default Navbar