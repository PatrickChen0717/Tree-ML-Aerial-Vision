import React, { useState, useEffect } from 'react';
import { Logo_Icon } from '../../assets/images';
import { camera_icon_green, login, create_account, logout, accounts, help } from '../../assets/icons';
import { backendURL, mainUploadLinks } from '../../constants';

const Navbar = () => {
  const [signedIn, setSignedIn] = useState(false);

  const checkLogin = async () => {
    try {
      const response = await fetch(`${backendURL}/api/auth/check`, {
        method: 'GET',
        credentials: 'include'
      });
      const result = await response.json();
      setSignedIn(result?.logged_in || false);
    } catch (error) {
      console.log(error);
    }
  };

  const logMeOut = async () => {
    try {
      await fetch(`${backendURL}/api/logout`, {
        method: 'POST',
        credentials: 'include'
      });
      window.location.href = "/";
    } catch (error) {
      console.log(error);
    }
  };

  useEffect(() => {
    checkLogin();
  }, []);

  return (
    <div className='w-full sticky top-0 left-0 z-50 bg-white/90 backdrop-blur-md shadow-md py-2'>
      <div className='max-w-[1152px] mx-auto flex items-center justify-between px-4'>

        {/* Left: Logo */}
        <button onClick={() => window.location.href = '/'} className='flex items-center gap-2 hover:scale-105 transition'>
          <img 
            src={Logo_Icon} 
            alt="Logo" 
            className="h-9 w-9 opacity-100 brightness-75 hue-rotate-150" 
          />

          <span className='text-tertiary font-bold text-xl hidden lg:block'>Tree Aerial Vision</span>
        </button>

        {/* Center: Nav Links */}
        <div className='hidden lg:flex gap-8 items-center text-tertiary font-semibold text-base'>
          {mainUploadLinks.map((link, i) => (
            <button key={i} onClick={() => window.location.href = link.link} className='hover:text-tertiary transition'>
              {link.label}
            </button>
          ))}
          {signedIn && (
            <button onClick={() => window.location.href = '/accounts/dashboard'} className='hover:text-tertiary transition'>
              My Account
            </button>
          )}
          <button onClick={() => window.location.href = '/help'} className='hover:text-tertiary transition'>
            Help
          </button>
        </div>

        {/* Right: Auth */}
        <div className='flex items-center gap-4'>
          {signedIn ? (
            <button onClick={logMeOut} className='px-4 py-2 rounded-full bg-primary text-white hover:bg-tertiary transition'>
              Logout
            </button>
          ) : (
            <>
              <button onClick={() => window.location.href = '/login'} className='px-4 py-2 rounded-full bg-tertiary text-white hover:bg-primary transition'>
                Login
              </button>
              <button onClick={() => window.location.href = '/accounts/create'} className='px-4 py-2 rounded-full border border-tertiary text-tertiary hover:bg-primary hover:text-white transition'>
                Create Account
              </button>
            </>
          )}
        </div>

      </div>
    </div>
  );
}

export default Navbar;
