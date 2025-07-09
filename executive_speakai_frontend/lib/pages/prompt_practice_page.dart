import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:intl/intl.dart';
import 'package:share_plus/share_plus.dart';
import 'package:hive/hive.dart';
import 'dart:convert';
import 'dart:io';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:printing/printing.dart';
import 'package:path_provider/path_provider.dart';

import '../screens/transcript_history_screen.dart';

class SessionListPage extends StatefulWidget {
  const SessionListPage({Key? key}) : super(key: key);

  @override
  _SessionListPageState createState() => _SessionListPageState();
}

class _SessionListPageState extends State<SessionListPage> {
  final FlutterSecureStorage secureStorage = const FlutterSecureStorage();
  List<dynamic> sessions = [];
  List<dynamic> filteredSessions = [];
  Set<int> selectedSessionIds = {}; // Used for multi-select
  Map<int, String> sessionTags = {}; // New: Tag or label per session
  bool isLoading = true;
  String? token;
  String searchQuery = '';

  @override
  void initState() {
    super.initState();
    loadTokenAndFetchSessions();
  }

  Future<void> loadTokenAndFetchSessions() async {
    var tagBox = await Hive.openBox('sessionTags');
    setState(() {
      sessionTags = Map<int, String>.from(tagBox.toMap().map((k, v) => MapEntry(int.parse(k), v.toString())));
    });
    token = await secureStorage.read(key: 'jwt_token');
    var cacheBox = await Hive.openBox('sessionCache');
    final cachedData = cacheBox.get('sessions');
    final cacheTimestamp = cacheBox.get('cacheTime');
    final now = DateTime.now();
    if (cacheTimestamp != null) {
      final lastUpdated = DateTime.tryParse(cacheTimestamp);
      if (lastUpdated == null || now.difference(lastUpdated).inMinutes > 10) {
        await fetchSessions();
        return;
      }
    }
    if (cachedData != null) {
      final List<dynamic> cachedList = json.decode(cachedData);
      setState(() {
        sessions = cachedList;
        filteredSessions = sessions;
      });
    }
    await fetchSessions();
  }

  Future<void> fetchSessions() async {
    if (token == null) {
      print('JWT token is missing');
      setState(() => isLoading = false);
      return;
    }

    final response = await http.get(
      Uri.parse('http://<YOUR_BACKEND_URL>/history'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      var cacheBox = await Hive.openBox('sessionCache');
      await cacheBox.put('sessions', json.encode(data));
      await cacheBox.put('cacheTime', DateTime.now().toIso8601String());
      setState(() {
        sessions = data.reversed.toList();
        filteredSessions = sessions;
        isLoading = false;
      });
    } else {
      print('Failed to load sessions');
      setState(() => isLoading = false);
    }
  }

  Future<void> deleteSession(int id) async {
    final response = await http.delete(
      Uri.parse('http://<YOUR_BACKEND_URL>/session/$id'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );
    if (response.statusCode == 200) {
      setState(() {
        sessions.removeWhere((s) => s['id'] == id);
        filteredSessions = sessions.where((s) => _matchesQuery(s)).toList();
        // Optional: add tag-based filtering here if needed
        selectedSessionIds.remove(id);
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Session deleted'),
          action: SnackBarAction(
            label: 'Undo',
            onPressed: () {
              fetchSessions();
            },
          ),
        ),
      );
    } else {
      print('Failed to delete session');
    }
  }

  void navigateToDetails(Map<String, dynamic> session) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => SessionDetailScreen(session: session),
      ),
    );
  }

  Future<void> _onRefresh() async {
    setState(() => isLoading = true);
    await fetchSessions();
  }

  String formatTimestamp(String raw) {
    try {
      final dt = DateTime.parse(raw).toLocal();
      return DateFormat('yyyy-MM-dd HH:mm').format(dt);
    } catch (_) {
      return raw;
    }
  }

  bool _matchesQuery(Map<String, dynamic> session) {
    final query = searchQuery.toLowerCase();
    return (session['transcript'] ?? '').toLowerCase().contains(query) ||
        (session['feedback'] ?? '').toLowerCase().contains(query);
  }

  void _onSearchChanged(String query) {
    setState(() {
      searchQuery = query;
      filteredSessions = sessions.where((s) => _matchesQuery(s)).toList();
    });
  }

  void _exportSelectedSessions() async {
    final selected = sessions.where((s) => selectedSessionIds.contains(s['id']));

    final pdf = pw.Document();

    for (var item in selected) {
      pdf.addPage(
        pw.Page(
          build: (pw.Context context) => pw.Column(
            crossAxisAlignment: pw.CrossAxisAlignment.start,
            children: [
              pw.Text('Session ${item['id']}', style: pw.TextStyle(fontSize: 20, fontWeight: pw.FontWeight.bold)),
              pw.SizedBox(height: 10),
              pw.Text('📝 Transcript:'),
              pw.Text(item['transcript'] ?? ''),
              pw.SizedBox(height: 10),
              pw.Text('💡 Feedback:'),
              pw.Text(item['feedback'] ?? ''),
              pw.SizedBox(height: 20),
              pw.Divider(),
            ],
          ),
        ),
      );
    }

    final output = await getTemporaryDirectory();
    final file = File("${output.path}/sessions.pdf");
    await file.writeAsBytes(await pdf.save());

    await Share.shareXFiles([XFile(file.path)], text: 'Exported Session PDFs');
  }\n📝 ${item['transcript']}\n💡 ${item['feedback']}\n---').join('\n\n');
Share.share(exportText);
}

@override
Widget build(BuildContext context) {
final uniqueTags = sessionTags.values.toSet().toList();
return Scaffold(
backgroundColor: Theme.of(context).brightness == Brightness.dark
? Colors.black
    : Colors.white,
appBar: AppBar(
title: Text('🧾 Session List'),
actions: [
if (selectedSessionIds.isNotEmpty)
IconButton(
icon: Icon(Icons.share),
onPressed: _exportSelectedSessions,
)
],
),
body: Column(
children: [
Padding(
padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
child: TextField(
decoration: InputDecoration(
labelText: 'Search Transcript or Feedback',
prefixIcon: Icon(Icons.search),
border: OutlineInputBorder(),
),
onChanged: _onSearchChanged,
),
),
Padding(
padding: const EdgeInsets.all(16.0),
child: ElevatedButton.icon(
onPressed: () {
Navigator.push(
context,
MaterialPageRoute(builder: (_) => TranscriptHistoryScreen()),
);
},
icon: Icon(Icons.history),
label: Text('View Transcript History'),
style: ElevatedButton.styleFrom(
minimumSize: Size(double.infinity, 48),
),
),
),
Padding(
padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 4.0),
child: DropdownButtonFormField<String>(
isExpanded: true,
decoration: InputDecoration(
labelText: 'Filter by Tag',
border: OutlineInputBorder(),
),
value: searchQuery.isNotEmpty ? searchQuery : null,
items: uniqueTags
    .map((tag) => DropdownMenuItem<String>(
value: tag,
child: Text(tag),
))
    .toList(),
onChanged: (value) {
if (value != null) {
_onSearchChanged(value);
}
},
),
),
Expanded(
child: isLoading
? Center(child: CircularProgressIndicator())
    : RefreshIndicator(
onRefresh: _onRefresh,
child: filteredSessions.isEmpty
? ListView(
children: [
SizedBox(height: 100),
Center(child: Text('No sessions found.')),
],
)
    : ListView.builder(
itemCount: filteredSessions.length,
itemBuilder: (context, index) {
final item = filteredSessions[index];
final rawDate = item['created_at'] ?? 'Unknown Date';
final createdAt = formatTimestamp(rawDate);
final transcript = item['transcript'] ?? '';
final preview = transcript.length > 60
? '${transcript.substring(0, 60)}...'
    : transcript;
final isSelected = selectedSessionIds.contains(item['id']);

return Dismissible(
key: ValueKey(item['id']),
direction: DismissDirection.endToStart,
onDismissed: (direction) => deleteSession(item['id']),
background: Container(
color: Colors.red,
alignment: Alignment.centerRight,
padding: EdgeInsets.symmetric(horizontal: 20),
child: Icon(Icons.delete, color: Colors.white),
),
child: ListTile(
title: Row(
mainAxisAlignment: MainAxisAlignment.spaceBetween,
children: [
Text('Session \${item['id']}'),
IconButton(
icon: Icon(Icons.edit, size: 20),
onPressed: () async {
final newTag = await showDialog<String>(
context: context,
builder: (context) {
String tempTag = sessionTags[item['id']] ?? '';
return AlertDialog(
title: Text('Set Tag for Session \${item['id']}'),
content: TextField(
autofocus: true,
onChanged: (val) => tempTag = val,
controller: TextEditingController(text: tempTag),
),
actions: [
TextButton(
onPressed: () => Navigator.pop(context),
child: Text('Cancel'),
),
TextButton(
onPressed: () => Navigator.pop(context, tempTag),
child: Text('Save'),
),
],
);
},
);
if (newTag != null) {
setState(() => sessionTags[item['id']] = newTag);
var tagBox = await Hive.openBox('sessionTags');
tagBox.put(item['id'].toString(), newTag);
}
},
)
],
),
subtitle: Text('\$preview
📅 \$createdAt
🏷️ \${sessionTags[item['id']] ?? 'No Tag'}'),
isThreeLine: true,
onTap: () => navigateToDetails(item),
trailing: IconButton(
icon: Icon(Icons.share),
onPressed: () {
final exportText =
'📝 Transcript:\n${item['transcript']}\n\n💡 Feedback:\n${item['feedback']}';
Share.share(exportText);
},
),
),
);
},
),
),
),
],
),
);
}
}

class SessionDetailScreen extends StatelessWidget {
final Map<String, dynamic> session;

const SessionDetailScreen({required this.session});

@override
Widget build(BuildContext context) {
return Scaffold(
appBar: AppBar(title: Text('Session ${session['id']}')),
body: Padding(
padding: const EdgeInsets.all(16.0),
child: ListView(
children: [
Text('📝 Transcript', style: TextStyle(fontWeight: FontWeight.bold)),
SizedBox(height: 8),
Text(session['transcript'] ?? 'N/A'),
SizedBox(height: 20),
Text('💡 Feedback', style: TextStyle(fontWeight: FontWeight.bold)),
SizedBox(height: 8),
Text(session['feedback'] ?? 'N/A'),
],
),
),
);
}
}
