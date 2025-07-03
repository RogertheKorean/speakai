import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'package:hive_flutter/hive_flutter.dart';
import '../models/practice_result.dart';

class PromptPracticePage extends StatefulWidget {
  final String prompt;

  const PromptPracticePage({super.key, required this.prompt});

  @override
  State<PromptPracticePage> createState() => _PromptPracticePageState();
}

class _PromptPracticePageState extends State<PromptPracticePage> {
  bool isRecording = false;
  bool isLoading = false;
  String transcript = "";
  String feedback = "";
  final AudioRecorder _recorder = AudioRecorder();

  Future<void> _toggleRecording() async {
    if (!await _recorder.hasPermission()) {
      _showErrorDialog("Microphone permission denied");
      return;
    }

    if (!isRecording) {
      final tempDir = await getTemporaryDirectory();
      final filePath = '${tempDir.path}/response.wav';

      await _recorder.start(
        RecordConfig(
          encoder: AudioEncoder.wav,
          sampleRate: 44100,
          bitRate: 128000,
        ),
        path: filePath,
      );

      setState(() {
        isRecording = true;
        transcript = "";
        feedback = "";
      });

    } else {
      final path = await _recorder.stop();
      setState(() {
        isRecording = false;
      });

      if (path != null && File(path).existsSync()) {
        setState(() {
          isLoading = true;
        });
        await _uploadRecording(File(path));
        setState(() {
          isLoading = false;
        });
      }
    }
  }

  Future<void> _uploadRecording(File file) async {
    final uri = Uri.parse("http://10.0.2.2:8000/upload");

    final request = http.MultipartRequest("POST", uri);
    request.files.add(await http.MultipartFile.fromPath(
      'file',
      file.path,
      contentType: MediaType('audio', 'wav'),
    ));

    try {
      final response = await request.send();
      final body = await http.Response.fromStream(response);

      if (body.statusCode == 200) {
        final data = json.decode(body.body);
        transcript = data["transcript"] ?? "No transcript.";
        feedback = data["feedback"] ?? "No feedback.";

        final box = Hive.box<PracticeResult>('historyBox');
        await box.add(PracticeResult(
          prompt: widget.prompt,
          transcript: transcript,
          feedback: feedback,
          timestamp: DateTime.now(),
        ));

        _showResultDialog();
      } else {
        _showErrorDialog("Upload failed: ${body.body}");
      }
    } catch (e) {
      _showErrorDialog("Upload error: $e");
    }
  }

  void _showResultDialog() {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: Text("✅ Result"),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text("🗣 Transcript:", style: TextStyle(fontWeight: FontWeight.bold)),
              SizedBox(height: 4),
              Text(transcript),
              SizedBox(height: 12),
              Text("💡 Feedback:", style: TextStyle(fontWeight: FontWeight.bold)),
              SizedBox(height: 4),
              Text(feedback),
            ],
          ),
        ),
        actions: [
          TextButton(
            child: Text("OK"),
            onPressed: () => Navigator.of(context).pop(),
          )
        ],
      ),
    );
  }

  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: Text("❌ Error"),
        content: Text(message),
        actions: [
          TextButton(
            child: Text("Close"),
            onPressed: () => Navigator.of(context).pop(),
          )
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Practice Prompt"),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: isLoading
            ? Center(child: CircularProgressIndicator())
            : Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text("📝 Prompt", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Text(widget.prompt, style: TextStyle(fontSize: 16, color: Colors.white70)),
            SizedBox(height: 24),
            Center(
              child: ElevatedButton.icon(
                icon: Icon(isRecording ? Icons.stop : Icons.mic),
                label: Text(isRecording ? "Stop Recording" : "Start Recording"),
                onPressed: isLoading ? null : _toggleRecording,
                style: ElevatedButton.styleFrom(
                  backgroundColor: isRecording ? Colors.red : Colors.green,
                  padding: EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
