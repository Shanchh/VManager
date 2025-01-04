import { Button, Flex, Modal, Popconfirm, Input, message } from 'antd'
import React, { useState } from 'react'
import { Account } from '../../type';
import { ExclamationCircleOutlined } from '@ant-design/icons';
import { delete_account } from '../api/ProcessApi';

interface DeleteAccountBtnProps {
    data: Account;
    onDelete: (id: string) => void;
}

const DeleteAccountBtn: React.FC<DeleteAccountBtnProps> = ({ data, onDelete }) => {
    const [modalOpen, setModalOpen] = useState<boolean>(false);
    const [loading, setLoading] = useState<boolean>(false);
    const [passwordInput, setPasswordInput] = useState<string>('');

    const deleteAccount = async () => {
        setLoading(true);
        if (passwordInput != '00000000') {
            setModalOpen(false);
            setLoading(false);
            message.error("管理員密碼錯誤！")
            return
        }
        
        try {
            const command = {
                data: data
            }
            const r = await delete_account(command);
            message.success(`刪除帳號成功！${data.nickname}`);
            await navigator.clipboard.writeText(r.VMword);
            onDelete(data._id);
        } catch (error: any) {
            console.error(error);
            message.error("刪除失敗！");
        } finally {
            setModalOpen(false);
            setLoading(false);
        }
    };

    return (
        <Flex justify="center" align="center" gap={5}>
            <Button
                type="default"
                style={{ height: 25, width: 45 }}
                onClick={() => setModalOpen(true)}
            >刪除
            </Button>
            <Modal
                centered
                title={
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <ExclamationCircleOutlined style={{ color: 'orange' }} />
                        <span>刪除用戶 {data.nickname}</span>
                    </div>
                }
                open={modalOpen}
                width={300}
                onCancel={() => setModalOpen(false)}
                footer={null}
            >
                請輸入管理員密碼:
                <Input.Password
                    size='middle'
                    placeholder='輸入密碼'
                    value={passwordInput}
                    onChange={(e) => setPasswordInput(e.target.value)}
                ></Input.Password>
                <Flex justify='flex-end' gap={5} style={{ paddingTop: 10 }}>
                    <Button color="primary" variant="solid" style={{ fontSize: 16 }} loading={loading} onClick={() => deleteAccount()}>
                        送出
                    </Button>
                    <Button color="default" variant="outlined" style={{ fontSize: 16 }} onClick={() => setModalOpen(false)}>
                        取消
                    </Button>
                </Flex>
            </Modal>
        </Flex>
    )
}

export default DeleteAccountBtn