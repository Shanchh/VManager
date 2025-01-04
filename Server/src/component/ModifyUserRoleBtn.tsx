import { Button, Flex, message, Modal, Select } from 'antd'
import React, { useState } from 'react'
import { UserOutlined } from '@ant-design/icons';
import { Account } from '../../type';
import { modify_user_role } from '../api/ProcessApi';

interface ModifyUserRoleBtnProps {
    data: Account;
    onModifyRole : (id: string, newRole: string) => void;
}

const ModifyUserRoleBtn: React.FC<ModifyUserRoleBtnProps> = ({ data, onModifyRole }) => {
    const [modalOpen, setModalOpen] = useState<boolean>(false);
    const [loading, setLoading] = useState<boolean>(false);
    const [selectRole, setSelectRole] = useState<string>("user");

    const onConfirm = async () => {
        setLoading(true);
        try {
            const command = {
                role: selectRole,
                objId: data._id
            }
            const r = await modify_user_role(command);
            message.success(`更動成功！${data.nickname}`);
            onModifyRole(data._id, selectRole);
        } catch (error: any) {
            console.error(error);
            message.error("更動失敗！");
        } finally {
            setModalOpen(false);
            setLoading(false);
        }
    };

    return (
        <Flex justify="center" align="center" gap={5}>
            <Button
                type="default"
                style={{ height: 25, width: 45 }}
                onClick={() => setModalOpen(true)}
            >組別
            </Button>
            <Modal
                centered
                title={
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <UserOutlined style={{ color: 'orange' }} />
                        <span>編輯身分組 {data.nickname}</span>
                    </div>
                }
                open={modalOpen}
                width={315}
                onCancel={() => setModalOpen(false)}
                footer={null}
            >
                <Flex justify="start" align="center" gap={5}>
                    <h3>調整身分：</h3>
                    <Select
                        size="middle"
                        style={{ width: 180 }}
                        value={selectRole}
                        onChange={(value) => setSelectRole(value)}
                        defaultValue={"all"}
                        options={[
                            { value: 'user', label: '員工' },
                            { value: 'newSales', label: '新客' },
                            { value: 'oldSales', label: '回客' },
                            { value: 'list', label: '名單部' },
                            { value: 'administrative', label: '行政' },
                            { value: 'admin', label: '管理員' },
                        ]}
                    />
                </Flex>
                <Flex justify='flex-end' gap={5} style={{ paddingTop: 10 }}>
                    <Button color="primary" variant="solid" style={{ fontSize: 16 }} loading={loading} onClick={() => onConfirm()}>
                        送出
                    </Button>
                    <Button color="default" variant="outlined" style={{ fontSize: 16 }} onClick={() => setModalOpen(false)}>
                        取消
                    </Button>
                </Flex>
            </Modal>
        </Flex>
    )
}

export default ModifyUserRoleBtn