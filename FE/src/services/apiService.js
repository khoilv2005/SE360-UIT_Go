// Multiple service URLs
// Sử dụng 127.0.0.1 cho emulator/web, 192.168.1.14 cho điện thoại thật
const SERVICE_URLS = {
 // USER: 'http://127.0.0.1:8000',    // Cho emulator/web
  USER: 'http://192.168.1.14:8000',  // Cho điện thoại thật qua Expo Go
  TRIP: 'http://127.0.0.1:8001', 
  DRIVER: 'http://127.0.0.1:8002',
};

class ApiService {
  constructor() {
    this.serviceUrls = SERVICE_URLS;
    this.useMockData = false; // Set to true for development without backend
  }

  // Get the appropriate base URL for the service
  getServiceUrl(service = 'USER') {
    return this.serviceUrls[service] || this.serviceUrls.USER;
  }

  // Format data as x-www-form-urlencoded
  formatRequestBody(data) {
    if (typeof data === 'object' && data !== null) {
      const params = new URLSearchParams();
      Object.keys(data).forEach(key => {
        if (data[key] !== null && data[key] !== undefined) {
          params.append(key, data[key].toString());
        }
      });
      return params.toString();
    }
    return data;
  }

  // Mock data for development
  getMockResponse(endpoint, method) {
    if (endpoint === '/auth/login' && method === 'POST') {
      return {
        success: true,
        token: 'mock_token_123',
        user: {
          id: 1,
          username: 'testuser',
          email: 'test@example.com',
          type: 'passenger'
        }
      };
    }
    
    if (endpoint === '/auth/register' && method === 'POST') {
      return {
        success: true,
        message: 'User registered successfully',
        user: {
          id: 2,
          username: 'newuser',
          email: 'new@example.com',
          type: 'driver'
        }
      };
    }
    
    return { success: true, data: 'Mock response' };
  }

  async request(endpoint, options = {}) {
    const { service = 'USER', ...restOptions } = options;
    
    // Return mock data if enabled
    if (this.useMockData) {
      console.log(`🔸 Using mock data for: ${endpoint}`);
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate network delay
      return this.getMockResponse(endpoint, restOptions.method || 'GET');
    }
    
    const baseUrl = this.getServiceUrl(service);
    const url = `${baseUrl}${endpoint}`;
    const config = {
      headers: {
        // Default headers - can be overridden by restOptions.headers
        ...restOptions.headers,
      },
      ...restOptions,
    };

    try {
      console.log(`Making request to: ${url}`);
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API request failed:', error);
      console.error('URL:', url);
      console.error('Config:', config);
      
      // More specific error messages
      if (error.message === 'Network request failed') {
        throw new Error('Không thể kết nối đến server. Vui lòng kiểm tra:✅ Backend services đang chạy✅ URL đúng định dạng');
      }
      
      throw error;
    }
  }

  // GET request
  async get(endpoint, params = {}, service = 'USER') {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    
    return this.request(url, {
      method: 'GET',
      service,
    });
  }

  // POST request
  async post(endpoint, data = {}, service = 'USER') {
    return this.request(endpoint, {
      method: 'POST',
      body: this.formatRequestBody(data),
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      service,
    });
  }

  // PUT request
  async put(endpoint, data = {}, service = 'USER') {
    return this.request(endpoint, {
      method: 'PUT',
      body: this.formatRequestBody(data),
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      service,
    });
  }

  // DELETE request
  async delete(endpoint, service = 'USER') {
    return this.request(endpoint, {
      method: 'DELETE',
      service,
    });
  }

  // Set authorization token
  setAuthToken(token) {
    this.authToken = token;
  }

  // Enable/disable mock data for development
  setMockMode(enabled) {
    this.useMockData = enabled;
    console.log(`🔸 Mock mode ${enabled ? 'ENABLED' : 'DISABLED'}`);
  }

  // Get request with auth
  async getWithAuth(endpoint, params = {}, service = 'USER') {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    
    return this.request(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${this.authToken}`,
      },
      service,
    });
  }

  // POST request with auth
  async postWithAuth(endpoint, data = {}, service = 'USER') {
    return this.request(endpoint, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.authToken}`,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: this.formatRequestBody(data),
      service,
    });
  }

  // PUT request with auth
  async putWithAuth(endpoint, data = {}, service = 'USER') {
    return this.request(endpoint, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${this.authToken}`,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: this.formatRequestBody(data),
      service,
    });
  }

  // DELETE request with auth
  async deleteWithAuth(endpoint, service = 'USER') {
    return this.request(endpoint, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${this.authToken}`,
      },
      service,
    });
  }
}

export default new ApiService();