import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/login/LoginPage';
import AuthProvider from './auth/AuthProvider';
import Home from './pages/main/Home';
import ProtectedRoute from './auth/ProtectedRoute';
import MyProfile from './pages/content/MyProfile';
import Setting from './pages/main/Setting';

function App() {
  return (
    <div className="className">
      <Router>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />

            <Route element={<ProtectedRoute />}>
              <Route path="/" element={<Home />}>
                <Route path="/my-profile" element={<MyProfile />} />
                
                <Route path="/setting" element={<Setting />} />
              </Route>
            </Route>
          </Routes>
        </AuthProvider>
      </Router>
    </div>
  );
}

export default App;