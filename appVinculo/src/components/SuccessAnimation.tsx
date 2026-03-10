import React, { useEffect, useRef } from 'react';
import { View, StyleSheet } from 'react-native';
import LottieView from 'lottie-react-native';

interface SuccessAnimationProps {
  visible: boolean;
  onAnimationFinish?: () => void;
}

export default function SuccessAnimation({ visible, onAnimationFinish }: SuccessAnimationProps) {
  const animationRef = useRef<LottieView>(null);

  useEffect(() => {
    if (visible) {
      animationRef.current?.play();
    }
  }, [visible]);

  if (!visible) return null;

  return (
    <View style={StyleSheet.absoluteFillObject} className="z-50 items-center justify-center bg-black/60">
      <LottieView
        ref={animationRef}
        // Utilizando una URL pública para un check o confeti (o puedes descargar el lottie json y usar require())
        source={{ uri: 'https://assets9.lottiefiles.com/packages/lf20_x2kida9w.json' }}
        autoPlay={false}
        loop={false}
        style={{ width: 300, height: 300 }}
        onAnimationFinish={onAnimationFinish}
      />
    </View>
  );
}
