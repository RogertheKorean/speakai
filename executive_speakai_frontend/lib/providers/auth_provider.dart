import 'package:flutter/material.dart';
import '../api_service.dart';

class AuthProvider extends ChangeNotifier {
  String? _token;
  bool get isAuthenticated => _token != null;

  String? get token => _token;

  Future<bool> login(String email, String password) async {
    final token = await ApiService.login(email, password);
    if (token != null) {
      _token = token;
      notifyListeners();
      return true;
    }
    return false;
  }

  Future<bool> register(String email, String password) async {
    return await ApiService.register(email, password);
  }

  Future<void> logout() async {
    _token = null;
    await ApiService.clearToken();
    notifyListeners();
  }
}
