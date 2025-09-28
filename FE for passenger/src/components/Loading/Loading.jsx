import React from 'react';
import { 
  View, 
  StyleSheet, 
  Text, 
  Image
} from 'react-native';

// Loading component chỉ hiển thị GIF toàn màn hình
const Loading = ({ style }) => {
  return (
    <View style={[styles.fullScreenContainer, style]}>
      <Image
        source={require('../../../assets/splasing.gif')}
        style={styles.fullScreenGif}
        resizeMode="cover"
      />
    </View>
  );
};

// Component loading GIF toàn màn hình
export const SplashLoading = () => {
  return (
    <View style={styles.fullScreenContainer}>
      <Image
        source={require('../../../assets/splasing.gif')}
        style={styles.fullScreenGif}
        resizeMode="cover"
      />
    </View>
  );
};

// Component loading GIF toàn màn hình (không cần header)
export const LoadingWithHeader = () => {
  return (
    <View style={styles.fullScreenContainer}>
      <Image
        source={require('../../../assets/splasing.gif')}
        style={styles.fullScreenGif}
        resizeMode="cover"
      />
    </View>
  );
};

const styles = StyleSheet.create({
  fullScreenContainer: {
    flex: 1,
    width: '100%',
    height: '100%',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
  },
  fullScreenGif: {
    flex: 1,
    width: '100%',
    height: '100%',
  },
});

export default Loading;