import { Button, Flex, message, Tooltip } from 'antd'
import { PoweroffOutlined, ReloadOutlined, DesktopOutlined } from '@ant-design/icons';
import React, { useState } from 'react'
import { Client } from '../types/type';
import { call_operation } from '../api/ProcessApi';

interface OnlineClientOperateProps {
    data: Client;
}

const OnlineClientOperate: React.FC<OnlineClientOperateProps> = ({ data }) => {
    const [loading, setLoading] = useState<boolean>(false);

    const onOperate = async (operation: string) => {
        const msg = {
            method: operation,
            content: {
                username: data.username
            }
        }
        try {
            const result = await call_operation(msg);
            message.success(result);
        } catch (error: any) {
            console.error(error);
            message.error("傳送指令失敗！");
        } finally {
            
        }
    }

    return (
        <Flex justify='center' align='center' gap={10}>
            <Tooltip placement="top" title="關閉電腦" arrow={true}>
                <Button
                    type="default"
                    icon={<PoweroffOutlined />}
                    style={{ height: 25, width: 40 }}
                    onClick={() => onOperate("shutdown_computer")}
                />
            </Tooltip>

            <Tooltip placement="top" title="重啟電腦" arrow={true}>
                <Button
                    type="default"
                    icon={<ReloadOutlined />}
                    style={{ height: 25, width: 40 }}
                    onClick={() => onOperate("restart_computer")}
                />
            </Tooltip>

            <Tooltip placement="top" title="關閉虛擬機" arrow={true}>
                <Button
                    type="default"
                    icon={<DesktopOutlined />}
                    style={{ height: 25, width: 40 }}
                    onClick={() => onOperate("close_vmware_workstation")}
                />
            </Tooltip>
        </Flex>
    )
}

export default OnlineClientOperate