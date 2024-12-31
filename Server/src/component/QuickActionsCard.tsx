import { Button, Card, Flex } from 'antd'
import React from 'react'
import { ThunderboltOutlined } from '@ant-design/icons';
import OneClickOperationBtn from './OneClickOperationBtn';
import OneClickBroadcastBtn from './OneClickBroadcastBtn';

const QuickActionsCard = () => {
    return (
        <Card
            title={<span><ThunderboltOutlined style={{ marginRight: 8 }} />管理員全體快捷操作</span>}
            style={{ width: 500 }}
        >
            <Flex justify='center' gap={10} style={{ width: '100%' }}>
                <OneClickOperationBtn operate='shutdown_computer' content='關閉電腦' />
                <OneClickOperationBtn operate='restart_computer' content='重新啟動' />
                <OneClickOperationBtn operate='close_vmware_workstation' content='關閉虛擬機' />
                <OneClickOperationBtn operate='close_chrome' content='關閉Chrome' />
            </Flex>
        </Card>
    )
}

export default QuickActionsCard