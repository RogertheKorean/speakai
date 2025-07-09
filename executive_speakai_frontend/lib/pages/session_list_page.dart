import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../api_service.dart';
import '../models/session.dart';
import 'session_details_page.dart';

class SessionListPage extends StatefulWidget {
  @override
  _SessionListPageState createState() => _SessionListPageState();
}

class _SessionListPageState extends State<SessionListPage> {
  List<Session> sessions = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    loadSessions();
  }

  Future<void> loadSessions() async {
    setState(() => isLoading = true);
    final data = await ApiService.fetchSessions();

    if (data != null) {
      final List<Session> loadedSessions = data.map<Session>((json) => Session.fromJson(json)).toList();
      setState(() {
        sessions = loadedSessions;
        isLoading = false;
      });
    } else {
      setState(() {
        sessions = [];
        isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed to load sessions')));
    }
  }

  Future<void> deleteSession(String id) async {
    final success = await ApiService.deleteSession(id);
    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Session deleted')));
      loadSessions();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed to delete session')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('🎧 Sessions')),
      body: isLoading
          ? Center(child: CircularProgressIndicator())
          : RefreshIndicator(
        onRefresh: loadSessions,
        child: ListView.builder(
          itemCount: sessions.length,
          itemBuilder: (context, index) {
            final session = sessions[index];
            return Dismissible(
              key: Key(session.id),
              background: Container(color: Colors.red),
              onDismissed: (_) => deleteSession(session.id),
              child: ListTile(
                title: Text('Session ${session.id}'),
                subtitle: Text(session.preview ?? 'No preview'),
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => SessionDetailsPage(session: session)),
                  );
                },
              ),
            );
          },
        ),
      ),
    );
  }
}
