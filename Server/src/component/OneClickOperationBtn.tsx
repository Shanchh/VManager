import { Button, Flex, message, Modal } from 'antd'
import React, { useState } from 'react'
import { ExclamationCircleOutlined } from '@ant-design/icons';
import { call_oneclick_operation } from '../api/ProcessApi';

interface OneClickOperationBtnProps {
    operate: string;
    content: string;
}

const OneClickOperationBtn: React.FC<OneClickOperationBtnProps> = ({ content, operate }) => {
    const [modalOpen, setModal1Open] = useState<boolean>(false);
    const [loading, setLoading] = useState<boolean>(false);

    const one_click_operation = async () => {
        setLoading(true);
        try {
            const command = {
                operation: operate
            }
            const result = await call_oneclick_operation(command);
            message.success("一鍵" + content + "指令傳送成功！");
        } catch (error: any) {
            console.error(error);
            message.error("傳送指令失敗！");
        }
        setModal1Open(false);
        setLoading(false);
    }

    return (
        <Flex>
            <Button color="danger" variant="outlined" style={{ width: 100 }} onClick={() => setModal1Open(true)}>{content}</Button>
            <Modal
                centered
                title={
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <ExclamationCircleOutlined style={{ color: 'orange' }} />
                        <span>確認一鍵操作</span>
                    </div>
                }
                open={modalOpen}
                width={300}
                onCancel={() => setModal1Open(false)}
                footer={null}
            >
                對全體成員進行 <span style={{ color: 'red' }}>{content}</span> 指令？
                <Flex justify='flex-end' gap={5} style={{ paddingTop: 10 }}>
                    <Button color="primary" variant="solid" style={{ fontSize: 16 }} loading={loading} onClick={() => one_click_operation()}>
                        確認
                    </Button>
                    <Button color="default" variant="outlined" style={{ fontSize: 16 }} onClick={() => setModal1Open(false)}>
                        取消
                    </Button>
                </Flex>
            </Modal>
        </Flex>
    )
}

export default OneClickOperationBtn