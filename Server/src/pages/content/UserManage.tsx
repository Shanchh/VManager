import React, { useState, useEffect } from 'react'
import { Account } from '../../../type'
import { get_all_account_data } from '../../api/ProcessApi';
import { ReloadOutlined } from '@ant-design/icons';
import { Button, Flex, Spin } from 'antd';
import AccountListTable from '../../component/AccountListTable';

const UserManage = () => {
    const [tableLoading, setTableLoading] = useState<boolean>(false);
    const [accountListData, setAccountListData] = useState<Account[]>([]);

    const refreshData = async () => {
        setTableLoading(true);
        const data = await get_all_account_data();
        setAccountListData(data);
        setTableLoading(false);
    }

    useEffect(() => {
        refreshData();
    }, []);

    return (
        <Flex>
            <Flex vertical justify='center' align='center' gap={10} style={{ width: '100%' }}>
                <Flex justify='flex-start' align='center' style={{ width: '100%'}}>
                    <Button color="default" variant="outlined" icon={<ReloadOutlined />} onClick={() => refreshData()}>刷新表格</Button>
                </Flex>
                {tableLoading ? (
                    <Flex justify='center' align='center' style={{ height: '50vh' }}>
                        <Spin size="large" />
                    </Flex>
                ) : (
                    <AccountListTable data={accountListData}></AccountListTable>
                )}
            </Flex>
        </Flex>
    )
}

export default UserManage