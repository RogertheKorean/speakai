import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import 'register_screen.dart';
import 'session_list_page.dart';

class LoginScreen extends StatefulWidget {
  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final emailController = TextEditingController();
  final passwordController = TextEditingController();
  bool isLoading = false;

  void login() async {
    setState(() => isLoading = true);
    final auth = context.read<AuthProvider>();
    final success = await auth.login(emailController.text.trim(), passwordController.text.trim());
    setState(() => isLoading = false);

    if (success) {
      Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => SessionListPage()));
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Login failed.')));
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: Text('🔐 Login')),
    body: Padding(
      padding: EdgeInsets.all(16),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          TextField(controller: emailController, decoration: InputDecoration(labelText: 'Email'), keyboardType: TextInputType.emailAddress),
          SizedBox(height: 12),
          TextField(controller: passwordController, decoration: InputDecoration(labelText: 'Password'), obscureText: true),
          SizedBox(height: 20),
          isLoading ? CircularProgressIndicator() : ElevatedButton(onPressed: login, child: Text('Login')),
          SizedBox(height: 12),
          TextButton(
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => RegisterScreen())),
            child: Text("Don't have an account? Register"),
          ),
        ],
      ),
    ),
  );
}
