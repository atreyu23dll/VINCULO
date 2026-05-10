import React, { createContext, useContext, useState, useEffect } from 'react';
import * as AuthSession from 'expo-auth-session';
import * as WebBrowser from 'expo-web-browser';
import * as SecureStore from 'expo-secure-store';
import { AUTH_CONFIG, KEYCLOAK_CONFIG } from '../constants/Auth';

WebBrowser.maybeCompleteAuthSession();

interface AuthContextType {
    user: any;
    token: string | null;
    login: () => Promise<void>;
    loginNativo: (username: string, pass: string) => Promise<{success: boolean, error?: string}>;
    register: (email: string, pass: string, nombre: string) => Promise<{success: boolean, error?: string}>;
    logout: () => Promise<void>;
    isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<any>(null);
    const [token, setToken] = useState<string | null>(null);
    const [refreshToken, setRefreshToken] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    // Cargar token al iniciar
    useEffect(() => {
        const loadStoredAuth = async () => {
            try {
                const storedToken = await SecureStore.getItemAsync('userToken');
                const storedUser = await SecureStore.getItemAsync('userData');
                if (storedToken) {
                    setToken(storedToken);
                    if (storedUser) setUser(JSON.parse(storedUser));
                }
            } catch (e) {
                console.error("Error cargando auth guardada", e);
            } finally {
                setIsLoading(false);
            }
        };
        loadStoredAuth();
    }, []);

    const [request, response, promptAsync] = AuthSession.useAuthRequest(
        {
            clientId: AUTH_CONFIG.clientId,
            redirectUri: AuthSession.makeRedirectUri(),
            scopes: ['openid', 'profile', 'email'],
        },
        AUTH_CONFIG.discovery
    );

    useEffect(() => {
        if (response?.type === 'success') {
            const { code } = response.params;
            handleExchangeCode(code);
        }
    }, [response]);

    const loginNativo = async (username: string, pass: string): Promise<{success: boolean, error?: string}> => {
        setIsLoading(true);
        try {
            const details: any = {
                'client_id': KEYCLOAK_CONFIG.clientId,
                'grant_type': 'password',
                'username': username,
                'password': pass,
                'scope': 'openid profile email'
            };

            const formBody = Object.keys(details)
                .map(key => encodeURIComponent(key) + '=' + encodeURIComponent(details[key]))
                .join('&');

            const res = await fetch(AUTH_CONFIG.discovery.tokenEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
                },
                body: formBody
            });

            const data = await res.json();

            if (res.ok && data.access_token) {
                await SecureStore.setItemAsync('userToken', data.access_token);
                setToken(data.access_token);
                setRefreshToken(data.refresh_token);
                
                const userResponse = await fetch(AUTH_CONFIG.discovery.userInfoEndpoint, {
                    headers: { Authorization: `Bearer ${data.access_token}` }
                });
                const userData = await userResponse.json();
                await SecureStore.setItemAsync('userData', JSON.stringify(userData));
                setUser(userData);
                return { success: true };
            } else {
                const errorMsg = data.error_description || data.error || "Error desconocido";
                return { success: false, error: errorMsg };
            }
        } catch (e: any) {
            return { success: false, error: "Error de red o servidor no disponible" };
        } finally {
            setIsLoading(false);
        }
    };

    const handleExchangeCode = async (code: string) => {
        try {
            const tokenResponse = await AuthSession.exchangeCodeAsync(
                {
                    code,
                    clientId: AUTH_CONFIG.clientId,
                    redirectUri: AuthSession.makeRedirectUri(),
                    extraParams: {
                        code_verifier: request?.codeVerifier || '',
                    },
                },
                AUTH_CONFIG.discovery
            );

            if (tokenResponse.accessToken) {
                await SecureStore.setItemAsync('userToken', tokenResponse.accessToken);
                setToken(tokenResponse.accessToken);
                if (tokenResponse.refreshToken) {
                    setRefreshToken(tokenResponse.refreshToken);
                }
                const userResponse = await fetch(AUTH_CONFIG.discovery.userInfoEndpoint, {
                    headers: { Authorization: `Bearer ${tokenResponse.accessToken}` }
                });
                const userData = await userResponse.json();
                await SecureStore.setItemAsync('userData', JSON.stringify(userData));
                setUser(userData);
            }
        } catch (e) {
            console.error("Error intercambiando código", e);
        }
    };

    const login = async () => {
        await promptAsync();
    };

    const logout = async () => {
        await SecureStore.deleteItemAsync('userToken');
        await SecureStore.deleteItemAsync('userData');
        setToken(null);
        setRefreshToken(null);
        setUser(null);
    };

    const register = async (email: string, pass: string, nombre: string): Promise<{success: boolean, error?: string}> => {
        setIsLoading(true);
        try {
            const api_url = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';
            const res = await fetch(`${api_url}/usuarios/registro`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password: pass, nombre })
            });

            const data = await res.json();
            if (res.ok) {
                return { success: true };
            } else {
                return { success: false, error: data.detail || "Error en el registro" };
            }
        } catch (e) {
            return { success: false, error: "Error de red" };
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <AuthContext.Provider value={{ user, token, login, loginNativo, register, logout, isLoading }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) throw new Error('useAuth debe usarse dentro de AuthProvider');
    return context;
};
