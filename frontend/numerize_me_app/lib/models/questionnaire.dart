class BinaryQuestion {
  final int id;
  final String text;
  final String optionA;
  final String optionB;

  BinaryQuestion({
    required this.id,
    required this.text,
    required this.optionA,
    required this.optionB,
  });

  factory BinaryQuestion.fromJson(Map<String, dynamic> json) {
    return BinaryQuestion(
      id: json['id'],
      text: json['text'],
      optionA: json['option_a'],
      optionB: json['option_b'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'text': text,
      'option_a': optionA,
      'option_b': optionB,
    };
  }
}

class Questionnaire {
  final int id;
  final String title;
  final String description;
  final String category;
  final int weight;
  final List<BinaryQuestion> questions;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final bool isCompleted;

  Questionnaire({
    required this.id,
    required this.title,
    required this.description,
    required this.category,
    required this.weight,
    required this.questions,
    required this.createdAt,
    this.updatedAt,
    this.isCompleted = false,
  });

  factory Questionnaire.fromJson(Map<String, dynamic> json) {
    var questionsList = json['questions'] as List;
    List<BinaryQuestion> questions = questionsList
        .map((q) => BinaryQuestion.fromJson(q))
        .toList();

    return Questionnaire(
      id: json['id'],
      title: json['title'],
      description: json['description'],
      category: json['category'],
      weight: json['weight'],
      questions: questions,
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: json['updated_at'] != null 
          ? DateTime.parse(json['updated_at']) 
          : null,
      isCompleted: json['is_completed'] ?? false,
    );
  }
}

class BinaryAnswer {
  final int questionId;
  final String chosenOption;

  BinaryAnswer({
    required this.questionId,
    required this.chosenOption,
  });

  Map<String, dynamic> toJson() {
    return {
      'question_id': questionId,
      'chosen_option': chosenOption,
    };
  }
}
