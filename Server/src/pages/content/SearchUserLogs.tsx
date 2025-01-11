import React, { useEffect, useState } from 'react'
import { TeamOutlined } from '@ant-design/icons';
import { Button, Card, Col, DatePicker, Flex, message, Row, Select } from 'antd'
import dayjs from 'dayjs';
import { get_all_account_data, get_user_log_counts_data, get_user_log_data } from '../../api/ProcessApi';
import { Account } from '../../../type';
import UserLogsCountGraphCard from '../../component/UserLogsCountGraphCard';
import UserLogsCard from '../../component/UserLogsCard';

const dateFormat = 'YYYY-MM-DD';

const SearchUserLogs = () => {
    const today = dayjs();
    const [selectedDate, setSelectedDate] = useState(today);
    const [selectedLogType, setSelectLogType] = useState<string>('all');
    const [userOptions, setUserOptions] = useState<any[]>([{ value: 'all', label: '全選' }]);
    const [selectedUser, setSelectedUser] = useState<string>('all');

    const [logCountData, setLogCountData] = useState([]);
    const [logData, setLogData] = useState([]);

    const convertToOptions = (Account: Account[]) => {
        return Account.map((Account) => ({
            value: Account._id,
            label: Account.nickname,
        }));
    };

    const handleDateChange = (date: any) => {
        if (date) {
            setSelectedDate(date.add(1, 'day'));
        }
    };

    const refreshUserData = async () => {
        try {
            const data = await get_all_account_data();
            await submitLogSearch();
            const options = convertToOptions(data);
            setUserOptions([{ value: 'all', label: '全選' }, ...options]);
        } catch (error) {
            message.error('獲取用戶列表失敗');
        }
    };

    useEffect(() => {
        refreshUserData();
    }, []);

    const submitLogSearch = async () => {
        try {
            const command1 = {
                date: selectedDate,
                userId: selectedUser
            }
            const command2 = {
                date: selectedDate,
                userId: selectedUser,
                logType: selectedLogType
            }
            const log_data = await get_user_log_data(command2);
            const log_counts_data = await get_user_log_counts_data(command1);
            setLogData(log_data);
            setLogCountData(log_counts_data);
        } catch (error) {
            message.error('獲取數據失敗');
        }
    };

    return (
        <Row justify="start" gutter={18}>
            <Col>
                <Card
                    title={<span><TeamOutlined style={{ marginRight: 8 }} />搜尋功能</span>}
                    style={{ width: 1100 }}
                >
                    <Flex justify='start' align='center' gap={20}>
                        <Flex justify='start' align='center'>
                            <h3>日期：</h3>
                            <DatePicker
                                placeholder='請選擇日期'
                                defaultValue={dayjs(today, dateFormat)}
                                minDate={dayjs('2025-01-06', dateFormat)}
                                maxDate={dayjs(today, dateFormat)}
                                onChange={handleDateChange}
                            />
                        </Flex>

                        <Flex justify='start' align='center'>
                            <h3>人員：</h3>
                            <Select
                                style={{ width: 120 }}
                                showSearch placeholder='請選擇對象'
                                defaultValue={'all'}
                                value={selectedUser}
                                onChange={(value) => setSelectedUser(value)}
                                options={userOptions}
                                optionFilterProp="label"
                            >
                            </Select>
                        </Flex>

                        <Flex justify='start' align='center'>
                            <h3>日誌類型：</h3>
                            <Select
                                style={{ width: 120 }}
                                defaultValue={'all'}
                                value={selectedLogType}
                                onChange={(value) => setSelectLogType(value)}
                                options={[
                                    { value: 'all', label: '全選' },
                                    { value: 'INFO', label: '資訊' },
                                    { value: 'WARN', label: '警告' },
                                    { value: 'ERROR', label: '錯誤' },
                                    { value: 'DEBUG', label: '排錯' },
                                ]}
                            >
                            </Select>
                        </Flex>

                        <Flex justify='end' align='center' style={{ flex: 1 }}>
                            <Button color="primary" variant="outlined" onClick={() => submitLogSearch()}>送出查詢</Button>
                        </Flex>
                    </Flex>
                </Card>
                <UserLogsCountGraphCard data={logCountData} />
            </Col>
            <Col>
                <UserLogsCard logsData={logData}/>
            </Col>
        </Row>
    )
}

export default SearchUserLogs