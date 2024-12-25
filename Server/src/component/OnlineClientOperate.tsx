import { Flex, message } from 'antd'
import { PoweroffOutlined, ReloadOutlined, DesktopOutlined } from '@ant-design/icons';
import React, { useState } from 'react'
import { Client } from '../types/type';
import { call_operation } from '../api/ProcessApi';
import OperateCheckModal from './OperateCheckModal';
import OperateEllipsisBtn from './OperateEllipsisBtn';

interface OnlineClientOperateProps {
    data: Client;
}

const OnlineClientOperate: React.FC<OnlineClientOperateProps> = ({ data }) => {
    const onOperate = async (operation: string, content: string) => {
        const msg = {
            method: operation,
            content: {
                username: data.username
            }
        }
        try {
            const result = await call_operation(msg);
            message.success(content + "指令傳送成功！");
        } catch (error: any) {
            console.error(error);
            message.error("傳送指令失敗！");
        }
    }

    return (
        <Flex justify='center' align='center' gap={10}>
            <OperateCheckModal icon={<PoweroffOutlined />} onOperate={onOperate} operate='shutdown_computer' data={data} content='關閉電腦'/>
            <OperateCheckModal icon={<ReloadOutlined />} onOperate={onOperate} operate='restart_computer' data={data} content='重啟電腦'/>
            <OperateCheckModal icon={<DesktopOutlined />} onOperate={onOperate} operate='close_vmware_workstation' data={data} content='關閉虛擬機'/>
            <OperateEllipsisBtn data={data}/>
        </Flex>
    )
}

export default OnlineClientOperate