import { Avatar, Flex, Grid } from 'antd'
import React from 'react'
import QuickActionsCard from '../../component/QuickActionsCard';
import { useAuth } from '../../auth/AuthProvider';
import MobileQuickActionsCard from '../../component/MobileQuickActionsCard';

const { useBreakpoint } = Grid;

const HomePage = () => {
    const { userProfile } = useAuth();

    const screens = useBreakpoint();
    const isMobile = !screens.md;

    return (
        <Flex vertical gap={10}>
            <Flex gap={5} justify='center' align='center' style={{ height: 50, width: '100%' }}>
                <div style={{ fontSize: 30, fontWeight: 'bold' }}>首頁</div>
            </Flex>
            {userProfile?.role === 'admin' || userProfile?.role === 'owner' ? (
                isMobile ? (
                    <MobileQuickActionsCard />
                ) : (
                    <QuickActionsCard />
                )
            ) : null}
        </Flex>
    );
};

export default HomePage;