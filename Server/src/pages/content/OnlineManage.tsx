import React, { useState, useEffect } from 'react'
import { Client } from '../../types/type'
import { ReloadOutlined, UserOutlined, SearchOutlined, DesktopOutlined } from '@ant-design/icons';
import { Button, Flex, Spin, Form, Row, Col, Radio, Input, Select } from 'antd';
import { list_connected } from '../../api/ProcessApi';
import OnlineClientTable from '../../component/OnlineClientTable';
import CustomCommandBtn from '../../component/CustomCommandBtn';

type SelectOption = {
    value: string;
    label: string;
}

const OnlineManage = () => {
    const [tableLoading, setTableLoading] = useState<boolean>(false);
    const [connectedListData, setConnectedListData] = useState<Client[]>([]);
    const [sorterType, setSorterType] = useState('none');
    const [sorterValue, setSorterValue] = useState('none');
    const [filteredData, setFilteredData] = useState<Client[]>([]);
    const [searchRole, setSearchRole] = useState<string>("all");

    const NoneSorterOption = [
        { value: 'none', label: '選擇排序方式' }
    ];

    const [selectSorterOption, setSelectSorterOption] = useState<SelectOption[]>(NoneSorterOption);

    const refreshData = async () => {
        setTableLoading(true);
        const data: Client[] = await list_connected()
        setConnectedListData(data);
        setFilteredData(data);
        setTableLoading(false);
    }

    useEffect(() => {
        refreshData();
    }, []);

    const all_admin_role = ['admin', 'owner'];

    const onResetSearch = () => {
        setSorterType('none');
        setSorterValue('none');
        setSearchRole("all");
        setFilteredData(connectedListData);
    }

    const selectOption = [
        { value: 'none', label: '選擇種類' },
        { value: 'time', label: '連線時間' },
        { value: 'long', label: '連線時長' }
    ]

    const handleChange = (value: string) => {
        setSorterType(value);
        if (value === 'time') {
            setSelectSorterOption(TimeSorterOption);
        } else if (value === 'long') {
            setSelectSorterOption(LongSorterOption);
        } else if (value === 'none') {
            setSelectSorterOption(NoneSorterOption);
        }
        setSorterValue('none')
    };

    const TimeSorterOption = [
        { value: 'none', label: '選擇排序方式' },
        { value: 'descending', label: '從遠到近' },
        { value: 'ascending', label: '從近到遠' }
    ]

    const LongSorterOption = [
        { value: 'none', label: '選擇排序方式' },
        { value: 'ascending', label: '從短到長' },
        { value: 'descending', label: '從長到短' }
    ];

    const onFinish = (values: any) => {
        const { nickname, ip, VMstatus } = values;

        const filtered = connectedListData.filter((item) => {
            const matchType =
                searchRole === 'all' ||
                (searchRole === 'all-admin' && all_admin_role.includes(item.role || '')) ||
                item.role === searchRole;

            const matchNickname = nickname ? item.username.includes(nickname) : true;
            const matchIp = ip ? item.ip.includes(ip) : true;

            const matchVMIsCreate =
                VMstatus === 'all' ||
                (VMstatus === 'true' && item.vmcount >= 1) ||
                (VMstatus === 'false' && item.vmcount === 0);

            return matchType && matchNickname && matchIp && matchVMIsCreate;
        });

        let sortedData = [...filtered];

        if (sorterType && sorterValue !== 'none') {
            const sortKey = sorterType === 'time' ? 'connected_at' : 'connection_duration';
            const sortOrder = sorterValue === 'ascending' ? 1 : -1;

            sortedData.sort((a, b) => (a[sortKey] - b[sortKey]) * sortOrder);
        }

        setFilteredData(sortedData);
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
                            <Form.Item>
                                <Flex justify="start" align="center" gap={10}>
                                    <h3>排序：</h3>
                                    <Select
                                        size="middle"
                                        defaultValue="none"
                                        value={sorterType}
                                        style={{ width: 120 }}
                                        onChange={(value) => handleChange(value)}
                                        options={selectOption}
                                    />

                                    <Select
                                        size="middle"
                                        defaultValue="none"
                                        style={{ width: 128 }}
                                        options={selectSorterOption}
                                        value={sorterValue}
                                        onChange={(value) => {
                                            setSorterValue(value);
                                        }}
                                    />
                                </Flex>
                            </Form.Item>
                        </Col>
                        <Col>
                            <Form.Item name="VMstatus" initialValue={'all'}>
                                <Flex justify="start" align="center" gap={5}>
                                    <h3>虛擬機狀態：</h3>
                                    <Radio.Group defaultValue="all">
                                        <Radio.Button value="all">全選</Radio.Button>
                                        <Radio.Button value={true}>啟動中</Radio.Button>
                                        <Radio.Button value={false}>尚未開機</Radio.Button>
                                    </Radio.Group>
                                </Flex>
                            </Form.Item>
                        </Col>
                        <Col>
                            <Form.Item name="ip" initialValue={''}>
                                <Flex justify="start" align="center" gap={10}>
                                    <h3>IP位置：</h3>
                                    <Input placeholder="請輸入IP位置" prefix={<DesktopOutlined />} style={{ width: 280 }} />
                                </Flex>
                            </Form.Item>
                        </Col>
                    </Row>
                    <Flex justify="end" style={{ paddingTop: 10 }} gap={10}>
                        <Button htmlType="submit" type="primary" icon={<SearchOutlined />}>
                            條件查詢
                        </Button>
                        <Button htmlType="reset" type="default" onClick={() => onResetSearch()}>
                            清除條件
                        </Button>
                    </Flex>
                </Form>

                <Flex style={{ width: '100%' }}>
                    <Flex justify='flex-start' align='center' gap={5} style={{ width: '50%' }}>
                        <Button color="default" variant="outlined" icon={<ReloadOutlined />} onClick={() => refreshData()}>刷新表格</Button>
                        <div style={{ fontSize: 18 }}>
                            <UserOutlined />
                            {connectedListData.length}
                        </div>
                    </Flex>
                    <Flex justify='flex-end' align='center' gap={5} style={{ width: '50%' }}>
                        <CustomCommandBtn connectedListData={connectedListData}/>
                    </Flex>
                </Flex>

                {tableLoading ? (
                    <Flex justify='center' align='center' style={{ height: '50vh' }}>
                        <Spin size="large" />
                    </Flex>
                ) : (
                    <OnlineClientTable data={filteredData} />
                )}
            </Flex>
        </Flex>
    )
}

export default OnlineManage