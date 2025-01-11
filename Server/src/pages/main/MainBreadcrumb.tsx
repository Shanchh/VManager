import React from "react";
import { Breadcrumb, Layout } from "antd";
import { useLocation, Link } from "react-router-dom";

const breadcrumbNameMap: Record<string, string> = {
    "/": "首頁",
    "/my-profile": "個人頁面",
    "/management": "管理功能",
    "/management/dashboard": "儀表板",
    "/management/user-manage": "帳號管理",
    "/management/online-manage": "線上裝置管理",
    "/backend-interface": "後臺功能",
    "/backend-interface/server-logs": "運行日誌",
    "/backend-interface/search-user-logs": "查詢用戶日誌",
    "/setting": "設定",
};

const MainBreadcrumb: React.FC = () => {
    const location = useLocation();

    const pathSnippets = location.pathname.split("/").filter((i) => i);
    const breadcrumbItems = [
        {
            title: <Link to="/">首頁</Link>,
            key: "home",
        },
        ...pathSnippets.map((_, index) => {
            const url = `/${pathSnippets.slice(0, index + 1).join("/")}`;
            const isLast = index === pathSnippets.length - 1;
            return {
                title: isLast ? breadcrumbNameMap[url] || url : <Link to={url}>{breadcrumbNameMap[url] || url}</Link>,
                key: url,
            };
        }),
    ];

    return <Breadcrumb style={{ margin: "12px 0" }} items={breadcrumbItems} />;
};

export default MainBreadcrumb;
