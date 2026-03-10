import * as Location from 'expo-location';
import * as TaskManager from 'expo-task-manager';
import { Alert } from 'react-native';

const LOCATION_TASK_NAME = 'background-radar-task';
const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://192.168.100.31:8000';
// TODO: Sustituir con User ID real
const USUARIO_TEST_ID = "00000000-0000-0000-0000-000000000000";

// 1. Definir la tarea en segundo plano
TaskManager.defineTask(LOCATION_TASK_NAME, async ({ data, error }) => {
  if (error) {
    console.error("Error en TaskManager de ubicación:", error);
    return;
  }
  if (data) {
    const { locations } = data as { locations: Location.LocationObject[] };
    const loc = locations[0];

    if (loc) {
      console.log(`📡 Enviando ubicación al radar: Lat: ${loc.coords.latitude}, Lon: ${loc.coords.longitude}`);
      try {
        const response = await fetch(`${API_URL}/api/radar/check`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            usuario_id: USUARIO_TEST_ID,
            latitude: loc.coords.latitude,
            longitude: loc.coords.longitude,
            radius_meters: 500
          })
        });

        if (response.ok) {
          const result = await response.json();
          if (result.matches && result.matches.length > 0) {
              // Notificar al usuario!
              const match = result.matches[0];
              // Nota: Alert no se muestra si la app está cerrada en iOS/Android nativo,
              // para notificaciones reales en background se usa expo-notifications.
              // Usamos Alert temporalmente asumiendo uso en primer plano o test.
              Alert.alert(
                  "¡Lugar Encontrado!",
                  `Tu deseo "${match.deseo_texto}" se puede cumplir en ${match.lugar_nombre}`,
                  [{ text: "Entendido" }]
              );
          }
        }
      } catch (err) {
          console.error("Error contactando al API del Radar:", err);
      }
    }
  }
});

// 2. Funciones para controlar el servicio
export const startRadarService = async () => {
    // Pedir permisos de foreground
    const { status: foregroundStatus } = await Location.requestForegroundPermissionsAsync();
    if (foregroundStatus !== 'granted') {
      Alert.alert('Permisos insuficientes', 'Se necesita acceso a la ubicación.');
      return false;
    }
  
    // Pedir permisos de background
    const { status: backgroundStatus } = await Location.requestBackgroundPermissionsAsync();
    if (backgroundStatus !== 'granted') {
      Alert.alert(
          'Radar Limitado', 
          'El radar solo funcionará mientras uses la app. Para monitoreo continuo "Siempre", cambia los permisos en ajustes.'
      );
      // Aun sin background, podemos al menos usar foreground de momento
    }
  
    const isRegistered = await TaskManager.isTaskRegisteredAsync(LOCATION_TASK_NAME);
    if (!isRegistered) {
        await Location.startLocationUpdatesAsync(LOCATION_TASK_NAME, {
            accuracy: Location.Accuracy.Balanced,
            timeInterval: 5 * 60 * 1000, // Cada 5 minutos
            distanceInterval: 100, // O cada 100 metros
            deferredUpdatesInterval: 5 * 60 * 1000, 
            showsBackgroundLocationIndicator: true, // Icono azul en iOS
        });
        console.log("✅ Servicio de Radar iniciado (Cada 5 mins).");
    }
    return true;
};

export const stopRadarService = async () => {
    const isRegistered = await TaskManager.isTaskRegisteredAsync(LOCATION_TASK_NAME);
    if (isRegistered) {
        await Location.stopLocationUpdatesAsync(LOCATION_TASK_NAME);
        console.log("⏹️ Servicio de Radar detenido.");
    }
};
