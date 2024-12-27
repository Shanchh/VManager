import { Button, Flex, message, Modal } from 'antd'
import TextArea from 'antd/es/input/TextArea'
import React, { useState } from 'react'
import { RocketOutlined } from '@ant-design/icons';
import { call_oneclick_broadcast } from '../api/ProcessApi';

const OneClickBroadcastBtn = () => {
    const [text, setText] = useState<string>('');
    const [modalOpen, setModal1Open] = useState<boolean>(false);
    const [loading, setLoading] = useState<boolean>(false);

    const onBoardcast = async () => {
        setLoading(true);
        try {
            const command = {
                content: text
            }
            const result = await call_oneclick_broadcast(command);
            message.success("一鍵廣播傳送成功");
        } catch (error: any) {
            console.error(error);
            message.error("一鍵廣播失敗！");
        }
        setModal1Open(false);
        setLoading(false);
    }

    return (
        <Flex>
            <Button color="default" variant="outlined" style={{ width: 100 }} onClick={() => setModal1Open(true)}>廣播訊息</Button>
            <Modal
                centered
                title={
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <RocketOutlined style={{ color: 'orange' }} />
                        <span>一鍵廣播訊息</span>
                    </div>
                }
                open={modalOpen}
                width={400}
                onCancel={() => setModal1Open(false)}
                footer={null}
            >
                <Flex vertical justify='start' align='start' gap={5} style={{ width: '100%', paddingTop: 10 }}>
                    <div style={{ fontSize: 14, fontWeight: 'bold' }}>廣播訊息：</div>
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
        </Flex>
    )
}

export default OneClickBroadcastBtn