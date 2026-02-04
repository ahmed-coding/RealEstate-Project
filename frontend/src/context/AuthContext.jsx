import React, { createContext, useContext, useState, useEffect } from 'react';
import { login as apiLogin, signup as apiSignup, logout as apiLogout } from '../api/auth';
import client from '../api/client';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check if token exists and maybe validate it or fetch user profile
        // For now, we just assume if token exists, we are logged in.
        // Ideally, we should fetch /api/auth/profile or similar if available.
        if (token) {
            // Set default header
            client.defaults.headers.common['Authorization'] = `Token ${token}`;
            // Verify token? The API doesn't have a clear "me" endpoint in the snippets seen, 
            // effectively we might just decode JWT or wait for a 401 to clear it.
            // We'll set a dummy user object for now or decode the token if it's JWT.
            // Let's assume we store user info in localStorage too for simplicity or fetch it.
            const storedUser = localStorage.getItem('user');
            if (storedUser) {
                setUser(JSON.parse(storedUser));
            }
        } else {
            delete client.defaults.headers.common['Authorization'];
            setUser(null);
        }
        setLoading(false);
    }, [token]);

    const login = async (data) => {
        try {
            const response = await apiLogin(data);
            // Assuming response contains { token: '...', user: {...} } or similar.
            // We will need to adjust based on actual schema 'AuthToken'.
            // If schema is just { token: ... }, we need to know.
            // PROVISIONAL: We'll save the whole response as token if it's a string, or extract it.

            const authToken = response.token || response.access || response.data?.token;
            const userData = response.user || response.data?.user || { username: data.username }; // Fallback

            if (authToken) {
                localStorage.setItem('token', authToken);
                setToken(authToken);
            }

            if (userData) {
                localStorage.setItem('user', JSON.stringify(userData));
                setUser(userData);
            }

            return response;
        } catch (error) {
            throw error;
        }
    };

    const signup = async (data) => {
        try {
            const response = await apiSignup(data);
            // Does signup auto-login? 
            // Schema says: 201 returns UserAuth.
            return response;
        } catch (error) {
            throw error;
        }
    };

    const logout = async () => {
        try {
            // local cleanup first
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            setToken(null);
            setUser(null);
            await apiLogout();
        } catch (error) {
            console.error("Logout failed", error);
        }
    };

    return (
        <AuthContext.Provider value={{ user, token, login, signup, logout, loading }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
