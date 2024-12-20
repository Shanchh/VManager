import { Button, Divider, Flex, Form, Input, message } from 'antd';
import React, { useState } from 'react'
import { DesktopOutlined } from '@ant-design/icons';

interface LoginFormProps {
    onRegisterClick: () => void;
}

const LoginForm: React.FC<LoginFormProps> = ({ onRegisterClick }) => {
    const [loading, setLoading] = useState<boolean>(false);

    const onForgetPassword = () => {
        message.success('您點選了忘記密碼');
    }

    const onFinish = () => {

    }

    return (
        <Flex vertical justify='center' align='center' style={{ width: 400, padding: 24, backgroundColor: '#ffffff', borderRadius: 8, boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
            <Flex gap={10} style={{ paddingBottom: 20 }}>
                <DesktopOutlined style={{ fontSize: 30 }} />
                <div style={{ fontSize: 30, fontWeight: 'bold', fontFamily: "Lucida Console, 微軟正黑體, 新細明體, sans-serif" }}>VManager管理系統</div>
            </Flex>
            <Form name="login_form" layout="vertical" onFinish={onFinish} style={{ width: '100%' }} initialValues={{ email: '', password: '' }}>
                <Form.Item label="信箱" name="email" rules={[{ required: true, message: '請輸入您的信箱！' }, { type: 'email', message: '信箱格式不正確！' }]}>
                    <Input placeholder="輸入您的信箱" />
                </Form.Item>
                <Form.Item label="密碼" name="password" rules={[{ required: true, message: '請輸入您的密碼！' }, { min: 6, message: '密碼必須至少 6 個字符！' }]}>
                    <Input.Password placeholder="輸入您的密碼" />
                </Form.Item>
                <Form.Item>
                    <a onClick={onForgetPassword}>忘記密碼?</a>
                    <Button type="primary" htmlType="submit" block>登錄</Button>
                </Form.Item>
                <Flex justify="center" gap={5}>
                    <span style={{color: 'gray'}}>您還沒有帳號嗎?</span>
                    <a onClick={() => onRegisterClick()}>註冊帳號</a>
                </Flex>
            </Form>
        </Flex>
    )
}

export default LoginForm