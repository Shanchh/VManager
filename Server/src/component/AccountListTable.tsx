import { Badge, Table } from 'antd';
import React, { useState } from 'react';
import type { TableProps } from 'antd';
import { Account } from '../../type';
import DeleteAccountBtn from './DeleteAccountBtn';
import UserRoleTag from './UserRoleTag';

interface AccountListTableProps {
    data: Account[];
}

type TableRowSelection<T extends object = object> = TableProps<T>['rowSelection'];

const AccountListTable: React.FC<AccountListTableProps> = ({ data }) => {
    const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
    const [accountData, setAccountData] = useState<Account[]>(data);

    const handleDelete = (id: string) => {
        setAccountData(accountData.filter(account => account._id !== id));
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
            align: 'center',
            render: (data: Account) => {
                return <UserRoleTag role={data.role} />
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
                <DeleteAccountBtn data={data} onDelete={handleDelete} />
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
            dataSource={accountData}
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