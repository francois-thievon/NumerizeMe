import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/app_theme.dart';
import '../providers/questionnaire_provider.dart';
import '../providers/auth_provider.dart';
import 'questionnaire_screen.dart';

class QuestionnairesListScreen extends StatefulWidget {
  const QuestionnairesListScreen({super.key});

  @override
  State<QuestionnairesListScreen> createState() => _QuestionnairesListScreenState();
}

class _QuestionnairesListScreenState extends State<QuestionnairesListScreen> {

  @override
  void initState() {
    super.initState();
    // Forcer le rechargement des questionnaires à chaque ouverture de la page
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadQuestionnaires(context);
    });
  }

  Future<void> _loadQuestionnaires(BuildContext context) async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final questionnaireProvider = Provider.of<QuestionnaireProvider>(context, listen: false);
    
    final token = authProvider.token;
    if (token != null) {
      await questionnaireProvider.fetchQuestionnaires(token);
    }
  }

  Future<void> _refreshQuestionnaires() async {
    await _loadQuestionnaires(context);
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Consumer<QuestionnaireProvider>(
        builder: (context, questionnaireProvider, child) {
          if (questionnaireProvider.isLoading) {
            return const Center(
              child: CircularProgressIndicator(
                valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
              ),
            );
          }

              if (questionnaireProvider.error != null) {
                return Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(
                        Icons.error_outline,
                        size: 64,
                        color: Colors.white,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'Erreur: ${questionnaireProvider.error}',
                        style: const TextStyle(
                          fontSize: 16,
                          color: Colors.white,
                        ),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: () => _loadQuestionnaires(context),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.white.withOpacity(0.2),
                          foregroundColor: Colors.white,
                        ),
                        child: const Text('Réessayer'),
                      ),
                    ],
                  ),
                );
              }

              final questionnaires = questionnaireProvider.questionnaires;

              if (questionnaires.isEmpty) {
                return const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.quiz_outlined,
                        size: 64,
                        color: Colors.white,
                      ),
                      SizedBox(height: 16),
                      Text(
                        'Aucun questionnaire disponible',
                        style: TextStyle(
                          fontSize: 18, 
                          color: Colors.white,
                        ),
                      ),
                    ],
                  ),
                );
              }

              return Column(
                children: [
                  // Header avec titre
                  Padding(
                    padding: const EdgeInsets.all(20),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        // Espacement pour centrer le titre
                        const SizedBox(width: 52), // Taille du bouton + padding
                        
                        // Titre
                        const Text(
                          'Questionnaires',
                          style: TextStyle(
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
                        ),
                        
                        // Bouton refresh à droite
                        IconButton(
                          onPressed: _refreshQuestionnaires,
                          icon: const Icon(
                            Icons.refresh,
                            color: Colors.white,
                            size: 28,
                          ),
                          style: IconButton.styleFrom(
                            backgroundColor: Colors.white.withOpacity(0.2),
                            padding: const EdgeInsets.all(12),
                          ),
                        ),
                      ],
                    ),
                  ),

                  // Contenu principal
                  Expanded(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 20.0),
                      child: Column(
                        children: [
                          const SizedBox(height: 20),
                          
                          Expanded(
                            child: ListView.builder(
                              itemCount: questionnaires.length,
                              itemBuilder: (context, index) {
                                final questionnaire = questionnaires[index];
                                return Padding(
                                  padding: const EdgeInsets.only(bottom: 20),
                                  child: AnimatedCard(
                                    child: InkWell(
                                      onTap: () {
                                        Navigator.push(
                                          context,
                                          MaterialPageRoute(
                                            builder: (context) => QuestionnaireScreen(
                                              questionnaire: questionnaire,
                                            ),
                                          ),
                                        );
                                      },
                                      borderRadius: BorderRadius.circular(16),
                                      child: Container(
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
                                        child: Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Row(
                                              children: [
                                                Container(
                                                  padding: const EdgeInsets.all(12),
                                                  decoration: BoxDecoration(
                                                    color: const Color(0xFF667eea).withOpacity(0.1),
                                                    borderRadius: BorderRadius.circular(12),
                                                  ),
                                                  child: Icon(
                                                    _getQuestionnaireIcon(questionnaire.title),
                                                    color: const Color(0xFF667eea),
                                                    size: 30,
                                                  ),
                                                ),
                                                const SizedBox(width: 16),
                                                Expanded(
                                                  child: Text(
                                                    questionnaire.title,
                                                    style: const TextStyle(
                                                      fontSize: 26,
                                                      fontWeight: FontWeight.bold,
                                                      color: Colors.black87,
                                                    ),
                                                  ),
                                                ),
                                              ],
                                            ),
                                            const SizedBox(height: 16),
                                            Row(
                                              children: [
                                                _buildInfoChip(
                                                  Icons.help_outline,
                                                  '${questionnaire.questions.length} questions',
                                                ),
                                                const Spacer(),
                                                _buildStatusBadge(questionnaire.isCompleted),
                                              ],
                                            ),
                                            const SizedBox(height: 16),
                                            Padding(
                                              padding: const EdgeInsets.only(top: 16),
                                              child: Container(
                                                width: double.infinity,
                                                margin: const EdgeInsets.symmetric(horizontal: 8),
                                                padding: const EdgeInsets.symmetric(
                                                  vertical: 12,
                                                ),
                                                decoration: BoxDecoration(
                                                  color: const Color(0xFF667eea),
                                                  borderRadius: BorderRadius.circular(20),
                                                ),
                                                child: const Text(
                                                  'Commencer',
                                                  style: TextStyle(
                                                    color: Colors.white,
                                                    fontSize: 16,
                                                    fontWeight: FontWeight.w600,
                                                  ),
                                                  textAlign: TextAlign.center,
                                                ),
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),
                                    ),
                                  ),
                                );
                              },
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              );
            },
          ),
        );
  }

  Widget _buildInfoChip(IconData icon, String label) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.grey.shade100,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 20, color: Colors.grey.shade600),
          const SizedBox(width: 6),
          Text(
            label,
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey.shade600,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusBadge(bool isCompleted) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: isCompleted ? Colors.green : Colors.orange,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            isCompleted ? Icons.check : Icons.schedule,
            size: 18,
            color: Colors.white,
          ),
          const SizedBox(width: 6),
          Text(
            isCompleted ? 'Effectué' : 'En attente',
            style: const TextStyle(
              fontSize: 15,
              color: Colors.white,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  IconData _getQuestionnaireIcon(String title) {
    switch (title.toLowerCase()) {
      case 'animaux':
        return Icons.pets;
      case 'nourriture':
        return Icons.restaurant;
      case 'sport':
        return Icons.sports_soccer;
      case 'musique':
        return Icons.music_note;
      case 'voyage':
        return Icons.flight;
      case 'cinéma':
      case 'cinema':
        return Icons.movie;
      case 'lecture':
        return Icons.book;
      case 'technologie':
        return Icons.computer;
      default:
        return Icons.quiz; // Icône par défaut
    }
  }
}
