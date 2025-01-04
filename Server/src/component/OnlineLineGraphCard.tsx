import React, { useEffect, useState } from 'react';
import { Line } from '@ant-design/charts';
import { Card } from 'antd';
import { AreaChartOutlined } from '@ant-design/icons';
import { get_average_daily_count } from '../api/ProcessApi';

const OnlineLineGraphCard: React.FC = () => {
  const [data, setData] = useState<any[]>([]);

  const transformDataToChinese = (rawData: any[]) => {
    return rawData.map(item => ({
      日期: item.date,
      平均在線數: item.average_online_count,
    }));
  };

  const config = {
    data: transformDataToChinese(data),
    padding: 'auto',
    xField: '日期',
    yField: '平均在線數',
    point: {
      size: 5,
      shape: 'diamond',
      style: {
        fill: 'white',
        stroke: '#2593fc',
        lineWidth: 2,
      },
    },
    label: {
      style: {
        fill: '#595959',
      },
    },
    smooth: true,
  };

  const refreshData = async () => {
    const r = await get_average_daily_count();
    setData(r);
  };

  useEffect(() => {
    refreshData();
  }, []);

  return (
    <Card title={<span><AreaChartOutlined style={{ marginRight: 8 }} />每日平均線上裝置數</span>} style={{ width: 800 }}>
      <Line {...config} />
    </Card>
  );
};

export default OnlineLineGraphCard;
