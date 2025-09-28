import React, { useEffect } from 'react';
import { View, Text, StyleSheet, SafeAreaView, Image } from 'react-native';
import { Button } from '../../components';
import authService from '../../services/authService';

const HomeScreen = ({ navigation }) => {
  // Kiểm tra trạng thái đăng nhập khi component mount
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      // Kiểm tra token đã lưu trong AsyncStorage
      const token = await authService.getStoredToken();
      if (token) {
        console.log('✅ Người dùng đã đăng nhập, chuyển đến Profile');
        navigation.navigate('Profile');
      } else {
        console.log('ℹ️ Người dùng chưa đăng nhập, ở lại HomeScreen');
      }
    } catch (error) {
      console.log('❌ Lỗi kiểm tra trạng thái đăng nhập:', error);
    }
  };

  const handleNavigateToLogin = () => {
    navigation.navigate('Login');
    console.log('Navigate to Login');
  };

  const handleNavigateToRegister = () => {
    navigation.navigate('Register');
    console.log('Navigate to Register');
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        {/* 2. Sử dụng Image component cho icon thay vì Text */}
        <View style={styles.iconContainer}>
          <Image 
            source={require('../../../assets/icon.png')} // Đảm bảo đường dẫn này đúng
            style={styles.carImage}
            resizeMode="contain"
          />
        </View>
        
        <Text style={styles.title}>Chào mừng đến với UIT-Go</Text>
        <Text style={styles.subtitle}>Ứng dụng đặt xe hàng đầu Việt Nam</Text>
        
        <View style={styles.buttonContainer}>
          <Button
            title="Đăng nhập"
            onPress={handleNavigateToLogin}
            style={styles.button}
          />
          <Button
            title="Đăng ký"
            onPress={handleNavigateToRegister}
            variant="outline"
            style={styles.button}
          />
        </View>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F8F8',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  iconContainer: {
    marginBottom: 40,
  },
  // 3. Thêm style cho Image để có kích thước
  carImage: {
    width: 150,
    height: 150,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 18,
    color: '#666',
    marginBottom: 40,
    textAlign: 'center',
  },
  buttonContainer: {
    width: '100%',
    gap: 16,
  },
  button: {
    width: '100%',
  },
});

export default HomeScreen;