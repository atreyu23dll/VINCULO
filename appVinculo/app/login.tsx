import React, { useState } from 'react';
import { View, Text, TouchableOpacity, TextInput, StyleSheet, ActivityIndicator, Alert } from 'react-native';
import { useAuth } from '../context/AuthContext';
import { Stack, useRouter } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';

export default function LoginScreen() {
    const { login, loginNativo, token, isLoading } = useAuth();
    const router = useRouter();

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    React.useEffect(() => {
        if (token) {
            router.replace('/(tabs)');
        }
    }, [token]);

    const handleNativeLogin = async () => {
        if (!username || !password) {
            Alert.alert("Campos requeridos", "Por favor ingresa usuario y contraseña");
            return;
        }

        const result = await loginNativo(username, password);
        if (!result.success) {
            Alert.alert("Error de acceso", result.error || "Credenciales inválidas");
        }
    };

    return (
        <View style={styles.container}>
            <Stack.Screen options={{ headerShown: false }} />

            <LinearGradient
                colors={['#0f172a', '#1e293b', '#0f172a']}
                style={styles.background}
            />

            <View style={styles.content}>
                <View style={styles.logoContainer}>
                    <Text style={styles.title}>VÍNCULO</Text>
                    <Text style={styles.subtitle}>CONECTANDO DESEOS</Text>
                </View>

                <View style={styles.formCard}>
                    <Text style={styles.formTitle}>Bienvenido</Text>
                    
                    <View style={styles.inputContainer}>
                        <Text style={styles.label}>USUARIO</Text>
                        <TextInput
                            style={styles.input}
                            placeholder="username"
                            placeholderTextColor="#475569"
                            value={username}
                            onChangeText={setUsername}
                            autoCapitalize="none"
                        />
                    </View>

                    <View style={styles.inputContainer}>
                        <Text style={styles.label}>CONTRASEÑA</Text>
                        <TextInput
                            style={styles.input}
                            placeholder="••••••••"
                            placeholderTextColor="#475569"
                            value={password}
                            onChangeText={setPassword}
                            secureTextEntry
                        />
                    </View>

                    <TouchableOpacity
                        style={styles.mainButton}
                        onPress={handleNativeLogin}
                        disabled={isLoading}
                    >
                        {isLoading ? (
                            <ActivityIndicator color="#0f172a" />
                        ) : (
                            <Text style={styles.mainButtonText}>ACCEDER</Text>
                        )}
                    </TouchableOpacity>

                    <View style={styles.divider}>
                        <View style={styles.line} />
                        <Text style={styles.dividerText}>O TAMBIÉN</Text>
                        <View style={styles.line} />
                    </View>

                    <TouchableOpacity
                        style={styles.secondaryButton}
                        onPress={() => login()}
                    >
                        <Text style={styles.secondaryButtonText}>Login con Keycloak</Text>
                    </TouchableOpacity>
                </View>

                <Text style={styles.footer}>
                    {process.env.EXPO_PUBLIC_API_URL || 'Dev Mode'}
                </Text>
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    background: {
        position: 'absolute',
        left: 0,
        right: 0,
        top: 0,
        height: '100%',
    },
    content: {
        flex: 1,
        justifyContent: 'center',
        paddingHorizontal: 30,
    },
    logoContainer: {
        alignItems: 'center',
        marginBottom: 50,
    },
    title: {
        fontSize: 42,
        fontWeight: 'bold',
        color: 'white',
        letterSpacing: 8,
        fontStyle: 'italic'
    },
    subtitle: {
        fontSize: 12,
        color: '#facc15',
        marginTop: 5,
        letterSpacing: 4,
        fontWeight: 'bold'
    },
    formCard: {
        backgroundColor: '#1e293b',
        padding: 30,
        borderRadius: 30,
        borderWidth: 1,
        borderColor: '#334155',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 10 },
        shadowOpacity: 0.3,
        shadowRadius: 20,
    },
    formTitle: {
        fontSize: 24,
        color: 'white',
        fontWeight: 'bold',
        marginBottom: 30,
        textAlign: 'center'
    },
    inputContainer: {
        marginBottom: 20,
    },
    label: {
        color: '#94a3b8',
        fontSize: 10,
        fontWeight: 'bold',
        letterSpacing: 2,
        marginBottom: 8,
        marginLeft: 5
    },
    input: {
        backgroundColor: '#0f172a',
        color: 'white',
        paddingHorizontal: 20,
        paddingVertical: 15,
        borderRadius: 15,
        fontSize: 16,
        borderWidth: 1,
        borderColor: '#334155'
    },
    mainButton: {
        backgroundColor: '#facc15',
        paddingVertical: 18,
        borderRadius: 15,
        marginTop: 10,
        alignItems: 'center',
        shadowColor: '#facc15',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 10,
    },
    mainButtonText: {
        color: '#0f172a',
        fontSize: 16,
        fontWeight: 'bold',
        letterSpacing: 1
    },
    divider: {
        flexDirection: 'row',
        alignItems: 'center',
        marginVertical: 25,
    },
    line: {
        flex: 1,
        height: 1,
        backgroundColor: '#334155',
    },
    dividerText: {
        color: '#475569',
        marginHorizontal: 15,
        fontSize: 10,
        fontWeight: 'bold'
    },
    secondaryButton: {
        paddingVertical: 10,
        alignItems: 'center',
    },
    secondaryButtonText: {
        color: '#94a3b8',
        fontSize: 14,
        textDecorationLine: 'underline'
    },
    footer: {
        textAlign: 'center',
        marginTop: 30,
        color: '#334155',
        fontSize: 10,
        fontFamily: 'monospace'
    }
});
