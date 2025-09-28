import React, { useState } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  SafeAreaView, 
  ScrollView,
  Alert 
} from 'react-native';
import { Button, Loading, SplashLoading, LoadingWithHeader } from '../../components';

const TestLoadingScreen = ({ navigation }) => {
  const [currentTest, setCurrentTest] = useState(null);

  const runTest = (testType, duration = 3000) => {
    setCurrentTest(testType);
    setTimeout(() => {
      setCurrentTest(null);
      Alert.alert('✅ Hoàn thành!', `Test ${testType} đã kết thúc`);
    }, duration);
  };

  // Render loading dựa theo test type
  if (currentTest === 'splash') {
    return <SplashLoading loadingText="🚗 UIT-Go đang khởi động..." />;
  }

  if (currentTest === 'basic') {
    return (
      <SafeAreaView style={styles.container}>
        <Loading text="Loading cơ bản..." />
      </SafeAreaView>
    );
  }

  if (currentTest === 'overlay') {
    return (
      <SafeAreaView style={styles.container}>
        <Text style={styles.backgroundText}>Nội dung phía sau</Text>
        <Loading 
          overlay={true} 
          text="Loading overlay..." 
          backgroundColor="rgba(0,0,0,0.7)"
        />
      </SafeAreaView>
    );
  }

  if (currentTest === 'header') {
    return (
      <SafeAreaView style={styles.container}>
        <LoadingWithHeader 
          headerTitle="Test Header Loading"
          headerColor="#007AFF"
          loadingText="Đang test loading với header..."
          useSplashIcon={true}
        />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.title}>🎬 Test Loading Components</Text>
        <Text style={styles.subtitle}>Chọn loại loading để test:</Text>

        <View style={styles.buttonGroup}>
          <Button
            title="🌟 Splash Loading (Hiệu ứng đẹp)"
            onPress={() => runTest('splash', 5000)}
            style={[styles.testButton, { backgroundColor: '#007AFF' }]}
          />

          <Button
            title="⚡ Basic Loading"
            onPress={() => runTest('basic', 3000)}
            style={[styles.testButton, { backgroundColor: '#28a745' }]}
          />

          <Button
            title="🎭 Overlay Loading"
            onPress={() => runTest('overlay', 3000)}
            style={[styles.testButton, { backgroundColor: '#ffc107' }]}
          />

          <Button
            title="📱 Header Loading"
            onPress={() => runTest('header', 4000)}
            style={[styles.testButton, { backgroundColor: '#17a2b8' }]}
          />
        </View>

        <View style={styles.infoBox}>
          <Text style={styles.infoTitle}>💡 Thông tin:</Text>
          <Text style={styles.infoText}>
            • Splash Loading: Hiệu ứng xoay, pulse với icon{'\n'}
            • Basic Loading: Spinner đơn giản{'\n'}
            • Overlay: Loading trên nội dung hiện tại{'\n'}
            • Header Loading: Có header + splash icon
          </Text>
        </View>

        <Button
          title="← Quay lại Login"
          onPress={() => navigation.goBack()}
          variant="outline"
          style={styles.backButton}
        />
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    padding: 20,
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 30,
  },
  buttonGroup: {
    width: '100%',
    marginBottom: 30,
  },
  testButton: {
    marginBottom: 15,
    paddingVertical: 15,
  },
  infoBox: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 12,
    marginBottom: 30,
    width: '100%',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  infoText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  backButton: {
    width: '100%',
  },
  backgroundText: {
    fontSize: 18,
    color: '#666',
    textAlign: 'center',
    marginTop: 100,
  },
});

export default TestLoadingScreen;