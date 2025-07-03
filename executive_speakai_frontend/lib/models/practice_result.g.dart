// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'practice_result.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class PracticeResultAdapter extends TypeAdapter<PracticeResult> {
  @override
  final int typeId = 0;

  @override
  PracticeResult read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return PracticeResult(
      prompt: fields[0] as String,
      transcript: fields[1] as String,
      feedback: fields[2] as String,
      timestamp: fields[3] as DateTime,
    );
  }

  @override
  void write(BinaryWriter writer, PracticeResult obj) {
    writer
      ..writeByte(4)
      ..writeByte(0)
      ..write(obj.prompt)
      ..writeByte(1)
      ..write(obj.transcript)
      ..writeByte(2)
      ..write(obj.feedback)
      ..writeByte(3)
      ..write(obj.timestamp);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is PracticeResultAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}
