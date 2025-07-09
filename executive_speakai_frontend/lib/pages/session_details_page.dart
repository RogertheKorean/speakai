import 'package:flutter/material.dart';
import '../models/session.dart';
import 'package:intl/intl.dart';

class SessionDetailsPage extends StatelessWidget {
  final Session session;
  const SessionDetailsPage({required this.session, Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final formattedDate = DateFormat.yMMMd().add_jm().format(session.createdAt);

    return Scaffold(
      appBar: AppBar(title: Text('Session Details')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: ListView(
          children: [
            Text('Session ID: ${session.id}', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
            SizedBox(height: 8),
            Text('Created at: $formattedDate'),
            SizedBox(height: 16),
            if (session.preview != null) ...[
              Text('Preview:', style: TextStyle(fontWeight: FontWeight.bold)),
              Text(session.preview!),
              SizedBox(height: 16),
            ],
            if (session.transcript != null) ...[
              Text('Transcript:', style: TextStyle(fontWeight: FontWeight.bold)),
              Text(session.transcript!),
              SizedBox(height: 16),
            ],
            if (session.feedback != null) ...[
              Text('Feedback:', style: TextStyle(fontWeight: FontWeight.bold)),
              Text(session.feedback!),
            ],
          ],
        ),
      ),
    );
  }
}
