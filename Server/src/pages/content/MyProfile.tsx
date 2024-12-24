import { Flex, Input, Card, Avatar, Tag, Badge } from 'antd'
import React, { useEffect, useState } from 'react'
import { CalendarOutlined, SafetyCertificateOutlined, UserOutlined, DesktopOutlined, HeartOutlined } from '@ant-design/icons';
import { get_my_data } from '../../api/ProcessApi';
import { Account } from '../../../type';
import RegisterVmBtn from '../../component/RegisterVmBtn';

const MyProfile = () => {
  const [profile, setProfile] = useState<Account | null>(null);

  const roleMap: Record<string, { color: string; label: string }> = {
    user: { color: '#efb01d', label: '員工' },
    admin: { color: '#b22222', label: '管理員' },
    owner: { color: '#40e0d0', label: '管理員' },
  };

  const RoleTag = ({ role }: { role: string | undefined }) => {
    if (!role) return null;

    const roleInfo = roleMap[role] || { color: 'gray', label: '未知角色' };
    return <Tag color={roleInfo.color}>{roleInfo.label}</Tag>;
  };

  const VMcreate = ({ isCreate }: { isCreate: boolean | undefined }) => {
    if (isCreate === undefined) return null;

    return isCreate ? (
      <Badge status="success" text="已註冊" />
    ) : (
      <Badge status="error" text="尚未註冊" />
    );
  };

  const OnlineTime = ({ heartbeatCount }: { heartbeatCount: number | undefined }) => {
    if (!heartbeatCount || heartbeatCount <= 0) return <span>未在線</span>;

    const totalSeconds = heartbeatCount * 5;
    const months = Math.floor(totalSeconds / (30 * 24 * 60 * 60));
    const days = Math.floor(totalSeconds / (24 * 60 * 60)) % 30;
    const hours = Math.floor(totalSeconds / (60 * 60)) % 24;
    const minutes = Math.floor(totalSeconds / 60) % 60;
    const seconds = totalSeconds % 60;

    const timeStrings = [
      months > 0 && `${months}月`,
      days > 0 && `${days}天`,
      hours > 0 && `${hours}時`,
      minutes > 0 && `${minutes}分`,
      seconds > 0 && `${seconds}秒`,
    ].filter(Boolean);

    return <span>{timeStrings.join('')}</span>;
  };

  const refreshData = async () => {
    const data = await get_my_data();
    setProfile(data);
  }

  useEffect(() => {
    refreshData();
  }, []);

  return (
    <Card
      title={<span><UserOutlined style={{ marginRight: 8 }} />個人資料</span>}
      style={{ width: 500 }}
    >
      <Flex vertical gap={5} justify='center' align='center' style={{ padding: '0 20px 0 20px', width: '100%' }}>
        <Avatar size={128} icon={<UserOutlined />} />
        <Flex vertical justify='center' align='center' style={{ width: '100%' }}>
          <div style={{ fontSize: 20, fontWeight: 'bold' }}>{profile?.nickname}</div>
          <div style={{ fontSize: 16 }}>{profile?.email}</div>
        </Flex>
        <Flex vertical gap={5} style={{ width: '100%', paddingTop: 25 }}>
          <div style={{ fontSize: 16 }}>
            <SafetyCertificateOutlined style={{ paddingRight: 8 }} />
            <RoleTag role={profile?.role} />
          </div>

          <div style={{ fontSize: 16 }}>
            <DesktopOutlined style={{ paddingRight: 8 }} />
            <VMcreate isCreate={profile?.VMisCreate} />
          </div>

          <div style={{ fontSize: 16 }}>
            <CalendarOutlined style={{ paddingRight: 8 }} />
            {profile?.createAt ? new Intl.DateTimeFormat('zh-TW', {
              year: 'numeric',
              month: '2-digit',
              day: '2-digit',
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit',
            }).format(new Date(profile.createAt * 1000)) : 'N/A'}
          </div>

          <div style={{ fontSize: 16 }}>
            <HeartOutlined style={{ paddingRight: 8 }} />
            <OnlineTime heartbeatCount={profile?.heartbeatCount} />
          </div>
        </Flex>
        <Flex style={{ paddingTop: 25 }}>
          <RegisterVmBtn refreshData={refreshData} VMisCreate={profile?.VMisCreate}/>
        </Flex>
      </Flex>
    </Card>
  )
}

export default MyProfile