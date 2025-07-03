import 'package:hive/hive.dart';

part 'practice_result.g.dart';

@HiveType(typeId: 0)
class PracticeResult extends HiveObject {
  @HiveField(0)
  String prompt;

  @HiveField(1)
  String transcript;

  @HiveField(2)
  String feedback;

  @HiveField(3)
  DateTime timestamp;

  PracticeResult({
    required this.prompt,
    required this.transcript,
    required this.feedback,
    required this.timestamp,
  });
}
