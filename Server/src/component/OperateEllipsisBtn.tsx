import { Button, Dropdown, Flex, message, Tooltip } from 'antd'
import React, { useState } from 'react'
import type { MenuProps } from 'antd';
import { EllipsisOutlined } from '@ant-design/icons';
import { Client } from '../types/type';
import BroadcastHub from './BroadcastHub';
import { call_update_client } from '../api/ProcessApi';

interface OperateEllipsisBtnProps {
    data: Client;
}

const OperateEllipsisBtn: React.FC<OperateEllipsisBtnProps> = ({ data }) => {
    const [modalOpen, setModal1Open] = useState<boolean>(false);
    const [dropdownOpen, setDropdownOpen] = useState<boolean>(false);

    const callUpdateClient = async () => {
        try {
            const command = {
                username: data.username
            };
            const r = await call_update_client(command);
            message.success(`已成功傳送更新指令給${data.username}`)
        } catch {
            message.error("傳送指令失敗！")
        }
    };

    const items: MenuProps['items'] = [
        {
            key: '1',
            label: (
                <div
                    onClick={() => {
                        setModal1Open(true);
                        setDropdownOpen(false);
                    }}
                    style={{ display: 'flex', alignItems: 'center', justifyContent: 'start', cursor: 'pointer' }}
                >
                    廣播訊息
                </div>
            ),
        },
        {
            key: '2',
            label: (
                <div
                    onClick={() => {
                        callUpdateClient();
                    }}
                    style={{ display: 'flex', alignItems: 'center', justifyContent: 'start', cursor: 'pointer' }}
                >
                    更新客戶端
                </div>
            ),
        },
    ];

    return (
        <Flex>
            <Tooltip placement="top" title="更多選項" arrow={true}>
                <Dropdown
                    menu={{ items }}
                    placement="top"
                    arrow
                    open={dropdownOpen}
                    onOpenChange={(open) => setDropdownOpen(open)}
                    trigger={['click']}
                >
                    <Button
                        type="default"
                        icon={<EllipsisOutlined />}
                        style={{ height: 25, width: 40 }}
                        onClick={() => setDropdownOpen(!dropdownOpen)}
                    />
                </Dropdown>
            </Tooltip>
            <BroadcastHub data={data} setModal1Open={setModal1Open} modalOpen={modalOpen} />
        </Flex>
    )
}

export default OperateEllipsisBtn