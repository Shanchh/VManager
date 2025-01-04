import React, { useEffect, useState } from 'react'
import { get_my_data } from '../../api/ProcessApi';
import { Account } from '../../../type';
import MyProfileCard from '../../component/MyProfileCard';
import MyRecentActivitiesCard from '../../component/MyRecentActivitiesCard';
import { Col, Flex, Row } from 'antd';
import QuickActionsCard from '../../component/QuickActionsCard';
import { useAuth } from '../../auth/AuthProvider';

const MyProfile = () => {
  const [profile, setProfile] = useState<Account | null>(null);

  const { userProfile } = useAuth()

  const refreshData = async () => {
    const data = await get_my_data();
    setProfile(data);
  }

  useEffect(() => {
    refreshData();
  }, []);

  return (
    <Flex>
      <Row justify="start" gutter={10}>
        <Col>
          <Flex vertical gap={10} style={{ paddingBottom: 10 }}>
            <MyProfileCard profile={profile} refreshData={refreshData} />
          </Flex>
        </Col>
        <Col>
          <MyRecentActivitiesCard />
        </Col>
      </Row>
    </Flex>
  )
}

export default MyProfile