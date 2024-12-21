import { Badge, Button, Flex, Popconfirm, Table, Tag } from 'antd';
import React, { useState } from 'react';
import type { TableProps } from 'antd';
import { Account } from '../../type';

interface AccountListTableProps {
    data: Account[];
}

type TableRowSelection<T extends object = object> = TableProps<T>['rowSelection'];

const AccountListTable: React.FC<AccountListTableProps> = ({ data }) => {
    const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);

    const roleMap: Record<string, { color: string; label: string }> = {
        user: { color: "#efb01d", label: "員工" },
        admin: { color: "#b22222", label: "管理員" },
        owner: { color: "#40e0d0", label: "管理員" },
    };

    const columns: TableProps<Account>['columns'] = [
        {
            title: '暱稱',
            dataIndex: 'nickname',
            key: 'nickname',
            align: 'center',
        },
        {
            title: '身分組',
            key: 'role',
            dataIndex: 'role',
            align: 'center',
            render: (role: string) => {
                const roleInfo = roleMap[role];
                if (roleInfo) {
                    return <Tag color={roleInfo.color}>{roleInfo.label}</Tag>;
                }
                return "Error";
            },
        },
        {
            title: '信箱',
            dataIndex: 'email',
            key: 'email',
            align: 'center',
        },
        {
            title: '創建日期',
            key: 'createAt',
            align: 'center',
            render: (data: Account) => {
                const date = new Date(data.createAt * 1000);
                const year = date.getFullYear();
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const day = String(date.getDate()).padStart(2, '0');
                return `${year}年${month}月${day}日`;
            },
        },
        {
            title: '虛擬機',
            key: 'VMisCreate',
            align: 'center',
            render: (data: Account) => (
                data.VMisCreate ? (
                    <Badge status="success" text="已註冊" />
                ) : (
                    <Badge status="error" text="尚未註冊" />
                )
            ),
        },
        {
            title: '總連線時間',
            key: 'heartbeatCount',
            dataIndex: 'heartbeatCount',
            align: 'center',
            render: (heartbeatCount: number) => {
                if (!heartbeatCount) return '尚未連線';

                const totalSeconds = heartbeatCount * 5;
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
            title: '操作',
            key: 'action',
            align: 'center',
            render: (data: Account) => (
                <Flex justify="center" align="center" gap={5}>
                    <Popconfirm placement="top" title="刪除資料庫" description={`確定要重製嗎？`} okText="確認" cancelText="取消">
                        <Button
                            type="default"
                            style={{ height: 25, width: 45 }}
                        >重製
                        </Button>
                    </Popconfirm>
                    <Popconfirm placement="top" title="刪除資料庫" description={`確定要刪除嗎？`} okText="確認" cancelText="取消">
                        <Button
                            type="default"
                            style={{ height: 25, width: 45 }}
                        >刪除
                        </Button>
                    </Popconfirm>
                </Flex>
            ),
        },
    ];

    const onSelectChange = (newSelectedRowKeys: React.Key[]) => {
        setSelectedRowKeys(newSelectedRowKeys);
    };

    const rowSelection: TableRowSelection<Account> = {
        selectedRowKeys,
        onChange: onSelectChange,
        columnWidth: '60px',
        selections: [
            {
                key: 'selectAll',
                text: '選取全部',
                onSelect: () => {
                    setSelectedRowKeys(data.map((item) => item._id));
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

    const [pageSize, setPageSize] = useState(10);
    const rowHeight = 57;

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
            rowKey={(record) => record._id}
        />
    )
}

export default AccountListTable