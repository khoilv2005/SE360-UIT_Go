import React, { useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { HomeScreen, LoginScreen, RegisterScreen, ProfileScreen } from './screens';
import { authService } from './services';

const Stack = createNativeStackNavigator();

const App = () => {
  // Initialize auth state from AsyncStorage when app starts
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const isLoggedIn = await authService.initializeAuth();
        if (isLoggedIn) {
          console.log('✅ User already logged in from previous session');
        } else {
          console.log('ℹ️ No previous session found');
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
      }
    };
    
    initializeAuth();
  }, []);

  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName="Home"
        screenOptions={{
          headerStyle: {
            backgroundColor: '#007AFF',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}
      >
        <Stack.Screen 
          name="Home" 
          component={HomeScreen}
          options={{ title: 'UIT Go' }}
        />
        <Stack.Screen 
          name="Login" 
          component={LoginScreen}
          options={{ title: 'Đăng nhập' }}
        />
        <Stack.Screen 
          name="Register" 
          component={RegisterScreen}
          options={{ title: 'Đăng ký' }}
        />
        <Stack.Screen 
          name="Profile" 
          component={ProfileScreen}
          options={{ title: 'Thông tin cá nhân' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default App;