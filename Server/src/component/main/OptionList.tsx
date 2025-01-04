import React from 'react'
import { Menu } from 'antd';
import { BugOutlined, SettingOutlined, UserOutlined, SolutionOutlined, WifiOutlined, CloudServerOutlined, LockOutlined, DashboardOutlined } from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { useLocation, useNavigate } from "react-router-dom"
import { useAuth } from '../../auth/AuthProvider';

const OptionList = () => {
    const navigate = useNavigate();
    const location = useLocation();

    const { userProfile } = useAuth();

    const item3: MenuProps['items'] = [
        {
            key: '/my-profile',
            icon: <UserOutlined />,
            label: '個人頁面',
            onClick: () => navigate("/my-profile"),
        },
        ...(userProfile?.role === 'owner' || userProfile?.role === 'admin' ? [
            {
                key: 'group-2',
                icon: <BugOutlined />,
                label: '管理功能',
                children: [
                    { key: '/management/dashboard', label: '儀表板', icon: <DashboardOutlined />, onClick: () => navigate("/management/dashboard") },
                    { key: '/management/online-manage', label: '線上裝置管理', icon: <WifiOutlined />, onClick: () => navigate("/management/online-manage") },
                    { key: '/management/user-manage', label: '帳號管理', icon: <SolutionOutlined />, onClick: () => navigate("/management/user-manage") },
                ],
            }
        ] : []),
        ...(userProfile?.role === 'owner' ? [
            {
                key: '/backend-interface',
                icon: <LockOutlined />,
                label: '後臺功能',
                children: [
                    { key: '/backend-interface/server-logs', label: '運行日誌', icon: <CloudServerOutlined />, onClick: () => navigate("/backend-interface/server-logs") },
                ],
            },
        ] : []),
        {
            key: '/setting',
            icon: <SettingOutlined />,
            label: '設定',
            onClick: () => navigate("/setting"),
        },
    ];
    return (
        <Menu
            mode="inline"
            selectedKeys={[location.pathname]}
            defaultSelectedKeys={['/my-profile']}
            style={{ height: '100%', borderRight: 0 }}
            items={item3}
        />
    )
}

export default OptionList