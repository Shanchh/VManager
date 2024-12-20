import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/login/LoginPage';
import AuthProvider from './auth/AuthProvider';

function App() {
  return (
    <div className="className">
      <Router>
        <AuthProvider>
          <Routes>
            <Route path="/Login" element={<LoginPage />} />
          </Routes>
        </AuthProvider>
      </Router>
    </div>
  );
}

export default App;