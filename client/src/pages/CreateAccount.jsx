import React, { useState } from 'react';
import { TextButton, Loader } from '../components';
import { backendURL } from '../constants';

const CreateAccount = ({ setAlert }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [created, setCreated] = useState(false);

  const handleCreateAccount = async () => {
    if (!username || !password || !confirmPassword) {
      setAlert({ body: "Please make sure all account creation fields are filled." });
      return;
    }
    if (password !== confirmPassword) {
      setAlert({ title: 'Error', body: "Passwords do not match. Please try again." });
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('Username', username);
      formData.append('Password', password);

      const response = await fetch(backendURL + '/api/account/create', {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });

      const result = await response.json();

      if (!response.ok) {
        setAlert({ title: 'Account Creation Failed', body: result.message || "There was an error creating your account. Please try again." });
      } else {
        setCreated(true)
      }
    } catch (error) {
      setAlert({ title: 'Account Creation Failed', body: "There was an error while trying to create your account. Please try again." });
    } finally {
      setLoading(false);
    }
  };

  const goToLogin = () => {
    window.location.href = "/login";
  }

  return (
    <div className='flex justify-center items-center absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2'>
      {created ? (
        <div className='flex flex-col items-center gap-12'>
          <div className='font-bold text-white text-2xl lg:text-4xl w-min'>
            CONGRATULATIONS!
            <div className='font-normal text-lg lg:text-xl text-center pt-6'>
              You have created your very own Korotu account. Click the button below to login.
            </div>
          </div>
          <TextButton onClick={goToLogin} text='GO TO LOGIN PAGE' />
        </div>
      ) : (
        <div className='bg-black/50 p-8 rounded-3xl shadow-2xl flex flex-col items-center gap-6 min-w-[80vw] lg:min-w-[30vw] border-[3px] border-white'>
          <h2 className='text-3xl lg:text-4xl font-bold text-white text-center'>CREATE ACCOUNT</h2>
          <input
            type='text'
            placeholder='Username'
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className='w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary'
          />
          <input
            type='password'
            placeholder='Password'
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className='w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary'
          />
          <input
            type='password'
            placeholder='Confirm Password'
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className='w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary'
          />
          <TextButton onClick={handleCreateAccount} text='CREATE ACCOUNT' />
          {loading && <Loader />}
        </div>
      )}
    </div>
  );
};

export default CreateAccount;
