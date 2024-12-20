import React, { createContext, useContext, useEffect, useState } from 'react'
import { auth } from "./FirebaseConfig";
import { User } from "firebase/auth";
import axios from "axios";
import { get_my_profile } from "../api/ProcessApi";

interface AuthContextProps {
    children: React.ReactNode
}

interface UserProfile {
    nickname: string,
    email: string,
    role: string
}

interface AuthContextType {
    user: User,
    setUser: React.Dispatch<any>,
    authIsLoading: boolean,
    userProfile: UserProfile | null
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

const AuthProvider: React.FC<AuthContextProps> = ({ children }) => {
    const [user, setUser] = useState<any | null>(null);
    const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
    const [authIsLoading, setAuthIsLoading] = useState(true);

    // 登入後初始化
    const initializeAuth = async (user: User) => {
        const idToken = await user.getIdToken();
        axios.defaults.headers.common.Authorization = `Bearer ${idToken}`;

        setInterval(async () => {
            const idToken = await user.getIdToken(true);
            axios.defaults.headers.common.Authorization = `Bearer ${idToken}`;
            console.log("更新token成功!");
        }, (10 * 60) * 1000);

        setInterval(() => {
            window.location.reload();
            console.log("刷新網頁!");
        }, (120 * 60) * 1000);

        fetchUserProfile();
    }

    const fetchUserProfile = async () => {
        try {
            const profile = await get_my_profile();
            setUserProfile(profile);
            setAuthIsLoading(false);
        } catch (error) {
            console.error("獲取用戶資料失敗, 0.5秒後重試...");
            setTimeout(fetchUserProfile, 500);
        }
    };

    // 掛載Auth監聽器
    useEffect(() => {
        auth.onAuthStateChanged((user) => {
            setUser(user);

            if (user)
                initializeAuth(user);
            else
                setAuthIsLoading(false);
        });
    }, []);

    return (
        <AuthContext.Provider value={{ user, setUser, authIsLoading, userProfile }}>
            {children}
        </AuthContext.Provider>
    )
}

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context)
        throw new Error("Error");
    return context;
}

export default AuthProvider