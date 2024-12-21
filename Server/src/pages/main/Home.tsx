import React from 'react';
import { Button, Layout, theme } from 'antd';
import Header from '../../component/main/Header';
import { Outlet } from 'react-router';
import OptionList from '../../component/main/OptionList';
import MainBreadcrumb from './MainBreadcrumb';
import { Content } from 'antd/es/layout/layout';

const { Sider } = Layout;

const MainPage: React.FC = () => {
    const {
        token: { colorBgContainer, borderRadiusLG },
    } = theme.useToken();

    return (
        <Layout style={{ height: '100vh', width: '100%' }}>
            <Header />
            <Layout>
                <Sider width={200} style={{ background: colorBgContainer }}>
                    <OptionList />
                </Sider>
                <Layout style={{ padding: '0 24px 24px' }}>
                    <MainBreadcrumb />
                    <Content
                        style={{
                            flex: 1,
                            padding: 24,
                            margin: 0,
                            background: colorBgContainer,
                            borderRadius: borderRadiusLG,
                        }}
                    >
                        <Outlet />
                    </Content>
                </Layout>
            </Layout>
        </Layout>
    );
};

export default MainPage;