import React, { useState } from 'react';
import { 
  View, 
  Text, 
  TouchableOpacity, 
  StyleSheet, 
  Alert,
  ScrollView,
  ActivityIndicator 
} from 'react-native';

const MainScreen = () => {
  const [loading, setLoading] = useState(false);
  const [fareEstimates, setFareEstimates] = useState(null);
  const [selectedVehicle, setSelectedVehicle] = useState(null);
  
  // Mock coordinates - trong thực tế sẽ lấy từ map
  const [pickupCoords] = useState({
    latitude: 10.7769,
    longitude: 106.6952
  });
  
  const [dropoffCoords] = useState({
    latitude: 10.8700,
    longitude: 106.8030
  });

  // Hàm gọi API estimate fare
  const getFareEstimates = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8001/fare-estimate/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pickup: pickupCoords,
          dropoff: dropoffCoords
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        setFareEstimates(data.estimates);
      } else {
        Alert.alert('Lỗi', 'Không thể tính giá cước');
      }
    } catch (error) {
      console.error('Error:', error);
      Alert.alert('Lỗi', 'Không thể kết nối tới server');
    } finally {
      setLoading(false);
    }
  };

  // Hàm tạo trip request
  const createTripRequest = async () => {
    if (!selectedVehicle) {
      Alert.alert('Thông báo', 'Vui lòng chọn loại xe');
      return;
    }

    setLoading(true);
    try {
      const tripData = {
        passenger_id: "passenger123", // Trong thực tế lấy từ user context
        pickup: {
          address: "227 Nguyễn Văn Cừ, Quận 5", // Sẽ reverse geocode từ coordinates
          latitude: pickupCoords.latitude,
          longitude: pickupCoords.longitude
        },
        dropoff: {
          address: "UIT, Thủ Đức", // Sẽ reverse geocode từ coordinates  
          latitude: dropoffCoords.latitude,
          longitude: dropoffCoords.longitude
        },
        vehicle_type: selectedVehicle.vehicle_type,
        route_geometry: selectedVehicle.route_geometry,
        payment_method: "CASH",
        notes: "Đặt xe từ app"
      };

      const response = await fetch('http://localhost:8001/trip-requests/complete/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(tripData)
      });

      const result = await response.json();
      
      if (response.ok) {
        Alert.alert('Thành công', 'Đã tạo chuyến đi thành công!');
        // Reset state
        setFareEstimates(null);
        setSelectedVehicle(null);
      } else {
        Alert.alert('Lỗi', 'Không thể tạo chuyến đi');
      }
    } catch (error) {
      console.error('Error:', error);
      Alert.alert('Lỗi', 'Không thể kết nối tới server');
    } finally {
      setLoading(false);
    }
  };

  const getVehicleTypeName = (type) => {
    switch (type) {
      case '2_SEATER': return 'Xe máy (2 chỗ)';
      case '4_SEATER': return 'Ô tô (4 chỗ)';
      case '7_SEATER': return 'Ô tô (7 chỗ)';
      default: return type;
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(amount);
  };

  const formatTime = (seconds) => {
    const minutes = Math.ceil(seconds / 60);
    return `${minutes} phút`;
  };

  const formatDistance = (meters) => {
    const km = (meters / 1000).toFixed(1);
    return `${km} km`;
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>UIT-Go - Đặt xe</Text>
      
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Điểm đón & điểm đến</Text>
        <Text>📍 Từ: Quận 5 ({pickupCoords.latitude}, {pickupCoords.longitude})</Text>
        <Text>📍 Đến: UIT Thủ Đức ({dropoffCoords.latitude}, {dropoffCoords.longitude})</Text>
      </View>

      {!fareEstimates && (
        <TouchableOpacity 
          style={styles.button} 
          onPress={getFareEstimates}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="white" />
          ) : (
            <Text style={styles.buttonText}>Tính giá cước</Text>
          )}
        </TouchableOpacity>
      )}

      {fareEstimates && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Chọn loại xe:</Text>
          
          {fareEstimates.map((estimate, index) => (
            <TouchableOpacity
              key={index}
              style={[
                styles.vehicleOption,
                selectedVehicle?.vehicle_type === estimate.vehicle_type && styles.selectedVehicle
              ]}
              onPress={() => setSelectedVehicle(estimate)}
            >
              <View style={styles.vehicleInfo}>
                <Text style={styles.vehicleType}>
                  {getVehicleTypeName(estimate.vehicle_type)}
                </Text>
                <Text style={styles.vehicleDetails}>
                  {formatDistance(estimate.distance_meters)} • {formatTime(estimate.duration_seconds)}
                </Text>
              </View>
              <Text style={styles.price}>
                {formatCurrency(estimate.estimated_fare)}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      )}

      {selectedVehicle && (
        <TouchableOpacity 
          style={styles.bookButton} 
          onPress={createTripRequest}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="white" />
          ) : (
            <Text style={styles.buttonText}>Đặt xe</Text>
          )}
        </TouchableOpacity>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20,
    color: '#333',
  },
  section: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 10,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginBottom: 15,
  },
  bookButton: {
    backgroundColor: '#28A745',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginBottom: 15,
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  vehicleOption: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
    backgroundColor: '#f8f9fa',
    borderWidth: 2,
    borderColor: 'transparent',
  },
  selectedVehicle: {
    borderColor: '#007AFF',
    backgroundColor: '#e3f2fd',
  },
  vehicleInfo: {
    flex: 1,
  },
  vehicleType: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  vehicleDetails: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  price: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#28A745',
  },
});

export default MainScreen;