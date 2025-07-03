import 'package:flutter/material.dart';
import 'package:hive_flutter/hive_flutter.dart';
import '../models/practice_result.dart';
import 'prompt_practice_page.dart';

class SessionListPage extends StatelessWidget {
  const SessionListPage({super.key});

  void _showResultDialog(BuildContext context, PracticeResult result) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: Text("🗂 Session Detail"),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text("📝 Prompt", style: TextStyle(fontWeight: FontWeight.bold)),
              SizedBox(height: 4),
              Text(result.prompt),
              SizedBox(height: 12),
              Text("🗣 Transcript", style: TextStyle(fontWeight: FontWeight.bold)),
              SizedBox(height: 4),
              Text(result.transcript),
              SizedBox(height: 12),
              Text("💡 Feedback", style: TextStyle(fontWeight: FontWeight.bold)),
              SizedBox(height: 4),
              Text(result.feedback),
            ],
          ),
        ),
        actions: [
          TextButton(
            child: Text("Close"),
            onPressed: () => Navigator.of(context).pop(),
          )
        ],
      ),
    );
  }

  void _confirmDelete(BuildContext context, Box<PracticeResult> box, PracticeResult result) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: Text("Delete Session"),
        content: Text("Are you sure you want to delete this session?"),
        actions: [
          TextButton(
            child: Text("Cancel"),
            onPressed: () => Navigator.of(context).pop(),
          ),
          TextButton(
            child: Text("Delete", style: TextStyle(color: Colors.red)),
            onPressed: () async {
              await result.delete();
              Navigator.of(context).pop();
              (context as Element).markNeedsBuild(); // Force UI refresh
            },
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final box = Hive.box<PracticeResult>('historyBox');
    final results = box.values.toList().reversed.toList();

    return Scaffold(
      appBar: AppBar(
        title: Text("📚 Session History"),
      ),
      body: results.isEmpty
          ? Center(child: Text("No sessions yet."))
          : ListView.builder(
        itemCount: results.length,
        itemBuilder: (context, index) {
          final result = results[index];
          return ListTile(
            title: Text(
              result.prompt,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            subtitle: Text(
              result.timestamp.toLocal().toString(),
              style: TextStyle(fontSize: 12),
            ),
            trailing: IconButton(
              icon: Icon(Icons.delete, color: Colors.redAccent),
              onPressed: () => _confirmDelete(context, box, result),
            ),
            onTap: () => _showResultDialog(context, result),
          );
        },
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => PromptPracticePage(
                prompt: "Tell me about your leadership experience.",
              ),
            ),
          );
        },
        icon: Icon(Icons.mic),
        label: Text("New Practice"),
      ),
    );
  }
}
