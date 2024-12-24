import { Button, Flex, Input, message, Modal } from 'antd';
import React, { useState } from 'react';
import { ExclamationCircleOutlined } from '@ant-design/icons';
import { register_vmware } from '../api/ProcessApi';

interface RegisterVmBtnProps {
    VMisCreate: boolean | undefined;
    refreshData: () => void;
}

const RegisterVmBtn: React.FC<RegisterVmBtnProps> = ({ VMisCreate, refreshData }) => {
    const [modalOpen, setModal1Open] = useState<boolean>(false);
    const [loading, setLoading] = useState<boolean>(false);
    const [passwordInput, setPasswordInput] = useState<string>('');

    const registerVM = async () => {
        setLoading(true);
        if (passwordInput != '00000000') {
            setModal1Open(false);
            setLoading(false);
            message.error("管理員密碼錯誤！")
            return
        }

        try {
            const r = await register_vmware();
            message.success(`創建成功！${r.VMword}`);
            await navigator.clipboard.writeText(r.VMword);
        } catch (error: any) {
            console.error(error);
            message.error("創建失敗！");
        } finally {
            setModal1Open(false);
            setLoading(false);
            refreshData();
        }
    }

    const VMcreate = ({ isCreate }: { isCreate: boolean | undefined }) => {
        if (isCreate === undefined)
            return <Button type="primary" disabled>加載中...</Button>;

        return isCreate ? (
            <Button color="primary" variant="solid" disabled>註冊虛擬機帳號</Button>
        ) : (
            <Button color="primary" variant="solid" onClick={() => setModal1Open(true)}>註冊虛擬機帳號</Button>
        );
    };

    return (
        <Flex>
            <VMcreate isCreate={VMisCreate} />
            <Modal
                centered
                title={
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <ExclamationCircleOutlined style={{ color: 'orange' }} />
                        <span>輸入管理員密碼</span>
                    </div>
                }
                open={modalOpen}
                width={300}
                onCancel={() => setModal1Open(false)}
                footer={null}
            >
                <Input.Password
                    size='middle'
                    placeholder='輸入密碼'
                    value={passwordInput}
                    onChange={(e) => setPasswordInput(e.target.value)}
                ></Input.Password>
                <Flex justify='flex-end' gap={5} style={{ paddingTop: 10 }}>
                    <Button color="primary" variant="solid" style={{ fontSize: 16 }} loading={loading} onClick={() => registerVM()}>
                        創建
                    </Button>
                    <Button color="default" variant="outlined" style={{ fontSize: 16 }} onClick={() => setModal1Open(false)}>
                        取消
                    </Button>
                </Flex>
            </Modal>
        </Flex>
    )
}

export default RegisterVmBtn