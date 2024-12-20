import React from 'react';
import { Button, Layout, theme } from 'antd';
import Header from '../../component/main/Header';
import { Outlet } from 'react-router';
import OptionList from '../../component/main/OptionList';
import { get_my_profile } from '../../api/ProcessApi';

const { Sider } = Layout;

const MainPage: React.FC = () => {
    const {
        token: { colorBgContainer },
    } = theme.useToken();

    const test = () => {
        const a = get_my_profile();
        console.log(a);
    }

    return (
        <Layout style={{ height: '100vh', width: '100%' }}>
            <Header />
            <Layout>
                <Sider width={200} style={{ background: colorBgContainer }}>
                    <OptionList />
                </Sider>
                <Button onClick={() => test()}></Button>
            </Layout>
        </Layout>
    );
};

export default MainPage;