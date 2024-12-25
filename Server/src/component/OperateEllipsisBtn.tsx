import { Button, Flex, Modal, Tooltip } from 'antd'
import React, { useState } from 'react'
import { EllipsisOutlined, BarsOutlined } from '@ant-design/icons';
import { Client } from '../types/type';
import BroadcastHub from './BroadcastHub';

interface OperateEllipsisBtnProps {
    data: Client;
}

const OperateEllipsisBtn: React.FC<OperateEllipsisBtnProps> = ({ data }) => {
    const [modalOpen, setModal1Open] = useState<boolean>(false);

    return (
        <Flex>
            <Tooltip placement="top" title="更多選項" arrow={true}>
                <Button
                    type="default"
                    icon={<EllipsisOutlined />}
                    style={{ height: 25, width: 40 }}
                    onClick={() => setModal1Open(true)}
                />
                <Modal
                    centered
                    title={
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <BarsOutlined style={{ color: 'orange' }} />
                            <span>更多選項 [{data.username}]</span>
                        </div>
                    }
                    open={modalOpen}
                    width={400}
                    onCancel={() => setModal1Open(false)}
                    footer={null}
                >
                    <BroadcastHub data={data}/>
                </Modal>
            </Tooltip>
        </Flex>
    )
}

export default OperateEllipsisBtn