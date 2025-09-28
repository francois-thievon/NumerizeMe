import 'package:flutter/material.dart';
import '../models/user.dart';
import '../services/profile_service.dart';

class ProfileProvider with ChangeNotifier {
  User? _user;
  bool _isLoading = false;
  String? _error;
  final ProfileService _profileService = ProfileService();

  User? get user => _user;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> loadUserProfile(String token) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final userData = await _profileService.getUserProfile(token);
      _user = User.fromJson(userData);
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> updateUserProfile(String token, Map<String, dynamic> data) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final updatedUserData = await _profileService.updateProfile(token, data);
      _user = User.fromJson(updatedUserData);
      _error = null;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void clearProfile() {
    _user = null;
    _error = null;
    _isLoading = false;
    notifyListeners();
  }
}
