import { Button, Card, Flex } from 'antd'
import React from 'react'
import { SettingOutlined } from '@ant-design/icons';
import ResetPasswordBtn from '../../component/ResetPasswordBtn';

const Setting = () => {
  return (
    <Card
      title={<span><SettingOutlined style={{ marginRight: 8 }} />設定</span>}
      style={{ width: 500 }}
    >
      <ResetPasswordBtn />
    </Card>
  )
}

export default Setting