import React, { useState } from 'react';
import LoginForm from './LoginForm'
import RegisterForm from './RegisterForm';

const LoginFormPage: React.FC = () => {
  const [isRegister, setIsRegister] = useState(false);

  return (
    <div
      style={{
        height: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        backgroundColor: '#ffffff',
      }}
    >
      {isRegister ? (
        <RegisterForm onLoginClick={() => setIsRegister(false)} />
      ) : (
        <LoginForm onRegisterClick={() => setIsRegister(true)} />
      )}
    </div>
  );
};

export default LoginFormPage;