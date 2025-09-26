import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  Alert,
  TouchableOpacity
} from 'react-native';
import { Loading } from '../../components';
import authService from '../../services/authService';

const ProfileScreen = ({ navigation }) => {
  const [userProfile, setUserProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchUserProfile = async () => {
    try {
      setLoading(true);
      const userData = await authService.getCurrentUser();
      console.log('User profile data:', userData);
      setUserProfile(userData);
    } catch (error) {
      console.error('Error fetching user profile:', error);
      Alert.alert(
        'Lỗi',
        'Không thể tải thông tin người dùng: ' + error.message
      );
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchUserProfile();
    setRefreshing(false);
  };

  const handleLogout = async () => {
    Alert.alert(
      'Đăng xuất',
      'Bạn có chắc chắn muốn đăng xuất?',
      [
        { text: 'Hủy', style: 'cancel' },
        {
          text: 'Đăng xuất',
          style: 'destructive',
          onPress: async () => {
            try {
              await authService.logout();
              navigation.navigate('Login');
            } catch (error) {
              Alert.alert('Lỗi', 'Không thể đăng xuất: ' + error.message);
            }
          }
        }
      ]
    );
  };

  useEffect(() => {
    fetchUserProfile();
  }, []);

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Loading />
        <Text style={styles.loadingText}>Đang tải thông tin...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.title}>Thông tin cá nhân</Text>
      </View>

      {userProfile && (
        <View style={styles.content}>
          <View style={styles.profileCard}>
            <View style={styles.profileItem}>
              <Text style={styles.label}>Tên đăng nhập:</Text>
              <Text style={styles.value}>{userProfile.username || 'Chưa cập nhật'}</Text>
            </View>

            <View style={styles.profileItem}>
              <Text style={styles.label}>Email:</Text>
              <Text style={styles.value}>{userProfile.email || 'Chưa cập nhật'}</Text>
            </View>

            <View style={styles.profileItem}>
              <Text style={styles.label}>Họ và tên:</Text>
              <Text style={styles.value}>{userProfile.full_name || 'Chưa cập nhật'}</Text>
            </View>

            <View style={styles.profileItem}>
              <Text style={styles.label}>Loại tài khoản:</Text>
              <Text style={styles.value}>
                {userProfile.user_type === 'PASSENGER' ? 'Hành khách' : 
                 userProfile.user_type === 'DRIVER' ? 'Tài xế' : userProfile.user_type}
              </Text>
            </View>

            {userProfile.created_at && (
              <View style={styles.profileItem}>
                <Text style={styles.label}>Ngày tạo tài khoản:</Text>
                <Text style={styles.value}>
                  {new Date(userProfile.created_at).toLocaleDateString('vi-VN')}
                </Text>
              </View>
            )}
          </View>

          <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
            <Text style={styles.logoutButtonText}>Đăng xuất</Text>
          </TouchableOpacity>
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
  header: {
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
  },
  content: {
    padding: 20,
  },
  profileCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  profileItem: {
    marginBottom: 16,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  label: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
    fontWeight: '500',
  },
  value: {
    fontSize: 16,
    color: '#333',
    fontWeight: '600',
  },
  logoutButton: {
    backgroundColor: '#dc3545',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    marginTop: 20,
    alignItems: 'center',
  },
  logoutButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default ProfileScreen;