import { Button, Flex, Modal, Tooltip } from 'antd'
import React, { useState } from 'react'
import { ReactNode } from 'react';
import { Client } from '../types/type';
import { ExclamationCircleOutlined } from '@ant-design/icons';

interface OperateCheckModalProps {
    icon: ReactNode;
    onOperate: (operation: string, content: string) => void;
    operate: string;
    data: Client;
    content: string;
}

const OperateCheckModal: React.FC<OperateCheckModalProps> = ({ icon, onOperate, data, content, operate }) => {
    const [modalOpen, setModal1Open] = useState<boolean>(false);
    const [loading, setLoading] = useState<boolean>(false);

    const msg = `確認對 ${data.username} 執行 ${content} 指令？`;

    const onCheck = () => {
        setLoading(true);
        onOperate(operate, content);
        setModal1Open(false);
        setLoading(false);
    };

    return (
        <Flex>
            <Tooltip placement="top" title={content} arrow={true}>
                <Button
                    type="default"
                    icon={icon}
                    style={{ height: 25, width: 40 }}
                    onClick={() => setModal1Open(true)}
                />
                <Modal
                    centered
                    title={
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <ExclamationCircleOutlined style={{ color: 'orange' }} />
                            <span>確認操作</span>
                        </div>
                    }
                    open={modalOpen}
                    width={300}
                    onCancel={() => setModal1Open(false)}
                    footer={null}
                >
                    {msg}
                    <Flex justify='flex-end' gap={5} style={{ paddingTop: 10 }}>
                        <Button color="primary" variant="solid" style={{ fontSize: 16 }} loading={loading} onClick={() => onCheck()}>
                            確認
                        </Button>
                        <Button color="default" variant="outlined" style={{ fontSize: 16 }} onClick={() => setModal1Open(false)}>
                            取消
                        </Button>
                    </Flex>
                </Modal>
            </Tooltip>
        </Flex>
    )
}

export default OperateCheckModal