import apiService from './apiService';
import AsyncStorage from '@react-native-async-storage/async-storage';

class AuthService {
  constructor() {
    this.currentUser = null;
    this.token = null;
  }

  // Login user
  async login(email, password) {
    try {
      const response = await fetch('http://192.168.88.137:8000/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        console.log('Login error:', errorData);
        throw new Error(`Login failed: ${errorData.detail || 'Unknown error'}`);
      }
      
      const data = await response.json();
      console.log('Login success:', data);
      
      // Lưu token và thông tin user
      if (data.access_token) {
        this.token = data.access_token;
        this.currentUser = data.user || { email };
        
        // Store token in async storage
        await AsyncStorage.setItem('userToken', data.access_token);
        await AsyncStorage.setItem('userData', JSON.stringify(this.currentUser));
        
        console.log('Token saved:', data.access_token);
        console.log('✅ Token đã lưu vào AsyncStorage (persistent)');
        console.log('✅ User data đã lưu vào AsyncStorage');
      }
      
      return data;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }

  // Register user
  async register(userData) {
    try {
      const response = await fetch('http://192.168.88.137:8000/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username: userData.username,
          email: userData.email,
          password: userData.password,
          full_name: userData.full_name || null, // Optional
          user_type: userData.user_type
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        console.log('Register error:', errorData);
        
        // Handle validation errors
        let errorMessage = 'Registration failed';
        if (errorData.detail && Array.isArray(errorData.detail)) {
          errorMessage = errorData.detail.map(err => err.msg).join(', ');
        } else if (errorData.detail) {
          errorMessage = errorData.detail;
        }
        
        throw new Error(errorMessage);
      }
      
      const data = await response.json();
      console.log('Register success:', data);
      
      return data;
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  }

  // Logout user
  async logout() {
    try {
      // Clear local data
      this.token = null;
      this.currentUser = null;
      
      // Remove token from storage
      await AsyncStorage.removeItem('userToken');
      await AsyncStorage.removeItem('userData');
      console.log('✅ Logged out successfully - Token removed from AsyncStorage');
      
      return true;
    } catch (error) {
      console.error('Logout failed:', error);
      throw error;
    }
  }

  // Get current user info
  async getCurrentUser() {
    try {
      const token = await AsyncStorage.getItem('userToken');
      if (!token) {
        throw new Error('No authentication token');
      }

      const response = await fetch('http://192.168.88.137:8000/users/me', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`Get user failed: ${errorData.detail || 'Unknown error'}`);
      }
      
      const data = await response.json();
      this.currentUser = data;
      return data;
    } catch (error) {
      console.error('Get current user failed:', error);
      throw error;
    }
  }

  // Check if user is authenticated
  isAuthenticated() {
    return !!this.token;
  }

  // Get stored token (persistent storage)
  async getStoredToken() {
    try {
      const token = await AsyncStorage.getItem('userToken');
      const userData = await AsyncStorage.getItem('userData');
      if (token) {
        this.token = token;
        this.currentUser = userData ? JSON.parse(userData) : null;
        console.log('✅ Token restored from AsyncStorage:', token.substring(0, 20) + '...');
        console.log('✅ User data restored from AsyncStorage');
      }
      return token;
    } catch (error) {
      console.error('Error getting stored token:', error);
      return null;
    }
  }

  // Initialize auth state from storage (call this when app starts)
  async initializeAuth() {
    try {
      const token = await this.getStoredToken();
      return !!token;
    } catch (error) {
      console.error('Error initializing auth:', error);
      return false;
    }
  }
}

export default new AuthService();