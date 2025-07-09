import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';

class SettingsScreen extends StatefulWidget {
  @override
  _SettingsScreenState createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool isDarkMode = false;

  @override
  void initState() {
    super.initState();
    // Could load saved preference here, simplified now
  }

  void toggleDarkMode(bool value) {
    setState(() => isDarkMode = value);
    // You can implement saving preference & applying theme
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.read<AuthProvider>();

    return Scaffold(
      appBar: AppBar(title: Text('⚙️ Settings')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            SwitchListTile(
              title: Text('Dark Mode'),
              value: isDarkMode,
              onChanged: toggleDarkMode,
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: () async {
                await auth.logout();
                Navigator.of(context).popUntil((route) => route.isFirst);
              },
              child: Text('Logout'),
            )
          ],
        ),
      ),
    );
  }
}
