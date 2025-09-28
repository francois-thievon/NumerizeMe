import 'package:dio/dio.dart';

class ApiService {
  final Dio _dio = Dio();
  final String _baseUrl = 'http://10.0.2.2:8000'; // Pour l'émulateur Android

  ApiService() {
    _dio.options.baseUrl = _baseUrl;
  }

  Future<Response> login(String email, String password) async {
    try {
      final response = await _dio.post('/api/login', data: {
        'email': email,
        'password': password,
      });
      return response;
    } catch (e) {
      if (e is DioException) {
        if (e.response?.statusCode == 401) {
          throw Exception('Invalid email or password');
        }
      }
      throw Exception('Failed to connect to server');
    }
  }

  Future<Response> register(String email, String username, String password) async {
    try {
      print('Attempting to register with URL: ${_dio.options.baseUrl}/api/register');
      final response = await _dio.post('/api/register', data: {
        'email': email,
        'username': username,
        'password': password,
      });
      print('Registration response: ${response.data}');
      return response;
    } catch (e) {
      if (e is DioException) {
        print('DioException during registration: ${e.message}');
        print('Response data: ${e.response?.data}');
        print('Response status code: ${e.response?.statusCode}');
        if (e.response?.statusCode == 400) {
          throw Exception(e.response?.data['detail'] ?? 'Registration failed');
        }
      }
      print('Registration error: $e');
      throw Exception('Failed to connect to server: ${e.toString()}');
    }
  }
}
