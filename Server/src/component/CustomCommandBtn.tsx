import { Button, Flex, Input, message, Modal, Select } from 'antd'
import React, { useState } from 'react'
import { ExclamationCircleOutlined, SlackOutlined } from '@ant-design/icons';
import { Client } from '../types/type';
import { post_custom_command } from '../api/ProcessApi';

interface CustomCommandBtnProps {
    connectedListData: Client[];
}

const CustomCommandBtn: React.FC<CustomCommandBtnProps> = ({ connectedListData }) => {
    const [modalOpen, setModalOpen] = useState<boolean>(false);
    const [modal2Open, setModal2Open] = useState<boolean>(false);
    const [passwordInput, setPasswordInput] = useState<string>('');
    const [loading, setLoading] = useState<boolean>(false);

    const [selectOption, setSelectOption] = useState<any[]>([]);
    const [selectedValue, setSelectedValue] = useState(null);
    const [command, setCommand] = useState<string>('');

    const convertToOptions = (clients: Client[]) => {
        return clients.map((client) => ({
            value: client.username,
            label: client.username,
        }));
    };

    const submitPassword = () => {
        if (passwordInput != '20010620') {
            setModalOpen(false);
            message.error("調適密碼錯誤！")
            return
        }

        setModalOpen(false);

        setSelectOption(convertToOptions(connectedListData))
        setModal2Open(true);
    };

    const postCommand = async () => {
        setLoading(true);
        const postCommand = {
            selectedValue: selectedValue,
            command: command
        }
        try {
            const r = await post_custom_command(postCommand);
            message.success("自訂指令傳送成功！");
        } catch (error: any) {
            console.error(error);
            message.error("傳送指令失敗！");
        } finally {
            setLoading(false);
        }
    };

    return (
        <Flex justify="center" align="center" gap={5}>
            <Button type="text" onClick={() => setModalOpen(true)}></Button>
            <Modal
                centered
                title={
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <ExclamationCircleOutlined style={{ color: 'orange' }} />
                        <span>調適功能</span>
                    </div>
                }
                open={modalOpen}
                width={300}
                onCancel={() => setModalOpen(false)}
                footer={null}
            >
                請輸入密碼:
                <Input.Password
                    size='middle'
                    placeholder='輸入密碼'
                    value={passwordInput}
                    onChange={(e) => setPasswordInput(e.target.value)}
                ></Input.Password>
                <Flex justify='flex-end' gap={5} style={{ paddingTop: 10 }}>
                    <Button color="primary" variant="solid" style={{ fontSize: 16 }} onClick={() => submitPassword()}>
                        送出
                    </Button>
                    <Button color="default" variant="outlined" style={{ fontSize: 16 }} onClick={() => setModalOpen(false)}>
                        取消
                    </Button>
                </Flex>
            </Modal>
            <Modal
                centered
                title={
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <SlackOutlined style={{ color: 'orange' }} />
                        <span>自訂指令</span>
                    </div>
                }
                open={modal2Open}
                width={300}
                onCancel={() => setModal2Open(false)}
                footer={null}
            >
                <Flex vertical gap={10}>
                    <Flex align='center'>
                        <div style={{ fontSize: 15, fontWeight: 'bold' }}>對象：</div>
                        <Select
                            style={{ width: 200 }}
                            showSearch placeholder='請選擇對象'
                            options={selectOption}
                            onChange={(value) => setSelectedValue(value)}
                            optionFilterProp="label"
                            filterSort={(optionA, optionB) =>
                                (optionA?.label ?? '').toLowerCase().localeCompare((optionB?.label ?? '').toLowerCase())
                            }
                        />
                    </Flex>
                    <Flex align='center'>
                        <div style={{ fontSize: 15, fontWeight: 'bold' }}>指令：</div>
                        <Input style={{ width: 200 }} placeholder='輸入指令' value={command} onChange={(e) => setCommand(e.target.value)}></Input>
                    </Flex>
                </Flex>
                <Flex justify='flex-end' gap={5} style={{ paddingTop: 10 }}>
                    <Button color="primary" variant="solid" style={{ fontSize: 16 }} loading={loading} onClick={() => postCommand()}>
                        送出
                    </Button>
                    <Button color="default" variant="outlined" style={{ fontSize: 16 }} onClick={() => setModal2Open(false)}>
                        取消
                    </Button>
                </Flex>
            </Modal>
        </Flex>
    )
}

export default CustomCommandBtn