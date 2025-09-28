import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../services/questionnaire_service.dart';
import '../models/questionnaire.dart';
import '../widgets/swipe_card.dart';
import '../core/app_theme.dart';

class QuestionnaireScreen extends StatefulWidget {
  final Questionnaire questionnaire;

  const QuestionnaireScreen({
    Key? key,
    required this.questionnaire,
  }) : super(key: key);

  @override
  _QuestionnaireScreenState createState() => _QuestionnaireScreenState();
}

class _QuestionnaireScreenState extends State<QuestionnaireScreen> {
  final QuestionnaireService _questionnaireService = QuestionnaireService();
  int currentQuestionIndex = 0;
  List<BinaryAnswer> answers = [];

  @override
  void initState() {
    super.initState();
    
    // Debug: afficher la structure des questions
    print('Questions received: ${widget.questionnaire.questions}');
    if (widget.questionnaire.questions.isNotEmpty) {
      print('First question structure: ${widget.questionnaire.questions[0]}');
    }
  }

  void _answerQuestion(String answer) async {
    // Ajouter la réponse binaire
    final currentQuestion = widget.questionnaire.questions[currentQuestionIndex];
    answers.add(BinaryAnswer(
      questionId: currentQuestion.id,
      chosenOption: answer,
    ));

    // Passer à la question suivante ou terminer
    if (currentQuestionIndex < widget.questionnaire.questions.length - 1) {
      setState(() {
        currentQuestionIndex++;
      });
    } else {
      // Terminer le questionnaire
      await _submitResponses();
    }
  }

  Future<void> _submitResponses() async {
    try {
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      final token = authProvider.token;

      if (token != null) {
        await _questionnaireService.submitResponse(
          token,
          widget.questionnaire.id,
          answers,
        );

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Questionnaire complété avec succès !'),
              backgroundColor: Colors.green,
            ),
          );
          Navigator.pop(context, true); // true indique que le questionnaire est complété
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Erreur lors de la soumission : $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (currentQuestionIndex >= widget.questionnaire.questions.length) {
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    final currentQuestion = widget.questionnaire.questions[currentQuestionIndex];

    return Scaffold(
      backgroundColor: Colors.transparent,
      body: AnimatedGradientBackground(
        colors: const [
          Color(0xFF4facfe),
          Color(0xFF00f2fe),
          Color(0xFF667eea),
          Color(0xFF764ba2),
        ],
        child: SafeArea(
          child: Column(
            children: [
              // Header avec titre et bouton retour
              Padding(
                padding: const EdgeInsets.all(20),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    // Bouton retour
                    IconButton(
                      onPressed: () => Navigator.of(context).pop(),
                      icon: const Icon(
                        Icons.arrow_back,
                        color: Colors.white,
                        size: 28,
                      ),
                      style: IconButton.styleFrom(
                        backgroundColor: Colors.white.withOpacity(0.2),
                        padding: const EdgeInsets.all(12),
                      ),
                    ),
                    
                    // Titre centré
                    Expanded(
                      child: Text(
                        'Questionnaire',
                        style: const TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                          shadows: [
                            Shadow(
                              color: Colors.black26,
                              offset: Offset(2, 2),
                              blurRadius: 4,
                            ),
                          ],
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ),
                    
                    // Espace équivalent au bouton retour pour centrer parfaitement le titre
                    const SizedBox(width: 52), // Largeur du bouton + padding
                  ],
                ),
              ),

              // Barre de progression dans un container stylisé
              Container(
                margin: const EdgeInsets.symmetric(horizontal: 20),
                padding: const EdgeInsets.all(16.0),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Column(
                  children: [
                    Text(
                      'Question ${currentQuestionIndex + 1} sur ${widget.questionnaire.questions.length}',
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: Colors.white,
                        shadows: [
                          Shadow(
                            color: Colors.black26,
                            offset: Offset(1, 1),
                            blurRadius: 3,
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),
                    LinearProgressIndicator(
                      value: (currentQuestionIndex + 1) / widget.questionnaire.questions.length,
                      backgroundColor: Colors.white.withOpacity(0.3),
                      valueColor: const AlwaysStoppedAnimation<Color>(Colors.white),
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ],
                ),
              ),
              
              // Question et réponses
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      // Question dans un container stylisé
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(24),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.95),
                          borderRadius: BorderRadius.circular(16),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.1),
                              blurRadius: 20,
                              offset: const Offset(0, 10),
                            ),
                          ],
                        ),
                        child: Text(
                          currentQuestion.text,
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            color: Colors.black87,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ),
                      const SizedBox(height: 30),
                      
                      // Cartes de réponse côte à côte
                      Expanded(
                        child: Row(
                          children: [
                            // Carte pour l'option A (gauche)
                            Expanded(
                              child: Container(
                                margin: const EdgeInsets.only(right: 8),
                                child: SwipeCard(
                                  option: currentQuestion.optionA,
                                  color: const Color(0xFF667eea),
                                  direction: 'left',
                                  onTap: () => _answerQuestion('A'),
                                ),
                              ),
                            ),
                            // Carte pour l'option B (droite)
                            Expanded(
                              child: Container(
                                margin: const EdgeInsets.only(left: 8),
                                child: SwipeCard(
                                  option: currentQuestion.optionB,
                                  color: const Color(0xFF4facfe),
                                  direction: 'right',
                                  onTap: () => _answerQuestion('B'),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
