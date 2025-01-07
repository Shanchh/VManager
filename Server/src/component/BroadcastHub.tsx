import { Button, Flex, Input, message, Modal } from 'antd'
import React, { useState } from 'react'
import { Client } from '../types/type';
import { call_operation } from '../api/ProcessApi';
import { BarsOutlined } from '@ant-design/icons';

interface BroadcastHubProps {
    data: Client;
    modalOpen: boolean;
    setModal1Open: (value: boolean) => void;
}

const { TextArea } = Input;

const BroadcastHub: React.FC<BroadcastHubProps> = ({ data, setModal1Open, modalOpen }) => {
    const [text, setText] = useState<string>('');
    const [loading, setLoading] = useState<boolean>(false);

    const onBoardcast = async () => {
        try {
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
            message.success(`已成功廣播 ${text} 給${data.username}`)
            setModal1Open(false);
            setLoading(false);
        } catch {
            message.error("廣播訊息失敗！")
        }
    };
    return (
        <Modal
            centered
            title={
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <BarsOutlined style={{ color: 'orange' }} />
                    <span>廣播訊息 [{data.username}]</span>
                </div>
            }
            width={400}
            open={modalOpen}
            onCancel={() => setModal1Open(false)}
            footer={null}
        >
            <Flex vertical justify='start' align='start' gap={5} style={{ width: '100%', paddingTop: 10 }}>
                <div style={{ fontSize: 14, fontWeight: 'bold' }}>內容：</div>
                <TextArea
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    placeholder="輸入內容"
                    autoSize={{ minRows: 3, maxRows: 5 }}
                />
                <Flex justify='end' style={{ paddingTop: 5, width: '100%' }}>
                    <Button color="primary" variant="outlined" style={{ width: 72 }} loading={loading} onClick={() => onBoardcast()}>送出</Button>
                </Flex>
            </Flex>
        </Modal>

    )
}

export default BroadcastHub