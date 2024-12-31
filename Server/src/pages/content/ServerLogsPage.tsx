import React from 'react'
import LogsCard from '../../component/LogsCard'
import { Col, Flex, Row } from 'antd'

const ServerLogsPage = () => {
    return (
        <Row justify="start" gutter={18}>
            <Col>
                <LogsCard level='INFO' title='資訊日誌' />
            </Col>
            <Col>
                <LogsCard level='WARN' title='警告日誌' />
            </Col>
            <Col>
                <LogsCard level='ERROR' title='錯誤日誌' />
            </Col>
        </Row>
    )
}

export default ServerLogsPage