import React from 'react';
import { Line } from '@ant-design/charts';
import { Card, Flex } from 'antd';
import { AreaChartOutlined } from '@ant-design/icons';
import { LogCountData } from '../types/type';

interface UserLogsCountGraphCardProps {
    data: LogCountData[];
}

const UserLogsCountGraphCard: React.FC<UserLogsCountGraphCardProps> = ({ data }) => {
    const config = {
        data,
        xField: 'time',
        yField: 'value',
        seriesField: 'category',
        smooth: true,
        meta: {
            value: { alias: '數值' },
            time: { alias: '時間' },
        },
        xAxis: {
            title: { text: '日期' },
        },
        yAxis: {
            title: { text: '值' },
        },
        legend: {
            position: 'top',
        },
    };

    return (
        <Flex style={{ paddingTop: 10 }}>
            <Card title={<span><AreaChartOutlined style={{ marginRight: 8 }} />每日LOGS統計圖</span>} style={{ width: 1100 }}>
            <Flex style={{height:495}}>
            <Line {...config} />
            </Flex>
            </Card>
        </Flex>
    );
};

export default UserLogsCountGraphCard;