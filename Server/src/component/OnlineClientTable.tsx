import React, { useState } from 'react'
import { Client } from '../types/type';
import { Badge, Table, type TableProps } from 'antd';
import OnlineClientOperate from './OnlineClientOperate';
import UserRoleTag from './UserRoleTag';

interface OnlineClientTableProps {
    data: Client[];
}

type TableRowSelection<T extends object = object> = TableProps<T>['rowSelection'];

const OnlineClientTable: React.FC<OnlineClientTableProps> = ({ data }) => {
    const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);

    const onSelectChange = (newSelectedRowKeys: React.Key[]) => {
        setSelectedRowKeys(newSelectedRowKeys);
    };

    const rowSelection: TableRowSelection<Client> = {
        selectedRowKeys,
        onChange: onSelectChange,
        columnWidth: '60px',
        selections: [
            {
                key: 'selectAll',
                text: '選取全部',
                onSelect: () => {
                    setSelectedRowKeys(data.map((item) => item.client_id));
                },
            },
            {
                key: 'clear',
                text: '清空選取',
                onSelect: () => {
                    setSelectedRowKeys([]);
                },
            },
        ],
    };

    const columns: TableProps<Client>['columns'] = [
        {
            title: '暱稱',
            dataIndex: 'username',
            key: 'username',
            align: 'center',
        },
        {
            title: '身分組',
            key: 'role',
            align: 'center',
            render: (data: Client) => {
                return <UserRoleTag role={data.role}/>
            },
        },
        {
            title: 'IP位置',
            dataIndex: 'ip',
            key: 'ip',
            align: 'center',
        },
        {
            title: '連線時間',
            key: 'connected_at',
            align: 'center',
            render: (data: Client) => {
                const date = new Date(data.connected_at * 1000);
                const year = date.getFullYear();
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const day = String(date.getDate()).padStart(2, '0');
                const hours = String(date.getHours()).padStart(2, '0');
                const minutes = String(date.getMinutes()).padStart(2, '0');
                const seconds = String(date.getSeconds()).padStart(2, '0');
                return `${year}年${month}月${day}日 ${hours}時${minutes}分${seconds}秒`;
            },
        },
        {
            title: '連線時長',
            key: 'connection_duration',
            align: 'center',
            render: (data: Client) => {
                const totalSeconds = data.connection_duration;
                const months = Math.floor(totalSeconds / (30 * 24 * 60 * 60));
                const days = Math.floor(totalSeconds / (24 * 60 * 60)) % 30;
                const hours = Math.floor(totalSeconds / (60 * 60)) % 24;
                const minutes = Math.floor(totalSeconds / 60) % 60;
                const seconds = totalSeconds % 60;

                return [
                    months && `${months}月`,
                    days && `${days}天`,
                    hours && `${hours}時`,
                    minutes && `${minutes}分`,
                    seconds && `${seconds}秒`
                ].filter(Boolean).join('');
            },
        },
        {
            title: '虛擬機',
            key: 'vmcount',
            align: 'center',
            render: (data: Client) => (
                data.vmcount > 0 ? (
                    <Badge status="success" text="啟動中" />
                ) : (
                    <Badge status="error" text="關機狀態" />
                )
            ),
        },
        {
            title: '版本',
            dataIndex: 'version',
            key: 'version',
            align: 'center',
        },
        {
            title: '操作',
            key: 'action',
            align: 'center',
            render: (data: Client) => (
                <OnlineClientOperate data={data} />
            ),
        },
    ];

    const [pageSize, setPageSize] = useState(10);
    const rowHeight = 50;

    return (
        <Table
            components={{
                header: {
                    row: (props: React.HTMLAttributes<HTMLTableRowElement>) => (
                        <tr {...props} style={{ height: '25px' }} />
                    ),
                },
            }}
            scroll={{ x: 'max-content', y: '70vh' }}
            rowSelection={rowSelection}
            columns={columns}
            dataSource={data}
            pagination={{
                position: ['bottomLeft'],
                pageSize: pageSize,
                pageSizeOptions: ['10', '20', '50', '100', '9999'],
                showSizeChanger: true,
                onShowSizeChange: (_, size) => setPageSize(size),
            }}
            onRow={() => ({
                style: { height: rowHeight },
            })}
            rowKey={(record) => record.client_id}
        />
    )
}

export default OnlineClientTable