import React, { useState, useEffect } from 'react'
import { Client } from '../../types/type'
import { ReloadOutlined, UserOutlined, SearchOutlined, DesktopOutlined } from '@ant-design/icons';
import { Button, Flex, Spin, Form, Row, Col, Radio, Input, Select } from 'antd';
import { list_connected } from '../../api/ProcessApi';
import OnlineClientTable from '../../component/OnlineClientTable';

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
        const { type, nickname, ip, VMstatus } = values;

        const filtered = connectedListData.filter((item) => {
            const matchType =
                type === 'all' ||
                (type === 'all-admin' && all_admin_role.includes(item.role || '')) ||
                item.role === type;

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
                            <Form.Item name="type" initialValue={'all'}>
                                <Flex justify="start" align="center" gap={5}>
                                    <h3>身分類型：</h3>
                                    <Radio.Group defaultValue="all">
                                        <Radio.Button value="all">全選</Radio.Button>
                                        <Radio.Button value="user">員工</Radio.Button>
                                        <Radio.Button value="all-admin">管理員</Radio.Button>
                                    </Radio.Group>
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

                <Flex justify='flex-start' align='center' gap={5} style={{ width: '100%' }}>
                    <Button color="default" variant="outlined" icon={<ReloadOutlined />} onClick={() => refreshData()}>刷新表格</Button>
                    <div style={{ fontSize: 18 }}>
                        <UserOutlined />
                        {connectedListData.length}
                    </div>
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