import React, { useState } from 'react'
import { Button, Flex, Input, message, Modal } from 'antd';
import { MailOutlined } from '@ant-design/icons';
import { auth } from '../../auth/FirebaseConfig';
import { sendPasswordResetEmail } from 'firebase/auth';

const ForgetPasswordBtn = () => {
    const [modalOpen, setModal1Open] = useState<boolean>(false);
    const [email, setEmail] = useState<string>("");
    const [loading, setLoading] = useState<boolean>(false);

    const handleForgetPassword = async () => {
        setLoading(true);
        if (!email) {
            message.error("請輸入有效的電子郵件地址！");
            setLoading(false);
            return;
        }

        try {
            await sendPasswordResetEmail(auth, email);
            message.success("重置密碼的郵件已發送，請檢查您的信箱！");

            setModal1Open(false);
        } catch (error: any) {
            console.error(error);
            message.error("重置密碼郵件發送失敗，請確認電子郵件地址是否正確！");
        } finally {
            setLoading(false);
        }
    }

    return (
        <Flex>
            <a onClick={() => setModal1Open(true)}>忘記密碼?</a>
            <Modal
                centered
                title="重設密碼"
                open={modalOpen}
                width={300}
                onCancel={() => setModal1Open(false)}
                footer={null}
            >
                <p>我們將會寄送重設郵件至您的電子郵箱</p>
                <Input size="middle" placeholder="請輸入您的電子信箱" prefix={<MailOutlined />} style={{ width: '100%' }} onChange={(e) => setEmail(e.target.value)} />
                <Flex justify='flex-end'>
                    <Button style={{marginTop: 18, height: 30}} color="primary" variant="solid" loading={loading} onClick={() => handleForgetPassword()}>送出申請</Button>
                </Flex>
            </Modal>
        </Flex>
    )

}

export default ForgetPasswordBtn