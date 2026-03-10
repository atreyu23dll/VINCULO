import { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, ActivityIndicator, Platform, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { startRadarService, stopRadarService } from '../../services/locationService';
import * as TaskManager from 'expo-task-manager';

export default function HomeScreen() {
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [lastCheck, setLastCheck] = useState<string | null>(null);
  const [radarActive, setRadarActive] = useState(false);

  useEffect(() => {
    // Check initial radar status
    const checkRadarStatus = async () => {
      const isRegistered = await TaskManager.isTaskRegisteredAsync('background-radar-task');
      setRadarActive(isRegistered);
    };
    checkRadarStatus();
  }, []);

  const toggleRadar = async () => {
    if (radarActive) {
      await stopRadarService();
      setRadarActive(false);
    } else {
      const started = await startRadarService();
      if (started) {
        setRadarActive(true);
        Alert.alert("Radar Activado", "La aplicación verificará coincidencias de tus deseos en segundo plano cada 5 minutos.");
      }
    }
  };

  const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

  const checkServerValues = async () => {
    setLoading(true);
    setStatus(null);

    try {
      console.log(`Conectando a: ${API_URL}`);
      const response = await fetch(API_URL);
      const data = await response.json();

      if (response.ok) {
        setStatus(JSON.stringify(data, null, 2));
      } else {
        setStatus(`Error: ${response.status}`);
      }
    } catch (error: any) {
      console.error(error);
      setStatus(`Error de conexión: ${error.message}`);
    } finally {
      setLoading(false);
      setLastCheck(new Date().toLocaleTimeString());
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-slate-900 items-center justify-center p-6">
      <View className="w-full max-w-md bg-slate-800 rounded-2xl p-6 border border-slate-700 shadow-lg">
        <Text className="text-3xl font-bold text-white mb-2 text-center">
          Vinculo App
        </Text>
        <Text className="text-slate-400 text-center mb-8">
          Estado del Servidor
        </Text>

        <View className="mb-8 p-4 bg-slate-950 rounded-lg min-h-[120px] justify-center items-center border border-slate-800">
          {loading ? (
            <ActivityIndicator size="large" color="#3b82f6" />
          ) : (
            <Text className={`text-center ${status?.includes('Error') ? 'text-red-400' : 'text-green-400'} font-medium`}>
              {status || "Pulsa el botón para comprobar conexión"}
            </Text>
          )}
        </View>

        <TouchableOpacity
          onPress={checkServerValues}
          disabled={loading}
          className={`active:bg-blue-600 py-4 px-6 rounded-xl flex-row justify-center items-center ${loading ? 'bg-slate-600' : 'bg-blue-500'}`}
        >
          <Text className="text-white font-bold text-lg">
            {loading ? 'Conectando...' : 'Verificar Estado'}
          </Text>
        </TouchableOpacity>

        {lastCheck && (
          <Text className="text-slate-500 text-xs text-center mt-4">
            Última comprobación: {lastCheck}
          </Text>
        )}

        {/* RADAR DE DESEOS BUTTON */}
        <TouchableOpacity
          onPress={toggleRadar}
          className={`mt-6 py-4 px-6 rounded-xl flex-row justify-center items-center ${radarActive ? 'bg-red-500/80' : 'bg-green-600'}`}
        >
          <Text className="text-white font-bold text-lg">
            {radarActive ? '⏹️ Detener Radar' : '📡 Activar Radar de Deseos'}
          </Text>
        </TouchableOpacity>

        <Text className="text-slate-600 text-xs text-center mt-6">
          Backend: {API_URL}
        </Text>
      </View>
    </SafeAreaView>
  );
}
