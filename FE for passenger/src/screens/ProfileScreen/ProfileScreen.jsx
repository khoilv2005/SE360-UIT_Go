import React, { useState, useEffect, } from 'react';
import {Image} from 'react-native';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  Alert,
  TouchableOpacity,
  SafeAreaView,
  StatusBar
} from 'react-native';
import { Loading, LoadingWithHeader, SplashLoading } from '../../components';
import authService from '../../services/authService';

const ProfileScreen = ({ navigation }) => {
  const [userProfile, setUserProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState('profile');

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

  // Hàm xử lý chuyển tab
  const handleTabPress = (tabName) => {
    setActiveTab(tabName);
    switch(tabName) {
      case 'home':
        console.log('Chuyển đến Trang chủ');
        // navigation.navigate('Home');
        break;
      case 'list':
        console.log('Chuyển đến Danh sách');
        // navigation.navigate('List');
        break;
      case 'message':
        console.log('Chuyển đến Tin nhắn');
        // navigation.navigate('Message');
        break;
      case 'profile':
        console.log('Đang ở Profile');
        break;
      default:
        break;
    }
  };

  useEffect(() => {
    fetchUserProfile();
  }, []);

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="light-content" backgroundColor="#007AFF" />
        <Loading />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#007AFF" />
      
      {/* Header với nút đăng xuất */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Thông tin cá nhân</Text>
        <TouchableOpacity style={styles.logoutHeaderButton} onPress={handleLogout}>
          <Text style={styles.logoutHeaderText}>Đăng xuất</Text>
        </TouchableOpacity>
      </View>
      
      <ScrollView
        style={styles.scrollContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
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
          </View>
        )}
      </ScrollView>

      {/* Bottom Navigation */}
      <View style={styles.bottomNavigation}>
        <TouchableOpacity 
          style={[styles.tabItem, activeTab === 'home' && styles.activeTab]}
          onPress={() => handleTabPress('home')}
        >
          <Image 
            source={require('../../../assets/car.png')}
            style={[styles.tabIcon, { tintColor: activeTab === 'home' ? '#fff' : '#666' }]}
          />
          
          <Text style={[styles.tabText, activeTab === 'home' && styles.activeTabText]}>
            Trang chủ
          </Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.tabItem, activeTab === 'list' && styles.activeTab]}
          onPress={() => handleTabPress('list')}
        >
          <Text style={styles.tabIcon}>📋</Text>
          <Text style={[styles.tabText, activeTab === 'list' && styles.activeTabText]}>
            Danh sách
          </Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.tabItem, activeTab === 'message' && styles.activeTab]}
          onPress={() => handleTabPress('message')}
        >
          <Text style={styles.tabIcon}>💬</Text>
          <Text style={[styles.tabText, activeTab === 'message' && styles.activeTabText]}>
            Tin nhắn
          </Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.tabItem, activeTab === 'profile' && styles.activeTab]}
          onPress={() => handleTabPress('profile')}
        >
          <Text style={styles.tabIcon}>👤</Text>
          <Text style={[styles.tabText, activeTab === 'profile' && styles.activeTabText]}>
            Profile
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  // Header styles
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: '#007AFF',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 5,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
  },
  logoutHeaderButton: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.3)',
  },
  logoutHeaderText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  scrollContainer: {
    flex: 1,
    paddingBottom: 20,
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
  content: {
    padding: 20,
    paddingTop: 20,
    paddingBottom: 100, // Thêm padding để không bị che bởi bottom nav
  },
  profileCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 24,
    marginHorizontal: 4,
    marginBottom: 20,
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
    marginBottom: 20,
    paddingBottom: 18,
    paddingHorizontal: 4,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  label: {
    fontSize: 14,
    color: '#666',
    marginBottom: 6,
    fontWeight: '500',
  },
  value: {
    fontSize: 16,
    color: '#333',
    fontWeight: '600',
    lineHeight: 22,
  },
  // Bottom Navigation Styles
  bottomNavigation: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: -2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 8,
  },
  tabItem: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 8,
    borderRadius: 12,
    marginHorizontal: 4,
  },
  activeTab: {
    backgroundColor: '#007AFF',
  },
  tabIcon: {
    width: 22, // Giảm kích thước chiều rộng
    height: 22, // Giảm kích thước chiều cao
    marginBottom: 4,
  },
  tabText: {
    fontSize: 12,
    color: '#666',
    fontWeight: '500',
  },
  activeTabText: {
    color: '#fff',
    fontWeight: 'bold',
  },
});

export default ProfileScreen;