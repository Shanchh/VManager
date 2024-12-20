import React from 'react';
import { Button, Dropdown } from 'antd';
import type { MenuProps } from 'antd';
import { useAuth } from '../../auth/AuthProvider';
import { auth } from '../../auth/FirebaseConfig';

const UserShow = () => {
    const { userProfile, setUser } = useAuth();

    const handleLogout = () => {
        auth.signOut().then(() => {
            setUser(null);
            window.location.reload();
        }).catch((error) => {
            console.error("登出失敗: ", error);
        });
    };

    const items: MenuProps['items'] = [
        {
            key: '1',
            label: (
                <div
                    onClick={handleLogout}
                    style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}
                >
                    Logout 登出
                </div>
            ),
        },
    ];

    return (
        <Dropdown menu={{ items }} placement="bottomRight" arrow>
            <Button type="text">
                <div style={{ fontFamily: 'Roboto, sans-serif', fontSize: '20px' }}>
                    {userProfile?.nickname || userProfile?.email || 'Loading'}
                </div>
            </Button>
        </Dropdown>
    );
};

export default UserShow;