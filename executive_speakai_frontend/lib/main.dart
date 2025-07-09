import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/auth_provider.dart';
import 'pages/login_screen.dart';

void main() {
  runApp(
    ChangeNotifierProvider(
      create: (_) => AuthProvider(),
      child: SpeakAIApp(),
    ),
  );
}

class SpeakAIApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    // Optional: listen to dark mode preference here
    return MaterialApp(
      title: 'SpeakAI',
      theme: ThemeData.light(),
      darkTheme: ThemeData.dark(),
      home: LoginScreen(),
    );
  }
}
