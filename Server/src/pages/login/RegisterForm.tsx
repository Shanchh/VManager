import { Button, Flex, Form, Input, message } from 'antd';
import React, { useState } from 'react'
import { UserAddOutlined } from '@ant-design/icons';
import { createUserWithEmailAndPassword, sendEmailVerification } from "firebase/auth";
import { auth } from '../../auth/FirebaseConfig';

interface RegisterFormProps {
    onLoginClick: () => void;
}

const RegisterForm: React.FC<RegisterFormProps> = ({ onLoginClick }) => {
    const [loading, setLoading] = useState<boolean>(false);

    const handleRegister = async (values: { name: string; email: string; password: string; }) => {
        setLoading(true);

        try {
            const userCredential = await createUserWithEmailAndPassword(auth, values.email, values.password);

            await sendEmailVerification(userCredential.user);
            message.success('註冊成功！請檢查您的電子郵件以完成驗證。');
            console.log('驗證信已發送：', userCredential.user.email);

        } catch (error: any) {
            console.error('註冊失敗：', error);
            message.error(`註冊失敗：${error.message}`);
        } finally {
            setLoading(false);
        }
    }

    return (
        <Flex vertical justify='center' align='center' gap={20} style={{ width: 400, padding: 24, backgroundColor: '#ffffff', borderRadius: 8, boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
            <Flex gap={10}>
                <UserAddOutlined style={{ fontSize: 30 }} />
                <div style={{ fontSize: 30, fontWeight: 'bold', fontFamily: "Lucida Console, 微軟正黑體, 新細明體, sans-serif" }}>VManager註冊帳號</div>
            </Flex>
            <Form name="register_form" layout="vertical" onFinish={handleRegister} style={{ width: '100%' }} initialValues={{ email: '', password: '' }}>
                <Form.Item label="暱稱" name="name" rules={[{ required: true, message: '請輸入您的暱稱！' }]}>
                    <Input placeholder="輸入您在公司的稱呼" />
                </Form.Item>
                <Form.Item label="信箱" name="email" rules={[{ required: true, message: '請輸入您的信箱！' }, { type: 'email', message: '信箱格式不正確！' }]}>
                    <Input placeholder="輸入您的信箱" />
                </Form.Item>
                <Form.Item label="密碼" name="password" rules={[{ required: true, message: '請輸入您的密碼！' }, { min: 6, message: '密碼必須至少 6 個字符！' }]}>
                    <Input.Password placeholder="輸入您的密碼" />
                </Form.Item>
                <Form.Item label="確認密碼" name="confirmp" dependencies={['password']}
                    rules={[
                        { required: true, message: '請輸入確認密碼！' },
                        ({ getFieldValue }) => ({
                            validator(_, value) {
                                if (!value || getFieldValue('password') === value) {
                                    return Promise.resolve();
                                }
                                return Promise.reject(new Error('密碼與確認密碼不一致！'))
                            },
                        }),
                    ]}
                >
                    <Input.Password placeholder="請輸入您的密碼" />
                </Form.Item>
                <Form.Item>
                    <a onClick={onLoginClick}>已有帳號?</a>
                    <Button type="primary" htmlType="submit" loading={loading} block>註冊</Button>
                </Form.Item>
            </Form>
        </Flex>
    )
}

export default RegisterForm