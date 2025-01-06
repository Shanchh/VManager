import { Card, Flex } from 'antd'
import React from 'react'
import { ThunderboltOutlined } from '@ant-design/icons';
import OneClickOperationBtn from './OneClickOperationBtn';
import OneClickBroadcastBtn from './OneClickBroadcastBtn';

const MobileQuickActionsCard = () => {
    return (
        <Flex style={{ width: '100%', minWidth: 200 }}>
            <Card
                title={<span><ThunderboltOutlined style={{ marginRight: 8 }} />管理員全體快捷操作</span>}
                style={{ width: '100%' }}
            >
                <Flex vertical gap={20} align='center'>
                    <OneClickOperationBtn operate='shutdown_computer' content='關閉電腦' />
                    <OneClickOperationBtn operate='restart_computer' content='重新啟動' />
                    <OneClickOperationBtn operate='close_vmware_workstation' content='關閉虛擬機' />
                    <OneClickOperationBtn operate='close_chrome' content='關閉Chrome' />
                    <OneClickBroadcastBtn />
                </Flex>
            </Card>
        </Flex>
    )
}

export default MobileQuickActionsCard