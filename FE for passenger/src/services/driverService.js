import apiService from './apiService';

class DriverService {
  // Register as driver
  async registerDriver(driverData) {
    try {
      const response = await apiService.postWithAuth('/drivers/register', driverData, 'DRIVER');
      return response;
    } catch (error) {
      console.error('Driver registration failed:', error);
      throw error;
    }
  }

  // Get driver profile
  async getDriverProfile() {
    try {
      const response = await apiService.getWithAuth('/drivers/profile', {}, 'DRIVER');
      return response;
    } catch (error) {
      console.error('Get driver profile failed:', error);
      throw error;
    }
  }

  // Update driver profile
  async updateDriverProfile(profileData) {
    try {
      const response = await apiService.putWithAuth('/drivers/profile', profileData, 'DRIVER');
      return response;
    } catch (error) {
      console.error('Update driver profile failed:', error);
      throw error;
    }
  }

  // Get driver's trips
  async getDriverTrips() {
    try {
      const response = await apiService.getWithAuth('/drivers/trips', {}, 'DRIVER');
      return response;
    } catch (error) {
      console.error('Get driver trips failed:', error);
      throw error;
    }
  }

  // Update driver location
  async updateLocation(locationData) {
    try {
      const response = await apiService.postWithAuth('/drivers/location', locationData, 'DRIVER');
      return response;
    } catch (error) {
      console.error('Update driver location failed:', error);
      throw error;
    }
  }

  // Set driver availability
  async setAvailability(isAvailable) {
    try {
      const response = await apiService.putWithAuth('/drivers/availability', { isAvailable }, 'DRIVER');
      return response;
    } catch (error) {
      console.error('Set driver availability failed:', error);
      throw error;
    }
  }

  // Get driver earnings
  async getEarnings(params = {}) {
    try {
      const response = await apiService.getWithAuth('/drivers/earnings', params, 'DRIVER');
      return response;
    } catch (error) {
      console.error('Get driver earnings failed:', error);
      throw error;
    }
  }

  // Accept trip request
  async acceptTrip(tripId) {
    try {
      const response = await apiService.postWithAuth(`/drivers/trips/${tripId}/accept`, {}, 'DRIVER');
      return response;
    } catch (error) {
      console.error('Accept trip failed:', error);
      throw error;
    }
  }

  // Reject trip request
  async rejectTrip(tripId, reason) {
    try {
      const response = await apiService.postWithAuth(`/drivers/trips/${tripId}/reject`, { reason }, 'DRIVER');
      return response;
    } catch (error) {
      console.error('Reject trip failed:', error);
      throw error;
    }
  }

  // Complete trip
  async completeTrip(tripId) {
    try {
      const response = await apiService.postWithAuth(`/drivers/trips/${tripId}/complete`, {}, 'DRIVER');
      return response;
    } catch (error) {
      console.error('Complete trip failed:', error);
      throw error;
    }
  }

  // Upload driver documents
  async uploadDocuments(documentsData) {
    try {
      const response = await apiService.postWithAuth('/drivers/documents', documentsData, 'DRIVER');
      return response;
    } catch (error) {
      console.error('Upload documents failed:', error);
      throw error;
    }
  }
}

export default new DriverService();