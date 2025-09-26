import React, { useState } from 'react';
import { View, Text, StyleSheet, SafeAreaView, Alert, ScrollView, TouchableOpacity } from 'react-native';
import { Button, Input, Loading } from '../../components';
import { authService } from '../../services';

const RegisterScreen = ({ navigation }) => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
    user_type: '', // 'driver' hoặc 'passenger'
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const updateField = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: '',
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.username.trim()) {
      newErrors.username = 'Tên đăng nhập là bắt buộc';
    } else if (formData.username.length < 3) {
      newErrors.username = 'Tên đăng nhập phải có ít nhất 3 ký tự';
    }
    
    if (!formData.email) {
      newErrors.email = 'Email là bắt buộc';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email không hợp lệ';
    }
    
    if (!formData.password) {
      newErrors.password = 'Mật khẩu là bắt buộc';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Mật khẩu phải có ít nhất 6 ký tự';
    }
    
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Xác nhận mật khẩu là bắt buộc';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Mật khẩu xác nhận không khớp';
    }
    
    if (!formData.full_name.trim()) {
      newErrors.full_name = 'Họ và tên là bắt buộc';
    }
    
    if (!formData.user_type) {
      newErrors.user_type = 'Vui lòng chọn loại tài khoản';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleRegister = async () => {
    if (!validateForm()) return;

    setLoading(true);
    try {
      const userData = {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
        user_type: formData.user_type,
      };
      
      await authService.register(userData);
      Alert.alert(
        'Thành công', 
        'Đăng ký thành công! Vui lòng đăng nhập.',
        [
          {
            text: 'OK',
            onPress: () => navigation.navigate('Login')
          }
        ]
      );
    } catch (error) {
      Alert.alert('Lỗi', 'Đăng ký thất bại. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  };

  const handleBackToLogin = () => {
    navigation.navigate('Login');
  };

  if (loading) {
    return <Loading />;
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.content}>
          <Text style={styles.title}>Đăng ký UIT Go</Text>
          <Text style={styles.subtitle}>Tạo tài khoản để sử dụng dịch vụ</Text>
          
          <View style={styles.form}>
            <Input
              label="Họ và tên"
              placeholder="Nhập họ và tên đầy đủ"
              value={formData.full_name}
              onChangeText={(value) => updateField('full_name', value)}
              error={errors.full_name}
            />
            
            <Input
              label="Tên đăng nhập"
              placeholder="Nhập tên đăng nhập"
              value={formData.username}
              onChangeText={(value) => updateField('username', value)}
              error={errors.username}
            />
            
            <Input
              label="Email"
              placeholder="Nhập email của bạn"
              value={formData.email}
              onChangeText={(value) => updateField('email', value)}
              keyboardType="email-address"
              error={errors.email}
            />
            
            <Input
              label="Mật khẩu"
              placeholder="Nhập mật khẩu"
              value={formData.password}
              onChangeText={(value) => updateField('password', value)}
              secureTextEntry
              error={errors.password}
            />
            
            <Input
              label="Xác nhận mật khẩu"
              placeholder="Nhập lại mật khẩu"
              value={formData.confirmPassword}
              onChangeText={(value) => updateField('confirmPassword', value)}
              secureTextEntry
              error={errors.confirmPassword}
            />
            
            {/* User Type Selection */}
            <View style={styles.userTypeContainer}>
              <Text style={styles.userTypeLabel}>Bạn là:</Text>
              <View style={styles.userTypeOptions}>
                <TouchableOpacity
                  style={[
                    styles.userTypeOption,
                    formData.user_type === 'PASSENGER' && styles.userTypeSelected
                  ]}
                  onPress={() => updateField('user_type', 'PASSENGER')}
                >
                  <View style={[
                    styles.checkbox,
                    formData.user_type === 'PASSENGER' && styles.checkboxSelected
                  ]} />
                  <Text style={[
                    styles.userTypeText,
                    formData.user_type === 'PASSENGER' && styles.userTypeTextSelected
                  ]}>
                    Hành khách
                  </Text>
                </TouchableOpacity>
                
                <TouchableOpacity
                  style={[
                    styles.userTypeOption,
                    formData.user_type === 'DRIVER' && styles.userTypeSelected
                  ]}
                  onPress={() => updateField('user_type', 'DRIVER')}
                >
                  <View style={[
                    styles.checkbox,
                    formData.user_type === 'DRIVER' && styles.checkboxSelected
                  ]} />
                  <Text style={[
                    styles.userTypeText,
                    formData.user_type === 'DRIVER' && styles.userTypeTextSelected
                  ]}>
                    Tài xế
                  </Text>
                </TouchableOpacity>
              </View>
              {errors.user_type && <Text style={styles.errorText}>{errors.user_type}</Text>}
            </View>
            
            <Button
              title="Đăng ký"
              onPress={handleRegister}
              style={styles.registerButton}
            />
            
            <Button
              title="Đã có tài khoản? Đăng nhập"
              onPress={handleBackToLogin}
              variant="outline"
              style={styles.loginButton}
            />
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F8F8',
  },
  scrollContent: {
    flexGrow: 1,
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
    paddingVertical: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 30,
  },
  form: {
    flex: 1,
  },
  registerButton: {
    marginTop: 20,
    marginBottom: 16,
  },
  loginButton: {
    marginTop: 8,
  },
  userTypeContainer: {
    marginBottom: 16,
  },
  userTypeLabel: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 12,
    color: '#333',
  },
  userTypeOptions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 16,
  },
  userTypeOption: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 16,
    paddingHorizontal: 16,
    borderWidth: 2,
    borderColor: '#DDD',
    borderRadius: 8,
    backgroundColor: '#FFF',
  },
  userTypeSelected: {
    borderColor: '#007AFF',
    backgroundColor: '#F0F8FF',
  },
  checkbox: {
    width: 20,
    height: 20,
    borderRadius: 10,
    borderWidth: 2,
    borderColor: '#DDD',
    marginRight: 12,
    backgroundColor: '#FFF',
  },
  checkboxSelected: {
    borderColor: '#007AFF',
    backgroundColor: '#007AFF',
  },
  userTypeText: {
    fontSize: 16,
    color: '#666',
    fontWeight: '500',
  },
  userTypeTextSelected: {
    color: '#007AFF',
    fontWeight: '600',
  },
  errorText: {
    color: '#FF3B30',
    fontSize: 14,
    marginTop: 4,
  },
});

export default RegisterScreen;