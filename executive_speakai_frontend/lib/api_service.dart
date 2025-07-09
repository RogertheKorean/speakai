import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'dart:convert';

class ApiService {
  static const String baseUrl = 'https://6a436dde2682.ngrok-free.app';
  static final FlutterSecureStorage storage = FlutterSecureStorage();

  static Future<bool> register(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}),
      );

      if (response.statusCode == 200) {
        return true;
      } else {
        print('Register failed: ${response.statusCode} ${response.body}');
        return false;
      }
    } catch (e) {
      print('Register exception: $e');
      return false;
    }
  }


  static Future<String?> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final token = data['token'];
      await storage.write(key: 'jwt_token', value: token);
      return token;
    }
    return null;
  }

  static Future<void> clearToken() async {
    await storage.delete(key: 'jwt_token');
  }

  static Future<String?> getToken() async {
    return await storage.read(key: 'jwt_token');
  }

  static Future<List<dynamic>?> fetchSessions() async {
    final token = await getToken();
    if (token == null) return null;

    final response = await http.get(
      Uri.parse('$baseUrl/sessions'),
      headers: {'Authorization': 'Bearer $token'},
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return null;
  }

  static Future<bool> deleteSession(String id) async {
    final token = await getToken();
    if (token == null) return false;

    final response = await http.delete(
      Uri.parse('$baseUrl/sessions/$id'),
      headers: {'Authorization': 'Bearer $token'},
    );

    return response.statusCode == 200;
  }
}
