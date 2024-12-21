import React from "react";
import { Breadcrumb, Layout } from "antd";
import { useLocation, Link } from "react-router-dom";

const breadcrumbNameMap: Record<string, string> = {
    "/": "首頁",
    "/my-profile": "個人頁面",
    "/setting": "設定",
};

const MainBreadcrumb: React.FC = () => {
    const location = useLocation();

    const pathSnippets = location.pathname.split("/").filter((i) => i);
    const breadcrumbItems = pathSnippets.map((_, index) => {
        const url = `/${pathSnippets.slice(0, index + 1).join("/")}`;
        const isLast = index === pathSnippets.length - 1;
        return (
            <Breadcrumb.Item key={url}>
                {isLast ? (
                    breadcrumbNameMap[url] || url
                ) : (
                    <Link to={url}>{breadcrumbNameMap[url] || url}</Link>
                )}
            </Breadcrumb.Item>
        );
    });

    const fullBreadcrumbItems = [
        <Breadcrumb.Item key="home">
            <Link to="/">首頁</Link>
        </Breadcrumb.Item>,
        ...breadcrumbItems,
    ];

    return (
        <Breadcrumb style={{ margin: "12px 0" }}>{fullBreadcrumbItems}</Breadcrumb>
    );
};

export default MainBreadcrumb;