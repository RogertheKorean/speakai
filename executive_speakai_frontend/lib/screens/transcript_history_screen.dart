import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class TranscriptHistoryScreen extends StatefulWidget {
  const TranscriptHistoryScreen({Key? key}) : super(key: key);

  @override
  _TranscriptHistoryScreenState createState() => _TranscriptHistoryScreenState();
}

class _TranscriptHistoryScreenState extends State<TranscriptHistoryScreen> {
  List<dynamic> history = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    fetchTranscriptHistory();
  }

  Future<void> fetchTranscriptHistory() async {
    final response = await http.get(
      Uri.parse('http://<YOUR_BACKEND_URL>/history'), // 🔁 Replace with your backend
      headers: {
        'Authorization': 'Bearer YOUR_JWT_TOKEN', // 🔐 If using JWT
      },
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      setState(() {
        history = data.reversed.toList(); // most recent first
        isLoading = false;
      });
    } else {
      setState(() => isLoading = false);
      print('Failed to fetch history');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('🗂️ Transcript History')),
      body: isLoading
          ? Center(child: CircularProgressIndicator())
          : history.isEmpty
          ? Center(child: Text('No transcripts found.'))
          : ListView.builder(
        itemCount: history.length,
        itemBuilder: (context, index) {
          final item = history[index];
          return ExpansionTile(
            title: Text(
              item['created_at'] != null
                  ? item['created_at'].substring(0, 19).replaceAll('T', ' ')
                  : 'Untitled Session',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            children: [
              ListTile(
                title: Text('📝 Transcript'),
                subtitle: Text(item['transcript'] ?? 'N/A'),
              ),
              ListTile(
                title: Text('💡 GPT Feedback'),
                subtitle: Text(item['feedback'] ?? 'N/A'),
              ),
            ],
          );
        },
      ),
    );
  }
}
