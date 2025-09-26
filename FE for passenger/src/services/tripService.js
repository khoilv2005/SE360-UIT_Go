import apiService from './apiService';

class TripService {
  // Get all trips
  async getAllTrips(params = {}) {
    try {
      const response = await apiService.getWithAuth('/trips', params, 'TRIP');
      return response;
    } catch (error) {
      console.error('Get trips failed:', error);
      throw error;
    }
  }

  // Get trip by ID
  async getTripById(tripId) {
    try {
      const response = await apiService.getWithAuth(`/trips/${tripId}`, {}, 'TRIP');
      return response;
    } catch (error) {
      console.error('Get trip by ID failed:', error);
      throw error;
    }
  }

  // Create new trip
  async createTrip(tripData) {
    try {
      const response = await apiService.postWithAuth('/trips', tripData, 'TRIP');
      return response;
    } catch (error) {
      console.error('Create trip failed:', error);
      throw error;
    }
  }

  // Book a trip
  async bookTrip(tripId, bookingData) {
    try {
      const response = await apiService.postWithAuth(`/trips/${tripId}/book`, bookingData, 'TRIP');
      return response;
    } catch (error) {
      console.error('Book trip failed:', error);
      throw error;
    }
  }

  // Cancel trip booking
  async cancelBooking(tripId, bookingId) {
    try {
      const response = await apiService.deleteWithAuth(`/trips/${tripId}/bookings/${bookingId}`, 'TRIP');
      return response;
    } catch (error) {
      console.error('Cancel booking failed:', error);
      throw error;
    }
  }

  // Update trip status
  async updateTripStatus(tripId, status) {
    try {
      const response = await apiService.putWithAuth(`/trips/${tripId}/status`, { status }, 'TRIP');
      return response;
    } catch (error) {
      console.error('Update trip status failed:', error);
      throw error;
    }
  }

  // Search trips
  async searchTrips(searchParams) {
    try {
      const response = await apiService.getWithAuth('/trips/search', searchParams, 'TRIP');
      return response;
    } catch (error) {
      console.error('Search trips failed:', error);
      throw error;
    }
  }

  // Get user's trips (as passenger)
  async getMyTrips() {
    try {
      const response = await apiService.getWithAuth('/trips/my-trips', {}, 'TRIP');
      return response;
    } catch (error) {
      console.error('Get my trips failed:', error);
      throw error;
    }
  }
}

export default new TripService();