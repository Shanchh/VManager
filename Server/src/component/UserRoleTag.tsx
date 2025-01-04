import React from 'react';
import { Tag } from 'antd';

interface UserRoleTagProps {
    role?: string;
}

const UserRoleTag: React.FC<UserRoleTagProps> = ({ role }) => {
    const roleMap: Record<string, { color: string; label: string }> = {
        owner: { color: "#40e0d0", label: "管理員" },
        admin: { color: "#b22222", label: "管理員" },
        list: { color: "#2169ce", label: "名單部" },
        administrative: { color: "#ed215f", label: "行政" },
        newSales: { color: "#13d731", label: "新客" },
        oldSales: { color: "#11a327", label: "回客" },
        user: { color: "#efb01d", label: "員工" }
    };

    if (!role) {
        return <Tag color="yellow">Unknown</Tag>;
    }

    const roleInfo = roleMap[role];
    if (roleInfo) {
        return <Tag color={roleInfo.color}>{roleInfo.label}</Tag>;
    }
    return <Tag color="red">Error</Tag>;
};

export default UserRoleTag;