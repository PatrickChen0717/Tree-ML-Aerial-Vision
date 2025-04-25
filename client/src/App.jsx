import React, { useState } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { Main, UploadPhone, UploadDroneRGB, Login, CreateAccount, Dashboard, Satellite, Help, UploadDroneSegment, History, Drone, UploadDroneLidar } from './pages';
import { Navbar, Footer, Alert } from './components';
import { help, helpGround, helpDroneRGB, helpCoordinates } from './constants';

const App = () => {
  const [alert, setAlert] = useState(null);

  return (
    <BrowserRouter>

      <div className='min-h-[100vh] h-auto bg-primary font-montserrat flex flex-col justify-between'>
        <div className='flex-1 relative flex flex-col justify-start items-center'>
          <Navbar />

          {alert && (
            <Alert alert={alert} setAlert={setAlert} />
          )}

          <Routes>
            <Route path="/" element={<Main />}></Route>

            <Route path="/upload/phone" element={<UploadPhone setAlert={setAlert} />}></Route>
            <Route path="/upload/drone" element={<Drone setAlert={setAlert} />}></Route>
            <Route path="/upload/drone/rgb" element={<UploadDroneRGB setAlert={setAlert} />}></Route>
            <Route path="/upload/drone/seg" element={<UploadDroneSegment setAlert={setAlert} />}></Route>
            <Route path="/upload/drone/lidar" element={<UploadDroneLidar setAlert={setAlert} />}></Route>
            <Route path="/upload/satellite" element={<Satellite setAlert={setAlert} />}></Route>

            <Route path="/help" element={<Help title={"What do you need help with?"} list={help} />}></Route>
            <Route path="/help/ground" element={<Help title={"Help for Phone Classification"} list={helpGround} />}></Route>
            <Route path="/help/droneRGB" element={<Help title={"Help for Drone RGB Classification"} list={helpDroneRGB} />}></Route>
            <Route path="/help/satellite" element={<Help title={"Help for Satellite Classification"} list={helpCoordinates} />}></Route>

            <Route path="/login" element={<Login setAlert={setAlert} />}></Route>
            <Route path="/accounts/create" element={<CreateAccount setAlert={setAlert} />}></Route>
            <Route path="/accounts/dashboard" element={<Dashboard />}></Route>
            <Route path="/accounts/history" element={<History setAlert={setAlert} />}></Route>
          </Routes>

        </div>

        {/* <Footer /> */}
      </div>

    </BrowserRouter>
  );
};

export default App;