import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './login/LoginPage';

function App() {
  return (
    <div className="className">
      <Router>
        <Routes>
          <Route path="/" element={<LoginPage />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;