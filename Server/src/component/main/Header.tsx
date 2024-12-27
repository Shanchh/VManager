import { Flex, Layout } from 'antd';
import UserShow from './UserShow';
import { useNavigate } from 'react-router-dom';
import { UnorderedListOutlined } from '@ant-design/icons';

const { Header, } = Layout;

interface MainHeaderProps {
    isMobile: boolean;
    setOptionListOpen: (value: boolean) => void;
    optionListOpen: boolean;
}

const MainHeader: React.FC<MainHeaderProps> = ({ optionListOpen, isMobile, setOptionListOpen }) => {
    const navigate = useNavigate();

    const navigateToHome = () => {
        navigate("/");
    };

    const onClick = () => {
        setOptionListOpen(!optionListOpen);
    };

    return (
        <Header style={{
            display: 'flex',
            alignItems: 'center',
            backgroundColor: '#f6f8f5',
            height: '50px',
            borderBottom: '2px solid #ffffff',
            padding: '0',
        }}>
            <Flex gap={20} >
                <div onClick={navigateToHome} style={{ marginLeft: 18, fontSize: 34, fontWeight: 'bold', fontFamily: "Lucida Console, 微軟正黑體, 新細明體, sans-serif" }}>VManager</div>
                {isMobile ? (
                    <UnorderedListOutlined style={{ fontSize: 25 }} onClick={() => onClick()} />
                ) : null}
            </Flex>
            <div style={{ marginLeft: 'auto', paddingRight: '24px' }}><UserShow /></div>
        </Header>
    )
}

export default MainHeader