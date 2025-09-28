import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/match.dart';

class MatchService {
  static const String baseUrl = 'http://10.0.2.2:8000/api';

  // Récupérer tous les matchs de l'utilisateur
  static Future<List<Match>> getUserMatches(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/matches/list-matches'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((json) => Match.fromJson(json)).toList();
    } else {
      throw Exception('Erreur lors de la récupération des matchs: ${response.statusCode}');
    }
  }

  // Calculer de nouveaux matchs pour l'utilisateur
  static Future<Map<String, dynamic>> calculateMatches(String token) async {
    final url = '$baseUrl/matches/calculate-matches';
    print('DEBUG: Calling URL: $url');
    print('DEBUG: Token: ${token.substring(0, 20)}...');
    
    final response = await http.post(
      Uri.parse(url),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    print('DEBUG: Response status: ${response.statusCode}');
    print('DEBUG: Response body: ${response.body}');

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else if (response.statusCode == 401) {
      throw Exception('Token d\'authentification invalide ou expiré');
    } else {
      throw Exception('Erreur lors du calcul des matchs: ${response.statusCode} - ${response.body}');
    }
  }

  // Récupérer les statistiques de matching
  static Future<MatchingStats> getMatchingStats(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/matches/stats'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      return MatchingStats.fromJson(json.decode(response.body));
    } else {
      throw Exception('Erreur lors de la récupération des statistiques: ${response.statusCode}');
    }
  }

  // Récupérer la conversation d'un match
  static Future<List<Message>> getConversation(String token, int matchId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/matches/conversation/$matchId'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((json) => Message.fromJson(json)).toList();
    } else if (response.statusCode == 403) {
      throw Exception('Accès refusé à cette conversation');
    } else {
      throw Exception('Erreur lors de la récupération de la conversation: ${response.statusCode}');
    }
  }

  // Envoyer un message
  static Future<Message> sendMessage(String token, int matchId, String content) async {
    final messageData = MessageCreate(content: content);
    
    final response = await http.post(
      Uri.parse('$baseUrl/matches/conversation/$matchId/message'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: json.encode(messageData.toJson()),
    );

    if (response.statusCode == 200) {
      return Message.fromJson(json.decode(response.body));
    } else if (response.statusCode == 403) {
      throw Exception('Accès refusé à cette conversation');
    } else {
      throw Exception('Erreur lors de l\'envoi du message: ${response.statusCode}');
    }
  }

  // Marquer une conversation comme lue
  static Future<void> markConversationAsRead(String token, int matchId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/matches/conversation/$matchId/mark-read'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode != 200) {
      throw Exception('Erreur lors du marquage comme lu: ${response.statusCode}');
    }
  }
}
