import { Card, Flex } from 'antd'
import React from 'react'
import { ThunderboltOutlined } from '@ant-design/icons';
import OneClickOperationBtn from './OneClickOperationBtn';
import OneClickBroadcastBtn from './OneClickBroadcastBtn';

const QuickActionsCard = () => {
    return (
        <Card
            title={<span><ThunderboltOutlined style={{ marginRight: 8 }} />管理員全體快捷操作</span>}
            style={{ height: 190, width: 410 }}
        >
            <Flex vertical justify='center' gap={20} style={{ width: '100%' }}>
                <Flex gap={30}>
                    <OneClickOperationBtn operate='shutdown_computer' content='關閉電腦' />
                    <OneClickOperationBtn operate='restart_computer' content='重新啟動' />
                    <OneClickBroadcastBtn />
                </Flex>
                <Flex gap={30}>
                    <OneClickOperationBtn operate='close_vmware_workstation' content='關閉虛擬機' />
                    <OneClickOperationBtn operate='close_chrome' content='關閉Chrome' />
                </Flex>
            </Flex>
        </Card>
    )
}

export default QuickActionsCard