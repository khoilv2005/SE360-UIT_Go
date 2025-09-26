    import React from 'react';
    import { View, Text, StyleSheet, SafeAreaView } from 'react-native';
    import { Button } from '../../components';

const HomeScreen = ({ navigation }) => {
  const handleNavigateToLogin = () => {
    navigation.navigate('Login');
    console.log('Navigate to Login');
  };

  const handleNavigateToRegister = () => {
    navigation.navigate('Register');
    console.log('Navigate to Register');
  };

  const handleNavigateToProfile = () => {
    navigation.navigate('Profile');
    console.log('Navigate to Profile');
  };    return (
        <SafeAreaView style={styles.container}>
        <View style={styles.content}>
            <Text style={styles.title}>Chào mừng đến với UIT-Go</Text>
            <Text style={styles.subtitle}>Ứng dụng đặt xe hàng đầu việt nam</Text>
            
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