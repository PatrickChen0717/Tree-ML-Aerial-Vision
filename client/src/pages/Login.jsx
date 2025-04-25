import React, { useState } from 'react';
import { TextButton, Loader } from '../components';
import { backendURL } from '../constants';

const Login = ({ setAlert }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!username || !password) {
      setAlert({ body: "Please make sure all login fields are filled." });
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('Username', username);
      formData.append('Password', password);

      const response = await fetch(backendURL + '/api/login', {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });

      const result = await response.json();

      if (!response.ok) {
        setAlert({ title: 'Login failed', body: "Either you username or password are incorrect. Please try again." });
      } else {
        window.location.href = "/accounts/dashboard";
      }
    } catch (error) {
      setAlert({ title: 'Login failed', body: "There was an error while trying to log you in. Please try again." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className='flex justify-center items-center absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2'>
      <div className='bg-black/50 p-8 rounded-3xl shadow-2xl flex flex-col items-center gap-6 min-w-[80vw] lg:min-w-[30vw] border-[3px] border-white'>
        <h2 className='text-3xl lg:text-4xl font-bold text-white'>LOGIN</h2>
        <input
          type='username'
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
        <TextButton onClick={handleLogin} text='LOGIN' />
        {loading && <Loader />}
      </div>
    </div>
  );
};

export default Login;
