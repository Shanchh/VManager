import React from 'react'
import OnlineLineGraphCard from '../../component/OnlineLineGraphCard'
import { Col, Row } from 'antd'
import QuickActionsCard from '../../component/QuickActionsCard'

const ManageDashboard = () => {
    return (
        <Row justify="start" gutter={10}>
            <Col>
                <OnlineLineGraphCard />
            </Col>
            <Col>
                <QuickActionsCard />
            </Col>
        </Row>
    )
}

export default ManageDashboard