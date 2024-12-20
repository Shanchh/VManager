import React from 'react'
import { Menu } from 'antd';
import { BugOutlined, SettingOutlined, UserOutlined } from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { useLocation, useNavigate } from "react-router-dom"

const OptionList = () => {
    const navigate = useNavigate();
    const item3: MenuProps['items'] = [
        {
            key: 'group-1',
            icon: <UserOutlined />,
            label: '個人頁面',
        },
        {
            key: 'group-2',
            icon: <BugOutlined />,
            label: '管理介面',
        },
        {
            key: 'group-3',
            icon: <SettingOutlined />,
            label: '設定',
            onClick: () => console.log('設定 clicked'),
        },
    ];
    return (
        <Menu
            mode="inline"
            // selectedKeys={[location.pathname]}
            defaultSelectedKeys={['/management/account-view']}
            style={{ height: '100%', borderRight: 0 }}
            items={item3}
        />
    )
}

export default OptionList