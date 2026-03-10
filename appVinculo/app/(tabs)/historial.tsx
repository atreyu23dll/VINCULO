import React, { useState, useCallback } from 'react';
import { View, Text, FlatList, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useFocusEffect } from 'expo-router';

export default function HistorialScreen() {
  const [deseos, setDeseos] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // TODO: Reemplazar con el usuario dinamico (Context/Storage)
  const USUARIO_ID_TEST = "00000000-0000-0000-0000-000000000000"; 
  const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

  const fetchHistorial = async () => {
    setLoading(true);
    try {
      const resp = await fetch(`${API_URL}/deseos/usuario/${USUARIO_ID_TEST}/historial`);
      if (resp.ok) {
        const data = await resp.json();
        setDeseos(data);
      }
    } catch (e) {
      console.error("Error obteniendo historial: ", e);
    } finally {
      setLoading(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      fetchHistorial();
    }, [])
  );

  const renderItem = ({ item }: { item: any }) => (
    <View className="bg-slate-800 p-5 rounded-2xl mb-4 border border-slate-700 shadow-sm">
      <Text className="text-white text-lg font-semibold mb-3">{item.texto_original}</Text>
      <View className="flex-row justify-between items-center">
        <View className="bg-green-500/20 px-3 py-1.5 rounded-full border border-green-500/30">
            <Text className="text-green-400 font-bold text-xs uppercase tracking-wider">Cumplido</Text>
        </View>
        <Text className="text-slate-400 text-sm font-medium">
          {new Date(item.fecha_completado).toLocaleDateString()}
        </Text>
      </View>
    </View>
  );

  return (
    <SafeAreaView className="flex-1 bg-slate-900 p-6">
      <View className="mb-6">
          <Text className="text-4xl font-bold text-white mb-2">Historial</Text>
          <Text className="text-slate-400 text-base">Tus deseos completados</Text>
      </View>
      
      {loading ? (
        <View className="flex-1 justify-center items-center">
            <ActivityIndicator size="large" color="#3b82f6" />
        </View>
      ) : deseos.length === 0 ? (
        <View className="flex-1 justify-center items-center bg-slate-800/50 rounded-2xl border border-slate-800 p-8">
          <Text className="text-slate-400 text-center text-lg">Aún no tienes deseos completados. ¡Cumple uno pronto!</Text>
        </View>
      ) : (
        <FlatList
          data={deseos}
          keyExtractor={(item) => item.id}
          renderItem={renderItem}
          showsVerticalScrollIndicator={false}
          contentContainerStyle={{ paddingBottom: 20 }}
        />
      )}
    </SafeAreaView>
  );
}
