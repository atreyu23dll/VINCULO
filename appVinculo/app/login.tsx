import { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, Alert, ActivityIndicator } from "react-native";
import { useRouter } from "expo-router";

const API_URL = process.env.EXPO_PUBLIC_API_URL;

export default function LoginScreen() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [cargando, setCargando] = useState(false);

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert("Error", "Por favor llena todos los campos");
      return;
    }
    setCargando(true);
    try {
      const res = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);
      router.replace("/(tabs)");
    } catch (err: any) {
      Alert.alert("Error", err.message || "No se pudo iniciar sesión");
    } finally {
      setCargando(false);
    }
  };

  return (
    <View style={{ flex: 1, backgroundColor: "#fff", justifyContent: "center", paddingHorizontal: 32 }}>
      <Text style={{ fontSize: 32, fontWeight: "bold", textAlign: "center", marginBottom: 8, color: "#4F46E5" }}>
        Vínculo
      </Text>
      <Text style={{ textAlign: "center", color: "#6B7280", marginBottom: 32 }}>
        Inicia sesión para continuar
      </Text>

      <TextInput
        style={{ borderWidth: 1, borderColor: "#D1D5DB", borderRadius: 12, paddingHorizontal: 16, paddingVertical: 12, marginBottom: 16, fontSize: 16 }}
        placeholder="Correo electrónico"
        keyboardType="email-address"
        autoCapitalize="none"
        value={email}
        onChangeText={setEmail}
      />
      <TextInput
        style={{ borderWidth: 1, borderColor: "#D1D5DB", borderRadius: 12, paddingHorizontal: 16, paddingVertical: 12, marginBottom: 24, fontSize: 16 }}
        placeholder="Contraseña"
        secureTextEntry
        value={password}
        onChangeText={setPassword}
      />

      <TouchableOpacity
        style={{ backgroundColor: "#4F46E5", borderRadius: 12, paddingVertical: 16, alignItems: "center" }}
        onPress={handleLogin}
        disabled={cargando}
      >
        {cargando
          ? <ActivityIndicator color="#fff" />
          : <Text style={{ color: "#fff", fontWeight: "600", fontSize: 16 }}>Iniciar sesión</Text>
        }
      </TouchableOpacity>
    </View>
  );
}
