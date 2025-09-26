# UIT Go - React Native App

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Button/         # Custom button component
│   ├── Input/          # Custom input component
│   ├── Loading/        # Loading spinner component
│   └── index.js        # Component exports
├── screens/            # App screens/pages
│   ├── HomeScreen/     # Home screen
│   ├── LoginScreen/    # Login screen
│   └── index.js        # Screen exports
├── services/           # API and business logic
│   ├── apiService.js   # HTTP request handler
│   ├── authService.js  # Authentication service
│   └── index.js        # Service exports
├── utils/              # Utility functions
│   ├── helpers.js      # General helper functions
│   ├── storage.js      # AsyncStorage wrapper
│   └── index.js        # Utility exports
├── hooks/              # Custom React hooks
│   └── index.js        # Custom hooks (useLoading, useForm, etc.)
├── constants/          # App constants
│   └── index.js        # Colors, sizes, screen names, etc.
├── navigation/         # Navigation setup
│   ├── AppNavigator.jsx # Main navigation component
│   └── index.js        # Navigation exports
├── App.jsx            # Main app component
└── index.js           # Main src exports
```

## Components

### Button
- Customizable button with multiple variants (primary, secondary, outline)
- Supports disabled state and custom styling

### Input
- Text input with label and error message support
- Supports various keyboard types and secure text entry

### Loading
- Simple loading spinner component

## Services

### ApiService
- HTTP request wrapper with GET, POST, PUT, DELETE methods
- Authentication token management
- Error handling

### AuthService
- User authentication (login, register, logout)
- Token management
- User session handling

## Utilities

### Helpers
- Date formatting
- Email/phone validation
- Currency formatting
- GPA calculation
- String utilities

### Storage
- AsyncStorage wrapper for data persistence
- User token and data management

## Custom Hooks

- **useLoading**: Loading state management
- **useForm**: Form validation and state management
- **useDebounce**: Debounced value hook
- **useApi**: API call state management

## Constants

- Colors (primary, secondary, UIT brand colors)
- Font sizes and spacing
- Screen names
- API endpoints

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. For navigation (optional):
   ```bash
   npm install @react-navigation/native @react-navigation/native-stack
   npx expo install react-native-screens react-native-safe-area-context
   ```

3. For storage (optional):
   ```bash
   npx expo install @react-native-async-storage/async-storage
   ```

4. Start the development server:
   ```bash
   npm start
   ```

## Usage Examples

### Import components:
```jsx
import { Button, Input, Loading } from './src/components';
```

### Import services:
```jsx
import { apiService, authService } from './src/services';
```

### Import utilities:
```jsx
import { formatDate, validateEmail, storageService } from './src/utils';
```

### Import hooks:
```jsx
import { useLoading, useForm } from './src/hooks';
```

### Import constants:
```jsx
import { COLORS, SIZES, SCREEN_NAMES } from './src/constants';
```

## Notes

- Some features require additional packages (React Navigation, AsyncStorage)
- Replace API_BASE_URL in apiService.js with your actual API endpoint
- Update colors and styling to match UIT branding requirements
- Add more components and screens as needed for your specific app requirements