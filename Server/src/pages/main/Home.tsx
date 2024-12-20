import React from 'react';
import { Button, message } from 'antd';
import { auth } from '../../auth/FirebaseConfig';
import { signOut } from 'firebase/auth';

const Home: React.FC = () => {
    const logout = async () => {
        try {
            await signOut(auth); // 调用 Firebase 的登出方法
            message.success('登出成功！');
        } catch (error) {
            console.error('登出失败:', error);
            message.error('登出失败，请稍后再试！');
        }
    };

    return (
        <Button type="primary" onClick={logout}>
            登出
        </Button>
    );
};

export default Home;