import React, { useState, useEffect } from 'react'
import { Account } from '../../../type'
import { get_all_account_data } from '../../api/ProcessApi';
import { ReloadOutlined, UserOutlined, MailOutlined, SearchOutlined } from '@ant-design/icons';
import { Button, Col, Flex, Row, Spin, Form, Radio, Input, DatePicker, Select } from 'antd';
import AccountListTable from '../../component/AccountListTable';

type Filter = {
    VMIsCreate: string;
    createDate: any[];
    email: string;
    nickname: string;
    type: string;
};

const UserManage = () => {
    const [tableLoading, setTableLoading] = useState<boolean>(false);
    const [accountListData, setAccountListData] = useState<Account[]>([]);
    const [filteredData, setFilteredData] = useState<Account[]>([]);
    const [searchLoading, setSearchLoading] = useState<boolean>(false);
    const [searchRole, setSearchRole] = useState<string>("all");

    const { RangePicker } = DatePicker;

    const refreshData = async () => {
        setTableLoading(true);
        const data = await get_all_account_data();
        setAccountListData(data);
        setFilteredData(data);
        setTableLoading(false);
    }

    const handleDelete = (id: string) => {
        setFilteredData(filteredData.filter(account => account._id !== id));
    };

    const handleModifyRole = (id: string, newRole: string) => {
        setFilteredData(filteredData.map(account => {
            if (account._id === id) {
                return { ...account, role: newRole };
            }
            return account;
        }));
    };

    useEffect(() => {
        refreshData();
    }, []);

    const all_admin_role = ['admin', 'owner'];

    const clearSearch = () => {
        setSearchRole("all");
        setFilteredData(accountListData);
    };

    const onFinish = (values: Filter) => {
        console.log(values);
        setSearchLoading(true);
        const { nickname, email, createDate, VMIsCreate } = values;

        const filtered = accountListData.filter((item) => {
            const matchType = searchRole === 'all' || (searchRole === 'all-admin' && all_admin_role.includes(item.role)) || searchRole === item.role;
            const matchNickname = nickname ? item.nickname.includes(nickname) : true;
            const matchEmail = email ? item.email.includes(email) : true;

            const createAt = item.createAt * 1000;
            const matchDate = !createDate || (createDate[0].startOf('day').valueOf() <= createAt && createAt <= createDate[1].endOf('day').valueOf());

            const matchVMIsCreate = VMIsCreate === 'all' || VMIsCreate == 'true' && item.VMisCreate || VMIsCreate == 'false' && !item.VMisCreate;

            return matchType && matchNickname && matchEmail && matchDate && matchVMIsCreate;
        });

        setFilteredData(filtered);
        setSearchLoading(false);
    };

    return (
        <Flex>
            <Flex vertical justify='center' align='center' gap={10} style={{ width: '100%' }}>
                <Form
                    name="user_search"
                    layout="vertical"
                    onFinish={(values) => onFinish(values)}
                    style={{ width: '100%', padding: '0 10px 0 10px' }}
                    initialValues={{
                        email: '',
                        password: '',
                    }}
                >
                    <Row justify="start" gutter={18}>
                        <Col>
                            <Form.Item>
                                <Flex justify="start" align="center" gap={5}>
                                    <h3>身分類型：</h3>
                                    <Select
                                        size="middle"
                                        style={{ width: 180 }}
                                        value={searchRole}
                                        onChange={(value) => setSearchRole(value)}
                                        defaultValue={"all"}
                                        options={[
                                            { value: 'all', label: '全選' },
                                            { value: 'all-admin', label: '管理員' },
                                            { value: 'administrative', label: '行政' },
                                            { value: 'list', label: '名單部' },
                                            { value: 'oldSales', label: '回客' },
                                            { value: 'newSales', label: '新客' },
                                            { value: 'user', label: '員工' },
                                        ]}
                                    />
                                </Flex>
                            </Form.Item>
                        </Col>
                        <Col>
                            <Form.Item name="nickname" initialValue={''}>
                                <Flex justify="start" align="center" gap={10}>
                                    <h3>暱稱：</h3>
                                    <Input placeholder="請輸入暱稱" prefix={<UserOutlined />} style={{ width: 200 }} />
                                </Flex>
                            </Form.Item>
                        </Col>
                        <Col>
                            <Form.Item name="email" rules={[{ type: 'email', message: '請輸入有效的信箱!' }]} initialValue={''}>
                                <Flex justify="start" align="center" gap={10}>
                                    <h3>信箱：</h3>
                                    <Input placeholder="請輸入信箱" prefix={<MailOutlined />} style={{ width: 280 }} />
                                </Flex>
                            </Form.Item>
                        </Col>
                        <Col>
                            <Flex justify="start" align="center" gap={10}>
                                <h3>創建日期：</h3>
                                <Form.Item name="createDate" style={{ margin: 0 }}>
                                    <RangePicker size="middle" placeholder={['選擇開始日期', '選擇結束日期']} />
                                </Form.Item>
                            </Flex>
                        </Col>
                        <Col>
                            <Form.Item name="VMIsCreate" initialValue={'all'}>
                                <Flex justify="start" align="center" gap={5}>
                                    <h3>虛擬機：</h3>
                                    <Radio.Group defaultValue="all">
                                        <Radio.Button value="all">全選</Radio.Button>
                                        <Radio.Button value={true}>已註冊</Radio.Button>
                                        <Radio.Button value={false}>未註冊</Radio.Button>
                                    </Radio.Group>
                                </Flex>
                            </Form.Item>
                        </Col>
                    </Row>
                    <Flex justify="end" style={{ paddingTop: 10 }} gap={10}>
                        <Button htmlType="submit" type="primary" icon={<SearchOutlined />} loading={searchLoading}>
                            條件查詢
                        </Button>
                        <Button htmlType="reset" type="default" onClick={() => clearSearch()}>
                            清除條件
                        </Button>
                    </Flex>
                </Form>

                <Flex justify='flex-start' align='center' style={{ width: '100%' }}>
                    <Button color="default" variant="outlined" icon={<ReloadOutlined />} onClick={() => refreshData()}>刷新表格</Button>
                </Flex>
                {tableLoading ? (
                    <Flex justify='center' align='center' style={{ height: '50vh' }}>
                        <Spin size="large" />
                    </Flex>
                ) : (
                    <AccountListTable data={filteredData} onDelete={handleDelete} onModifyRole={handleModifyRole}></AccountListTable>
                )}
            </Flex>
        </Flex>
    )
}

export default UserManage