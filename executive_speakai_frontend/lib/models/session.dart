class Session {
  final String id;
  final String? preview;
  final String? transcript;
  final String? feedback;
  final DateTime createdAt;

  Session({
    required this.id,
    this.preview,
    this.transcript,
    this.feedback,
    required this.createdAt,
  });

  factory Session.fromJson(Map<String, dynamic> json) {
    return Session(
      id: json['id'].toString(),
      preview: json['preview'],
      transcript: json['transcript'],
      feedback: json['feedback'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}
