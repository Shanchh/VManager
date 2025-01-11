import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/login/LoginPage';
import AuthProvider from './auth/AuthProvider';
import Home from './pages/main/Home';
import ProtectedRoute from './auth/ProtectedRoute';
import MyProfile from './pages/content/MyProfile';
import Setting from './pages/main/Setting';
import UserManage from './pages/content/UserManage';
import OnlineManage from './pages/content/OnlineManage';
import HomePage from './pages/content/HomePage';
import ServerLogsPage from './pages/content/ServerLogsPage';
import ManageDashboard from './pages/content/ManageDashboard';
import SearchUserLogs from './pages/content/SearchUserLogs';

function App() {
  return (
    <div className="className">
      <Router>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />

            <Route element={<ProtectedRoute />}>
              <Route path="/" element={<Home />}>
                <Route path="/" element={<HomePage />} />
                <Route path="/my-profile" element={<MyProfile />} />
                
                <Route path="/management/dashboard" element={<ManageDashboard />} />
                <Route path="/management/online-manage" element={<OnlineManage />} />
                <Route path="/management/user-manage" element={<UserManage />} />
                
                <Route path="/backend-interface/server-logs" element={<ServerLogsPage />} />
                <Route path="/backend-interface/search-user-logs" element={<SearchUserLogs />} />
                
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