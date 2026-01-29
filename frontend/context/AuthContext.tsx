'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../lib/api';
import { useRouter, usePathname } from 'next/navigation';

interface User {
    id: number;
    email: string;
    name: string;
    profile_completed: boolean;
    current_stage: string;
}

interface AuthContextType {
    user: User | null;
    loading: boolean;
    login: (token: string, user: User) => void;
    logout: () => void;
    refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
    user: null,
    loading: true,
    login: () => { },
    logout: () => { },
    refreshUser: async () => { },
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();
    const pathname = usePathname();

    const refreshUser = async () => {
        try {
            const { data } = await api.get('/auth/me');
            setUser(data);
        } catch (error) {
            console.error("Failed to fetch user", error);
            logout();
        }
    };

    useEffect(() => {
        const initAuth = async () => {
            const token = localStorage.getItem('token');
            if (token) {
                try {
                    const { data } = await api.get('/auth/me');
                    setUser(data);
                } catch (error) {
                    localStorage.removeItem('token');
                }
            }
            setLoading(false);
        };
        initAuth();
    }, []);

    const login = (token: string, userData: User) => {
        localStorage.setItem('token', token);
        setUser(userData);

        // Explicit Redirection Rule
        if (!userData.profile_completed) {
            router.push('/onboarding');
        } else {
            router.push('/dashboard');
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        setUser(null);
        router.push('/login');
    };

    // Route Protection Logic (Client Side)
    useEffect(() => {
        if (loading) return;

        const isPublic = ['/', '/login', '/signup'].includes(pathname);

        if (!user && !isPublic) {
            router.push('/login');
            return;
        }

        if (user) {
            if (pathname === '/login' || pathname === '/signup') {
                if (!user.profile_completed) router.push('/onboarding');
                else router.push('/dashboard');
            }

            if (pathname.startsWith('/dashboard') && !user.profile_completed) {
                router.push('/onboarding');
            }

            if (pathname.startsWith('/onboarding') && user.profile_completed) {
                router.push('/dashboard');
            }
        }
    }, [user, loading, pathname]);

    return (
        <AuthContext.Provider value={{ user, loading, login, logout, refreshUser }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
