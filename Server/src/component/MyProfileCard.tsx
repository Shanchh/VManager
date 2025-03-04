import { Flex, Card, Avatar, Tag, Badge, Spin } from 'antd'
import React from 'react'
import { CalendarOutlined, SafetyCertificateOutlined, UserOutlined, DesktopOutlined, HeartOutlined } from '@ant-design/icons';
import { Account } from '../../type';
import RegisterVmBtn from './RegisterVmBtn';
import UserRoleTag from './UserRoleTag';

interface MyProfileCardProps {
    profile: Account | null;
    refreshData: () => void;
}

const MyProfileCard: React.FC<MyProfileCardProps> = ({ profile, refreshData }) => {
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
                        <UserRoleTag role={profile?.role} />
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
                    <RegisterVmBtn refreshData={refreshData} VMisCreate={profile?.VMisCreate} />
                </Flex>
            </Flex>
        </Card>
    )
}

export default MyProfileCard