import React, { useState } from 'react';
import { View, Text, TouchableOpacity, TextInput, StyleSheet, ActivityIndicator, Alert, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import { useAuth } from '../context/AuthContext';
import { Stack, useRouter, Link } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';

export default function RegisterScreen() {
    const { register, isLoading } = useAuth();
    const router = useRouter();

    const [nombre, setNombre] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');

    const handleRegister = async () => {
        if (!email || !password || !nombre) {
            Alert.alert("Campos requeridos", "Por favor completa todos los campos");
            return;
        }

        if (password !== confirmPassword) {
            Alert.alert("Error", "Las contraseñas no coinciden");
            return;
        }

        const result = await register(email, password, nombre);
        if (result.success) {
            Alert.alert(
                "¡Éxito!", 
                "Usuario registrado correctamente. Ahora puedes iniciar sesión.",
                [{ text: "OK", onPress: () => router.push('/login') }]
            );
        } else {
            Alert.alert("Error de registro", result.error || "No se pudo crear la cuenta");
        }
    };

    return (
        <KeyboardAvoidingView 
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
            style={styles.container}
        >
            <Stack.Screen options={{ headerShown: false }} />

            <LinearGradient
                colors={['#0f172a', '#1e293b', '#0f172a']}
                style={styles.background}
            />

            <ScrollView contentContainerStyle={styles.scrollContent}>
                <View style={styles.logoContainer}>
                    <Text style={styles.title}>VÍNCULO</Text>
                    <Text style={styles.subtitle}>CREAR CUENTA</Text>
                </View>

                <View style={styles.formCard}>
                    <Text style={styles.formTitle}>Registro</Text>
                    
                    <View style={styles.inputContainer}>
                        <Text style={styles.label}>NOMBRE COMPLETO</Text>
                        <TextInput
                            style={styles.input}
                            placeholder="Juan Pérez"
                            placeholderTextColor="#475569"
                            value={nombre}
                            onChangeText={setNombre}
                        />
                    </View>

                    <View style={styles.inputContainer}>
                        <Text style={styles.label}>EMAIL</Text>
                        <TextInput
                            style={styles.input}
                            placeholder="email@ejemplo.com"
                            placeholderTextColor="#475569"
                            value={email}
                            onChangeText={setEmail}
                            autoCapitalize="none"
                            keyboardType="email-address"
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

                    <View style={styles.inputContainer}>
                        <Text style={styles.label}>CONFIRMAR CONTRASEÑA</Text>
                        <TextInput
                            style={styles.input}
                            placeholder="••••••••"
                            placeholderTextColor="#475569"
                            value={confirmPassword}
                            onChangeText={setConfirmPassword}
                            secureTextEntry
                        />
                    </View>

                    <TouchableOpacity
                        style={styles.mainButton}
                        onPress={handleRegister}
                        disabled={isLoading}
                    >
                        {isLoading ? (
                            <ActivityIndicator color="#0f172a" />
                        ) : (
                            <Text style={styles.mainButtonText}>REGISTRARSE</Text>
                        )}
                    </TouchableOpacity>

                    <View style={styles.footerContainer}>
                        <Text style={styles.footerText}>¿Ya tienes cuenta?</Text>
                        <Link href="/login" asChild>
                            <TouchableOpacity>
                                <Text style={styles.linkText}> Inicia sesión</Text>
                            </TouchableOpacity>
                        </Link>
                    </View>
                </View>
            </ScrollView>
        </KeyboardAvoidingView>
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
    scrollContent: {
        flexGrow: 1,
        justifyContent: 'center',
        paddingHorizontal: 30,
        paddingVertical: 50,
    },
    logoContainer: {
        alignItems: 'center',
        marginBottom: 40,
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
    footerContainer: {
        flexDirection: 'row',
        justifyContent: 'center',
        marginTop: 25,
    },
    footerText: {
        color: '#94a3b8',
        fontSize: 14,
    },
    linkText: {
        color: '#facc15',
        fontSize: 14,
        fontWeight: 'bold',
    }
});
