import { Avatar, Card, Flex, List, Spin } from 'antd'
import React, { useEffect, useState } from 'react'
import { ProfileOutlined, InfoCircleOutlined, WarningOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { get_my_20_activities } from '../api/ProcessApi';
import { Log } from '../../type';

const MyRecentActivitiesCard = () => {
    const [activitiesData, setActivitiesData] = useState<Log[]>([]);
    const [loading, setLoading] = useState<boolean>(false);

    const refreshData = async () => {
        setLoading(true);
        const data: Log[] = await get_my_20_activities();
        setActivitiesData(data);
        setLoading(false);
    };

    useEffect(() => {
        refreshData();
    }, []);

    const getIconByLevel = (level: string) => {
        switch (level) {
            case 'INFO':
                return <InfoCircleOutlined style={{ fontSize: 25, color: '#87d068' }} />;
            case 'WARN':
                return <WarningOutlined style={{ fontSize: 25, color: '#faad14' }} />;
            case 'ERROR':
                return <CloseCircleOutlined style={{ fontSize: 25, color: '#f5222d' }} />;
            default:
                return <InfoCircleOutlined style={{ fontSize: 25, color: '#d9d9d9' }} />;
        }
    };

    return (
        <Card
            title={<span><ProfileOutlined style={{ marginRight: 8 }} />我的近期動態</span>}
            style={{ width: 500 }}
        >
            {loading ? (
                <Flex justify='center' align='center' style={{ height: 200, width: '100%' }}>
                    <div style={{color: 'gray'}}>加載中...</div>
                </Flex>
            ) : (
                <List
                    itemLayout="horizontal"
                    dataSource={activitiesData}
                    renderItem={(item) => (
                        <List.Item>
                            <Flex gap={20} style={{ width: '100%' }}>
                                {getIconByLevel(item.level)}
                                <List.Item.Meta
                                    title={new Date(item.timestamp).toLocaleString('zh-CN', {
                                        year: 'numeric',
                                        month: '2-digit',
                                        day: '2-digit',
                                        hour: '2-digit',
                                        minute: '2-digit',
                                        second: '2-digit',
                                        hour12: false,
                                    })}
                                    description={item.details.message}
                                />
                            </Flex>
                        </List.Item>
                    )}
                />
            )}
        </Card>
    );
}

export default MyRecentActivitiesCard