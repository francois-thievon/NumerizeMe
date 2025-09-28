import 'package:flutter/material.dart';
import '../models/questionnaire.dart';
import '../services/questionnaire_service.dart';

class QuestionnaireProvider with ChangeNotifier {
  final QuestionnaireService _questionnaireService = QuestionnaireService();
  List<Questionnaire> _questionnaires = [];
  Questionnaire? _currentQuestionnaire;
  bool _isLoading = false;
  String? _error;

  List<Questionnaire> get questionnaires => _questionnaires;
  Questionnaire? get currentQuestionnaire => _currentQuestionnaire;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> fetchQuestionnaires(String token) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      // Récupérer les questionnaires
      List<Questionnaire> questionnaires = await _questionnaireService.getQuestionnaires(token);
      
      // Récupérer les réponses de l'utilisateur
      List<Map<String, dynamic>> userResponses = await _questionnaireService.getUserResponses(token);
      
      // Créer un set des IDs de questionnaires déjà complétés
      Set<int> completedQuestionnaireIds = userResponses
          .map((response) => response['questionnaire_id'] as int)
          .toSet();
      
      // Mettre à jour le statut de completion pour chaque questionnaire
      _questionnaires = questionnaires.map((questionnaire) {
        bool isCompleted = completedQuestionnaireIds.contains(questionnaire.id);
        return Questionnaire(
          id: questionnaire.id,
          title: questionnaire.title,
          description: questionnaire.description,
          category: questionnaire.category,
          weight: questionnaire.weight,
          questions: questionnaire.questions,
          createdAt: questionnaire.createdAt,
          updatedAt: questionnaire.updatedAt,
          isCompleted: isCompleted,
        );
      }).toList();
      
      _error = null;
    } catch (e) {
      _error = e.toString();
      _questionnaires = [];
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> submitQuestionnaire(String token, int questionnaireId, List<BinaryAnswer> answers) async {
    try {
      await _questionnaireService.submitResponse(token, questionnaireId, answers);
      notifyListeners();
    } catch (e) {
      rethrow;
    }
  }

  void setCurrentQuestionnaire(Questionnaire questionnaire) {
    _currentQuestionnaire = questionnaire;
    notifyListeners();
  }

  void clearCurrentQuestionnaire() {
    _currentQuestionnaire = null;
    notifyListeners();
  }
}
