import { Layout } from 'antd';
import UserShow from './UserShow';

const { Header, } = Layout;

const MainHeader = () => {
    return (
        <Header style={{
            display: 'flex',
            alignItems: 'center',
            backgroundColor: '#f6f8f5',
            height: '50px',
            borderBottom: '2px solid #ffffff',
            padding: '0',
        }}>
            <div style={{ marginLeft: 18, fontSize: 34, fontWeight: 'bold', fontFamily: "Lucida Console, 微軟正黑體, 新細明體, sans-serif" }}>VManager</div>
            <div style={{ marginLeft: 'auto', paddingRight: '24px'}}><UserShow /></div>
        </Header>
    )
}

export default MainHeader