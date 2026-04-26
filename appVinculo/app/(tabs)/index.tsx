import React, { useState, useEffect, useRef } from 'react';
import { View, Text, FlatList, TouchableOpacity, TextInput, ActivityIndicator, Alert, Modal, Dimensions, StyleSheet, Platform, KeyboardAvoidingView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAuth } from '../../context/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import * as Location from 'expo-location';
import * as TaskManager from 'expo-task-manager';
import {
  GestureHandlerRootView,
  GestureDetector,
  Gesture,
  ScrollView
} from 'react-native-gesture-handler';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  runOnJS,
  interpolate,
  Extrapolate
} from 'react-native-reanimated';

const { width } = Dimensions.get('window');
const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';
const PRIORIDADES = ['alta', 'media', 'baja'] as const;

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
    shouldShowBanner: true,
    shouldShowList: true,
  }),
});

const getPriorityColor = (p: string) => {
  switch (p) {
    case 'alta': return '#ef4444';
    case 'media': return '#facc15';
    case 'baja': return '#22c55e';
    default: return '#94a3b8';
  }
};

const GEOFENCE_TASK_NAME = 'GEOFENCE_VINCULO';

TaskManager.defineTask(GEOFENCE_TASK_NAME, async ({ data: { eventType, region }, error }: any) => {
  if (error) {
    console.error("Error en Geofence:", error.message);
    return;
  }
  if (eventType === Location.GeofencingEventType.Enter) {
    console.log("📍 ¡ENTRASTE A UNA ZONA VÍNCULO!", region);
    
    await Notifications.scheduleNotificationAsync({
      content: {
        title: "✨ ¡VÍNCULO CERCANO!",
        body: `Detectado movimiento cerca de un punto de interés.`,
        sound: true,
        priority: Notifications.AndroidNotificationPriority.MAX,
        color: '#facc15',
        data: { region }
      },
      trigger: null,
    });
  }
});

interface Ubicacion {
  id: string;
  nombre_lugar: string;
  lat: number;
  lon: number;
}

interface Deseo {
  id: string;
  texto_original: string;
  tag_osm: string | null;
  estado: string;
  prioridad: string;
  es_favorito: boolean;
  created_at: string;
  ubicaciones?: Ubicacion[];
}

interface Notificacion {
  id: string;
  mensaje: string;
}

const decodeToken = (token: string | null) => {
  if (!token) return null;
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=';
    let str = base64.replace(/=+$/, '');
    let output = '';
    for (let bc = 0, bs = 0, buffer, i = 0; (buffer = str.charAt(i++)); ~buffer && (bs = bc % 4 ? bs * 64 + buffer : buffer, bc++ % 4) ? (output += String.fromCharCode(255 & (bs >> (-2 * bc & 6)))) : 0) {
      buffer = chars.indexOf(buffer);
    }
    return JSON.parse(output);
  } catch (e) {
    return null;
  }
};

const DraggableCard = ({ item, onMove, onDelete, onEdit, onFavorite }: {
  item: Deseo,
  onMove: (item: Deseo, direction: 'left' | 'right') => void,
  onDelete: (id: string) => void,
  onEdit: (item: Deseo) => void,
  onFavorite: (item: Deseo) => void
}) => {
  const translateX = useSharedValue(0);
  const scale = useSharedValue(1);

  const panGesture = Gesture.Pan()
    .onUpdate((event) => {
      translateX.value = event.translationX;
      scale.value = withSpring(1.02);
    })
    .onEnd(() => {
      scale.value = withSpring(1);
      if (translateX.value > width * 0.3) {
        runOnJS(onMove)(item, 'right');
      } else if (translateX.value < -width * 0.3) {
        runOnJS(onMove)(item, 'left');
      }
      translateX.value = withSpring(0);
    });

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: translateX.value }, { scale: scale.value }],
    opacity: interpolate(translateX.value, [-width * 0.5, 0, width * 0.5], [0.8, 1, 0.8], Extrapolate.CLAMP)
  }));



  const getProgress = (estado: string) => {
    switch (estado) {
      case 'nuevo': return 0.2;
      case 'analizando': return 0.5;
      case 'buscando': return 0.8;
      case 'completado': return 1;
      case 'error': return 1;
      default: return 0.1;
    }
  };

  return (
    <GestureDetector gesture={panGesture}>
      <Animated.View style={[styles.cardContainer, animatedStyle]}>
        <View style={styles.cardHeader}>
          <View style={styles.headerLeft}>
            <TouchableOpacity onPress={() => onFavorite(item)} style={styles.actionBtn}>
              <Ionicons name={item.es_favorito ? "star" : "star-outline"} size={20} color={item.es_favorito ? "#facc15" : "#475569"} />
            </TouchableOpacity>
            {item.tag_osm && (
              <View style={styles.tagBadge}>
                <Text style={styles.tagText}>{item.tag_osm}</Text>
              </View>
            )}
          </View>
          <TouchableOpacity onPress={() => onDelete(item.id)} style={styles.actionBtn}>
            <Ionicons name="trash-outline" size={18} color="#ef4444" />
          </TouchableOpacity>
        </View>

        <TouchableOpacity onPress={() => onEdit(item)} activeOpacity={0.7} style={styles.cardContent}>
          <Text style={styles.cardText}>{item.texto_original}</Text>
          
          {item.estado !== 'completado' && (
            <View style={styles.progressContainer}>
              <View style={[styles.progressBar, { 
                width: `${getProgress(item.estado) * 100}%`,
                backgroundColor: item.estado === 'error' ? '#ef4444' : '#facc15'
              }]} />
              <Text style={styles.progressText}>{item.estado.toUpperCase()}...</Text>
            </View>
          )}

          {item.ubicaciones && item.ubicaciones.length > 0 && (
            <View style={styles.locationsBox}>
              <Text style={styles.locationsTitle}>LOCALES EN CD. JUÁREZ ({item.ubicaciones.length})</Text>
              {item.ubicaciones.slice(0, 4).map((u, idx) => (
                <View key={u.id || idx} style={styles.locationRow}>
                  <Text style={styles.locationName} numberOfLines={1}>• {u.nombre_lugar}</Text>
                  <Text style={styles.locationCoords}>{u.lat?.toFixed(3)},{u.lon?.toFixed(3)}</Text>
                </View>
              ))}
            </View>
          )}

          <View style={styles.cardFooter}>
            <View style={[styles.priorityDot, { backgroundColor: getPriorityColor(item.prioridad) }]} />
            <Text style={styles.dateText}>{new Date(item.created_at).toLocaleDateString()}</Text>
          </View>
        </TouchableOpacity>
      </Animated.View>
    </GestureDetector>
  );
};

export default function KanbanDeseosScreen() {
  const { token, logout } = useAuth();
  const [deseos, setDeseos] = useState<Deseo[]>([]);
  const [loading, setLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [userName, setUserName] = useState('Usuario');
  const [editingDeseo, setEditingDeseo] = useState<Deseo | null>(null);
  const [textoDeseo, setTextoDeseo] = useState('');
  const [prioridadSeleccionada, setPrioridadSeleccionada] = useState<'alta' | 'media' | 'baja'>('media');
  const [currentCol, setCurrentCol] = useState(1);
  const scrollViewRef = useRef<Animated.ScrollView>(null);

  const [location, setLocation] = useState<Location.LocationObject | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [lastUpdateCoords, setLastUpdateCoords] = useState<{lat: number, lon: number} | null>(null);

  useEffect(() => {
    (async () => {
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        setErrorMsg('Permiso de ubicación denegado');
        return;
      }

      // IMPORTANTE: Pedir permiso de segundo plano para Geofencing
      const { status: bgStatus } = await Location.requestBackgroundPermissionsAsync();
      if (bgStatus !== 'granted') {
        console.warn('Permiso de ubicación en segundo plano denegado. El Geofencing no funcionará con la app cerrada.');
      }

      // Configurar Canal de Notificaciones (Android)
      if (Platform.OS === 'android') {
        await Notifications.setNotificationChannelAsync('vinculo-alerts', {
          name: 'Alertas de Vínculo',
          importance: Notifications.AndroidImportance.MAX,
          vibrationPattern: [0, 250, 250, 250],
          lightColor: '#FF231F7C',
        });
      }

      // Obtener ubicación inicial
      let loc = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced });
      setLocation(loc);
      setLastUpdateCoords({ lat: loc.coords.latitude, lon: loc.coords.longitude });

      // Monitorear cambios (cada 100 metros)
      await Location.watchPositionAsync(
        {
          accuracy: Location.Accuracy.Balanced,
          distanceInterval: 100, // 100 metros para ahorrar batería
        },
        (newLoc) => {
          setLocation(newLoc);
          // 1. Guardar en la tabla de usuario para notificaciones de proximidad
          saveUserLocation(newLoc.coords.latitude, newLoc.coords.longitude);
          // 2. Refrescar deseos para buscar cosas nuevas en esa zona
          fetchDeseos(newLoc.coords.latitude, newLoc.coords.longitude);
        }
      );
    })();

    fetchDeseos();
    const info = decodeToken(token);
    if (info) setUserName(info.given_name || 'Usuario');
    
    // Registrar para Notificaciones Push (Bolsillo)
    registerForPushNotificationsAsync().then(pushToken => {
      if (pushToken) {
        console.log("📲 Push Token obtenido:", pushToken);
        savePushToken(pushToken);
      }
    });

    const interval = setInterval(() => {
        fetchDeseos();
    }, 10000); 
    return () => clearInterval(interval);
  }, [token]);

  const registerGeofences = async (deseosData: any[]) => {
    try {
      const regions: any[] = [];
      deseosData.forEach(deseo => {
        if (deseo.ubicaciones) {
          deseo.ubicaciones.forEach((ubi: any) => {
            // SOLO REGISTRAR SI NO HA SIDO NOTIFICADO
            if (!ubi.ya_notificado && ubi.lat && ubi.lon) {
              regions.push({
                identifier: ubi.id,
                latitude: ubi.lat,
                longitude: ubi.lon,
                radius: 150, // 150 metros
                notifyOnEnter: true,
                notifyOnExit: false, // Quité el Exit para evitar ruido
              });
            }
          });
        }
      });

      if (regions.length > 0) {
        console.log(`📡 Intentando registrar ${regions.length} geocercas...`);
        const limitedRegions = regions.slice(0, 20);
        await Location.startGeofencingAsync(GEOFENCE_TASK_NAME, limitedRegions);
        console.log(`🎯 Geofencing ACTIVO: ${limitedRegions.length} zonas vigiladas.`);
      }
    } catch (e) {
      console.error("Error registrando Geofences:", e);
    }
  };

  const saveUserLocation = async (lat: number, lon: number) => {
    try {
      await fetch(`${API_URL}/usuarios/me/ubicacion`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify({ latitud: lat, longitud: lon }),
      });
      console.log("📍 Ubicación sincronizada con el servidor");
    } catch (e) {
      console.error("Error sincronizando ubicación:", e);
    }
  };

  const registerForPushNotificationsAsync = async () => {
    let token;
    if (Device.isDevice) {
      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;
      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }
      if (finalStatus !== 'granted') {
        alert('¡Vínculo necesita permiso para avisarte en el bolsillo!');
        return;
      }
      token = (await Notifications.getExpoPushTokenAsync({
        projectId: '088d6c7b-8322-41e2-bf73-f0502b2bbb6f'
      })).data;
    } else {
      console.log('Debes usar un dispositivo físico para notificaciones push');
    }

    if (Platform.OS === 'android') {
      Notifications.setNotificationChannelAsync('default', {
        name: 'default',
        importance: Notifications.AndroidImportance.MAX,
        vibrationPattern: [0, 250, 250, 250],
        lightColor: '#FF231F7C',
      });
    }

    return token;
  };

  const savePushToken = async (pushToken: string) => {
    try {
      await fetch(`${API_URL}/usuarios/me/push-token`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify({ push_token: pushToken }),
      });
    } catch (e) {
      console.error("Error guardando push token:", e);
    }
  };

  // Nuevo efecto para Notificaciones de Proximidad
  useEffect(() => {
    const checkNotifications = async () => {
      if (!token) return;
      try {
        const response = await fetch(`${API_URL}/notificaciones/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (response.ok) {
          const notifs: Notificacion[] = await response.json();
          if (notifs.length > 0) {
            const latest = notifs[0];
            Alert.alert('¡VÍNCULO!', latest.mensaje, [
              { 
                text: 'OK', 
                onPress: async () => {
                  await fetch(`${API_URL}/notificaciones/${latest.id}/leer`, {
                    method: 'POST',
                    headers: { Authorization: `Bearer ${token}` },
                  });
                }
              }
            ]);
          }
        }
      } catch (error) {
        // No logeamos error para no saturar la consola en caso de micro-cortes
      }
    };

    // Ejecutar de inmediato al montar
    checkNotifications();

    const notifInterval = setInterval(checkNotifications, 5000); // Bajamos a 5 segundos
    return () => clearInterval(notifInterval);
  }, [token]);

  const fetchDeseos = async (lat?: number, lon?: number) => {
    try {
      // Si recibimos coordenadas nuevas, se las mandamos al backend para que el worker de IA
      // sepa dónde buscar. Si no, solo traemos los deseos existentes.
      const url = (lat && lon) 
        ? `${API_URL}/deseos/me?lat=${lat}&lon=${lon}` 
        : `${API_URL}/deseos/me`;

      const response = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await response.json();
      if (Array.isArray(data)) {
        setDeseos(data);
        // Actualizar las cercas geográficas (Geofencing)
        registerGeofences(data);
      }
    } catch (error) {
      console.error("Fetch error:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    console.log("📝 Intentando guardar deseo:", textoDeseo);
    if (!textoDeseo.trim()) {
      console.log("⚠️ Error: El texto está vacío");
      return;
    }
    if (isSaving) {
      console.log("⏳ Ya se está guardando otro deseo, ignorando...");
      return;
    }

    setIsSaving(true);
    const url = editingDeseo ? `${API_URL}/deseos/${editingDeseo.id}` : `${API_URL}/deseos/`;
    const method = editingDeseo ? 'PATCH' : 'POST';
    
    console.log(`🌐 Enviando petición ${method} a: ${url}`);

    try {
      const response = await fetch(url, {
        method,
        headers: { 
          'Content-Type': 'application/json', 
          'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify({ 
          texto_original: textoDeseo, 
          prioridad: prioridadSeleccionada,
          latitud_usuario: location?.coords.latitude || 31.6904,
          longitud_usuario: location?.coords.longitude || -106.4245,
          radio_busqueda_metros: 5000
        }),
      });

      console.log("✅ Respuesta recibida:", response.status);

      if (response.ok) {
        setModalVisible(false);
        setTextoDeseo(''); // Limpiar el input
        fetchDeseos();
      } else {
        const errorData = await response.json();
        console.log("❌ Error del servidor:", errorData);
        Alert.alert('Error', `Servidor respondió con ${response.status}`);
      }
    } catch (error) {
      console.log("🚨 Error de RED:", error);
      Alert.alert('Error de conexión', 'No se pudo conectar con el servidor. Verifica que tu IP sea correcta.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleMove = async (item: Deseo, direction: 'left' | 'right') => {
    const currentIndex = PRIORIDADES.indexOf(item.prioridad as any);
    let nextIndex = direction === 'right' ? currentIndex + 1 : currentIndex - 1;
    if (nextIndex >= 0 && nextIndex < PRIORIDADES.length) {
      const nuevaPrioridad = PRIORIDADES[nextIndex];
      setDeseos(prev => prev.map(d => d.id === item.id ? { ...d, prioridad: nuevaPrioridad } : d));
      try {
        await fetch(`${API_URL}/deseos/${item.id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
          body: JSON.stringify({ prioridad: nuevaPrioridad }),
        });
      } catch (error) {
        fetchDeseos();
      }
    }
  };

  const deleteDeseo = (id: string) => {
    Alert.alert('Eliminar', '¿Borrar registro?', [
      { text: 'Cancelar' },
      { text: 'Eliminar', style: 'destructive', onPress: async () => {
          await fetch(`${API_URL}/deseos/${id}`, {
            method: 'DELETE',
            headers: { Authorization: `Bearer ${token}` },
          });
          fetchDeseos();
        }
      }
    ]);
  };

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaView style={{ flex: 1, backgroundColor: '#020617' }}>
        <LinearGradient colors={['#1e293b', '#0f172a']} style={styles.header}>
          <View>
            <View style={{ flexDirection: 'row', alignItems: 'center' }}>
              <Text style={styles.headerTitle}>Vínculo</Text>
              <View style={[styles.gpsDot, { backgroundColor: location ? '#22c55e' : '#64748b' }]} />
            </View>
            <Text style={styles.headerSubtitle}>Hola, {userName}</Text>
          </View>
          <TouchableOpacity onPress={logout} style={styles.logoutBtn}>
            <Ionicons name="log-out-outline" size={24} color="#facc15" />
          </TouchableOpacity>
        </LinearGradient>

        {loading ? <ActivityIndicator size="large" color="#facc15" style={{marginTop: 50}} /> : (
          <Animated.ScrollView
            horizontal pagingEnabled ref={scrollViewRef} showsHorizontalScrollIndicator={false}
            onMomentumScrollEnd={(e) => setCurrentCol(Math.round(e.nativeEvent.contentOffset.x / width))}
            contentOffset={{ x: width, y: 0 }}
          >
            {PRIORIDADES.map((p) => (
              <View key={p} style={{ width, paddingHorizontal: 20 }}>
                <Text style={[styles.colTitle, { color: p==='alta'?'#f87171':p==='media'?'#facc15':'#4ade80' }]}>{p.toUpperCase()}</Text>
                <FlatList
                  data={(deseos || []).filter(d => d.prioridad === p)}
                  keyExtractor={(item) => item.id}
                  renderItem={({ item }) => (
                    <DraggableCard item={item} onMove={handleMove} onDelete={deleteDeseo} onEdit={(d) => { setEditingDeseo(d); setTextoDeseo(d.texto_original); setPrioridadSeleccionada(d.prioridad as any); setModalVisible(true); }} onFavorite={async (d) => {
                      setDeseos(prev => prev.map(x => x.id === d.id ? { ...x, es_favorito: !x.es_favorito } : x));
                      await fetch(`${API_URL}/deseos/${d.id}`, {
                        method: 'PATCH',
                        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
                        body: JSON.stringify({ es_favorito: !d.es_favorito }),
                      });
                    }} />
                  )}
                  ListEmptyComponent={<Text style={styles.emptyText}>Vacío</Text>}
                />
              </View>
            ))}
          </Animated.ScrollView>
        )}

        <TouchableOpacity style={styles.fab} onPress={() => { setEditingDeseo(null); setTextoDeseo(''); setPrioridadSeleccionada('media'); setModalVisible(true); }}>
          <Ionicons name="add" size={36} color="#0f172a" />
        </TouchableOpacity>

        <Modal visible={modalVisible} animationType="slide" transparent>
          <KeyboardAvoidingView 
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
            style={{ flex: 1 }}
          >
            <View style={styles.modalOverlay}>
              <View style={styles.modalContent}>
                <ScrollView bounces={false} showsVerticalScrollIndicator={false}>
                  <Text style={styles.modalTitle}>{editingDeseo ? 'EDITAR' : 'NUEVO'} DESEO</Text>
                  <TextInput 
                    style={styles.modalInput} 
                    value={textoDeseo} 
                    onChangeText={setTextoDeseo} 
                    multiline 
                    placeholder="¿Qué estás buscando? (ej. Unos tacos de pastor)" 
                    placeholderTextColor="#475569" 
                    autoFocus
                  />
                  
                  <View style={styles.prioritiesRow}>
                    {PRIORIDADES.map(p => (
                      <TouchableOpacity 
                        key={p} 
                        style={[styles.priorityBtn, prioridadSeleccionada === p && { borderColor: getPriorityColor(p), backgroundColor: 'rgba(255,255,255,0.05)' }]}
                        onPress={() => setPrioridadSeleccionada(p)}
                      >
                        <View style={[styles.priorityDot, { backgroundColor: getPriorityColor(p) }]} />
                        <Text style={[styles.priorityBtnText, prioridadSeleccionada === p && { color: 'white' }]}>{p.toUpperCase()}</Text>
                      </TouchableOpacity>
                    ))}
                  </View>

                  <TouchableOpacity style={styles.saveBtn} onPress={handleSave} disabled={isSaving}>
                    {isSaving ? <ActivityIndicator color="#0f172a" /> : <Text style={styles.saveBtnText}>GUARDAR EN MI VÍNCULO</Text>}
                  </TouchableOpacity>
                  <TouchableOpacity onPress={() => setModalVisible(false)} style={{marginTop: 15, paddingBottom: 20}}>
                    <Text style={{color:'#94a3b8', textAlign:'center'}}>Cancelar</Text>
                  </TouchableOpacity>
                </ScrollView>
              </View>
            </View>
          </KeyboardAvoidingView>
        </Modal>
      </SafeAreaView>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  header: { paddingHorizontal: 30, paddingVertical: 20, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  headerTitle: { fontSize: 28, fontWeight: 'bold', color: 'white', fontStyle: 'italic' },
  headerSubtitle: { fontSize: 10, color: '#facc15', letterSpacing: 2, fontWeight: 'bold', marginTop: 4 },
  logoutBtn: { padding: 10, borderRadius: 15, backgroundColor: '#1e293b' },
  colTitle: { fontSize: 12, fontWeight: 'bold', letterSpacing: 3, marginVertical: 20, textAlign: 'center' },
  cardContainer: { backgroundColor: '#1e293b', marginBottom: 15, borderRadius: 24, borderWidth: 1, borderColor: '#334155', elevation: 4 },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', padding: 15, paddingBottom: 5 },
  headerLeft: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  actionBtn: { padding: 5 },
  tagBadge: { backgroundColor: 'rgba(250, 204, 21, 0.1)', paddingHorizontal: 8, paddingVertical: 2, borderRadius: 8, borderWidth: 1, borderColor: 'rgba(250, 204, 21, 0.3)' },
  tagText: { color: '#facc15', fontSize: 9, fontWeight: 'bold', textTransform: 'uppercase' },
  cardContent: { padding: 20, paddingTop: 10 },
  cardText: { color: 'white', fontSize: 16, lineHeight: 24 },
  progressContainer: { marginTop: 15, backgroundColor: '#0f172a', height: 20, borderRadius: 10, overflow: 'hidden', justifyContent: 'center' },
  progressBar: { height: '100%', backgroundColor: '#facc15' },
  progressText: { position: 'absolute', width: '100%', textAlign: 'center', color: 'white', fontSize: 8, fontWeight: 'bold' },
  locationsBox: { marginTop: 15, padding: 12, backgroundColor: '#0f172a', borderRadius: 16 },
  locationsTitle: { color: '#64748b', fontSize: 9, fontWeight: 'bold', marginBottom: 8 },
  locationRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 4 },
  locationName: { color: '#cbd5e1', fontSize: 11, flex: 1 },
  locationCoords: { color: '#475569', fontSize: 9, fontFamily: 'monospace' },
  cardFooter: { flexDirection: 'row', alignItems: 'center', marginTop: 20, opacity: 0.5 },
  priorityDot: { width: 6, height: 6, borderRadius: 3, marginRight: 10 },
  dateText: { color: '#94a3b8', fontSize: 10 },
  emptyText: { color: '#334155', textAlign: 'center', marginTop: 40, fontStyle: 'italic' },
  gpsDot: { width: 8, height: 8, borderRadius: 4, marginLeft: 10, marginTop: 5, shadowColor: '#22c55e', shadowOffset: { width: 0, height: 0 }, shadowOpacity: 0.5, shadowRadius: 5 },
  fab: { position: 'absolute', bottom: 40, right: 30, backgroundColor: '#facc15', width: 64, height: 64, borderRadius: 32, justifyContent: 'center', alignItems: 'center', elevation: 8 },
  modalOverlay: { flex: 1, justifyContent: 'flex-end', backgroundColor: 'rgba(0,0,0,0.8)' },
  modalContent: { backgroundColor: '#1e293b', padding: 30, borderTopLeftRadius: 40, borderTopRightRadius: 40 },
  modalInput: { backgroundColor: '#0f172a', color: 'white', padding: 20, borderRadius: 20, fontSize: 18, marginBottom: 20, height: 120 },
  saveBtn: { backgroundColor: '#facc15', padding: 20, borderRadius: 20, alignItems: 'center' },
  saveBtnText: { color: '#0f172a', fontWeight: 'bold', fontSize: 16 },
  modalTitle: { color: 'white', fontSize: 12, fontWeight: 'bold', letterSpacing: 2, marginBottom: 20, textAlign: 'center' },
  prioritiesRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 20, gap: 10 },
  priorityBtn: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', padding: 10, borderRadius: 12, borderWidth: 1, borderColor: '#334155' },
  priorityBtnText: { color: '#64748b', fontSize: 10, fontWeight: 'bold', marginLeft: 5 }
});
