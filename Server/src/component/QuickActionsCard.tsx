import { Button, Card, Flex } from 'antd'
import React from 'react'
import { ThunderboltOutlined } from '@ant-design/icons';

const QuickActionsCard = () => {
    return (
        <Card
            title={<span><ThunderboltOutlined style={{ marginRight: 8 }} />管理員全體快捷操作</span>}
            style={{ width: 500 }}
        >
            <Flex justify='center' gap={50} style={{width:'100%'}}>
                <Button color="danger" variant="outlined">關閉電腦</Button>
                <Button color="danger" variant="outlined">重新啟動</Button>
                <Button color="danger" variant="outlined">關閉虛擬機</Button>
            </Flex>
        </Card>
    )
}

export default QuickActionsCard