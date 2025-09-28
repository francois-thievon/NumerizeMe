import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/auth_service.dart';

class AuthProvider with ChangeNotifier {
  bool _isAuthenticated = false;
  String? _token;
  String? _username;
  String? _email;
  final AuthService _authService = AuthService();

  bool get isAuthenticated => _isAuthenticated;
  String? get token => _token;
  String? get username => _username;
  String? get email => _email;

  Future<void> register({
    required String email,
    required String username,
    required String password,
  }) async {
    try {
      final response = await _authService.register(
        email: email,
        username: username,
        password: password,
      );
      
      _username = response['username'];
      _email = response['email'];
      
      // Après l'inscription réussie, connecter automatiquement
      await login(email: email, password: password);
    } catch (e) {
      throw Exception(e.toString());
    }
  }

  Future<void> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await _authService.login(
        email: email,
        password: password,
      );
      
      _token = response['access_token'];
      _email = response['email'];
      _username = response['username'];
      _isAuthenticated = true;
      
      // Sauvegarder les informations
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('token', _token!);
      await prefs.setString('username', _username!);
      await prefs.setString('email', _email!);
      
      notifyListeners();
    } catch (e) {
      _isAuthenticated = false;
      _token = null;
      notifyListeners();
      throw Exception(e.toString());
    }
  }

  Future<void> logout() async {
    _isAuthenticated = false;
    _token = null;
    _username = null;
    _email = null;
    
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('token');
    await prefs.remove('username');
    await prefs.remove('email');
    
    notifyListeners();
  }

  Future<void> checkAuthStatus() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('token');
    if (_token != null) {
      try {
        final userResponse = await _authService.getUserProfile(_token!);
        _username = userResponse['username'];
        _email = userResponse['email'];
        _isAuthenticated = true;
      } catch (e) {
        _token = null;
        _isAuthenticated = false;
        await prefs.remove('token');
      }
    } else {
      _isAuthenticated = false;
    }
    notifyListeners();
  }
}
