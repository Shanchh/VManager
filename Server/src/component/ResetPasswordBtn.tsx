import { Button, Flex, message, Modal } from 'antd'
import React, { useState } from 'react'
import { LockOutlined } from '@ant-design/icons';
import { auth } from '../auth/FirebaseConfig';
import { useAuth } from '../auth/AuthProvider';
import { sendPasswordResetEmail } from 'firebase/auth';

const ResetPasswordBtn = () => {
    const [modalOpen, setModalOpen] = useState<boolean>(false);
    const [loading, setLoading] = useState<boolean>(false);

    const { userProfile } = useAuth();

    const onConfirm = async () => {
        setLoading(true);
        if (userProfile){
            try {
                await sendPasswordResetEmail(auth, userProfile.email);
                message.success("重置密碼的郵件已發送，請檢查您的信箱！");
    
                setModalOpen(false);
            } catch (error: any) {
                console.error(error);
                message.error("重置密碼郵件發送失敗，請確認電子郵件地址是否正確！");
            } finally {
                setLoading(false);
            }
        } else {
            message.error('發生錯誤！');
            setLoading(false);
        }
    };

    return (
        <Flex>
            <Button color="primary" variant="outlined" icon={<LockOutlined />} onClick={() => setModalOpen(true)}>變更密碼</Button>
            <Modal
                centered
                title={
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <LockOutlined style={{ color: 'orange' }} />
                        <span>變更密碼</span>
                    </div>
                }
                open={modalOpen}
                width={300}
                onCancel={() => setModalOpen(false)}
                footer={null}
            >
                將會寄送重設密碼郵件至您的電子信箱！
                <Flex justify='flex-end' gap={5} style={{ paddingTop: 10 }}>
                    <Button color="default" variant="outlined" style={{ fontSize: 16 }} onClick={() => setModalOpen(false)}>
                        取消
                    </Button>
                    <Button color="primary" variant="solid" style={{ fontSize: 16 }} loading={loading} onClick={() => onConfirm()}>
                        確認
                    </Button>
                </Flex>
            </Modal>
        </Flex>
    )
}

export default ResetPasswordBtn