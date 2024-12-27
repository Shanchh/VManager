import React, { useState } from 'react';
import { Button, Layout, theme, Grid } from 'antd';
import Header from '../../component/main/Header';
import { Outlet } from 'react-router';
import OptionList from '../../component/main/OptionList';
import MainBreadcrumb from './MainBreadcrumb';
import { Content } from 'antd/es/layout/layout';

const { Sider } = Layout;
const { useBreakpoint } = Grid;

const MainPage: React.FC = () => {
    const [optionListOpen, setOptionListOpen] = useState<boolean>(true);

    const {
        token: { colorBgContainer, borderRadiusLG },
    } = theme.useToken();

    const screens = useBreakpoint();
    const isMobile = !screens.md;

    return (
        <Layout style={{ height: '100vh', width: '100%' }}>
            <Header isMobile={isMobile} optionListOpen={optionListOpen} setOptionListOpen={setOptionListOpen} />
            <Layout>
                <Sider
                    width={200}
                    collapsedWidth={0}
                    collapsed={!optionListOpen}
                    style={{
                        background: colorBgContainer,
                        transition: 'all 0.3s ease',
                        overflow: 'hidden',
                    }}
                >
                    <OptionList />
                </Sider>
                <Layout style={{ padding: '0 24px 24px' }}>
                    <MainBreadcrumb />
                    <Content
                        style={{
                            flex: 1,
                            display: 'flex',
                            flexDirection: 'column',
                            padding: 12,
                            margin: 0,
                            background: colorBgContainer,
                            borderRadius: borderRadiusLG,
                            overflow: 'auto',
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