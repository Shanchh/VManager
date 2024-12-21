import React from 'react'
import { Menu } from 'antd';
import { BugOutlined, SettingOutlined, UserOutlined } from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { useLocation, useNavigate } from "react-router-dom"

const OptionList = () => {
    const navigate = useNavigate();
    const location = useLocation();

    const item3: MenuProps['items'] = [
        {
            key: '/my-profile',
            icon: <UserOutlined />,
            label: '個人頁面',
            onClick: () => navigate("/my-profile"),
        },
        {
            key: 'group-2',
            icon: <BugOutlined />,
            label: '管理功能',
        },
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