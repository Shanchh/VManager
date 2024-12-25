import { Button, Flex, Input, message } from 'antd'
import React, { useState } from 'react'
import { Client } from '../types/type';
import { call_operation } from '../api/ProcessApi';

interface BroadcastHubProps {
    data: Client;
}

const { TextArea } = Input;

const BroadcastHub: React.FC<BroadcastHubProps> = ({ data }) => {
    const [text, setText] = useState<string>('');
    const [loading, setLoading] = useState<boolean>(false);

    const onBoardcast = async () => {
        setLoading(true);
        if (!text) {
            message.error("請輸入訊息內容！");
            setLoading(false);
            return;
        }

        const command = {
            method: "message",
            content: {
                username: data.username,
                msg: text
            }
        }
        call_operation(command);
        setLoading(false);
    };
    return (
        <Flex vertical justify='start' align='start' gap={5} style={{ width: '100%', paddingTop: 10 }}>
            <div style={{ fontSize: 14, fontWeight: 'bold' }}>廣播訊息：</div>
            <TextArea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="輸入內容"
                autoSize={{ minRows: 3, maxRows: 5 }}
            />
            <Flex justify='end' style={{ paddingTop:5, width: '100%' }}>
                <Button color="primary" variant="outlined" style={{ width: 72 }} loading={loading} onClick={() => onBoardcast()}>送出</Button>
            </Flex>
        </Flex>
    )
}

export default BroadcastHub