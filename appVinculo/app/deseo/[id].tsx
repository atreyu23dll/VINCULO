import { useLocalSearchParams, useRouter } from 'expo-router';
import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, ActivityIndicator, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import SuccessAnimation from '../../components/SuccessAnimation';

export default function DeseoDetailScreen() {
  const { id } = useLocalSearchParams();
  const router = useRouter();
  const [deseo, setDeseo] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [completing, setCompleting] = useState(false);
  const [showAnimation, setShowAnimation] = useState(false);

  const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

  useEffect(() => {
    if (id) {
        fetchDeseo();
    }
  }, [id]);

  const fetchDeseo = async () => {
    try {
      const resp = await fetch(`${API_URL}/deseos/${id}`);
      if (resp.ok) {
        const data = await resp.json();
        setDeseo(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleCompletar = async () => {
    setCompleting(true);
    try {
      // Opcionalmente se puede enviar lat/lng si se tiene la ubicación del dispositivo
      const resp = await fetch(`${API_URL}/deseos/${id}/complete`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lat: null, lng: null })
      });
      
      if (resp.ok) {
        setShowAnimation(true);
      } else {
        const errorData = await resp.json();
        Alert.alert("Error", `No se pudo completar el deseo: ${JSON.stringify(errorData)}`);
      }
    } catch (error) {
      console.error(error);
      Alert.alert("Error", "Hubo un problema de conexión con el servidor");
    } finally {
      setCompleting(false);
    }
  };

  if (loading) return <View className="flex-1 justify-center items-center bg-slate-900"><ActivityIndicator size="large" color="#3b82f6" /></View>;
  if (!deseo) return <View className="flex-1 justify-center items-center bg-slate-900"><Text className="text-white">Deseo no encontrado</Text></View>;

  return (
    <SafeAreaView className="flex-1 bg-slate-900 p-6 relative">
      <View className="flex-1">
        <TouchableOpacity onPress={() => router.back()} className="mb-6">
          <Text className="text-blue-400 font-bold text-base">{'< Volver'}</Text>
        </TouchableOpacity>
        
        <View className="bg-slate-800 p-6 rounded-2xl border border-slate-700">
          <Text className="text-slate-400 text-sm mb-2 font-medium uppercase tracking-wider">Detalle del Deseo</Text>
          <Text className="text-white text-2xl font-semibold mb-4 leading-tight">{deseo.texto_original}</Text>
          
          <Text className="text-slate-400 font-medium mb-8">
            Estado: <Text className="text-blue-400 font-bold uppercase ml-1">{deseo.estado}</Text>
          </Text>

          {deseo.estado !== 'COMPLETADO' && (
            <TouchableOpacity 
              onPress={handleCompletar}
              disabled={completing}
              className={`py-4 px-6 rounded-xl flex-row justify-center items-center shadow-lg ${completing ? 'bg-slate-600' : 'bg-green-500 active:bg-green-600'}`}
            >
              <Text className="text-white font-bold text-lg tracking-wide">
                {completing ? 'Completando...' : '¡Deseo Completado!'}
              </Text>
            </TouchableOpacity>
          )}
        </View>
      </View>

      <SuccessAnimation 
        visible={showAnimation} 
        onAnimationFinish={() => {
            setShowAnimation(false);
            // Navegar al historial despues de la animación
            router.replace('/(tabs)/historial');
        }} 
      />
    </SafeAreaView>
  );
}
