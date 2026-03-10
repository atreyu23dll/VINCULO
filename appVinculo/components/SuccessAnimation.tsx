import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function SuccessAnimation() {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>¡Deseo Completado!</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { padding: 20, backgroundColor: '#d4edda', borderRadius: 10, alignItems: 'center', marginVertical: 10 },
  text: { color: '#155724', fontWeight: 'bold' }
});
