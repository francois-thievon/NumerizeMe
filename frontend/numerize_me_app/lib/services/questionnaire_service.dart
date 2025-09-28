import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/api_config.dart';
import '../models/questionnaire.dart';

class QuestionnaireService {
  final String baseUrl = ApiConfig.baseUrl;

  // Méthode de test sans authentification
  Future<List<Questionnaire>> getQuestionnairesTest() async {
    final url = '$baseUrl/questionnaires/questionnaires-test';
    print('Calling TEST API: $url'); // Debug log
    
    final response = await http.get(
      Uri.parse(url),
      headers: {
        'Content-Type': 'application/json',
      },
    );

    print('Response status: ${response.statusCode}'); // Debug log
    print('Response body: ${response.body}'); // Debug log

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => Questionnaire.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load questionnaires: ${response.statusCode}');
    }
  }

  Future<List<Questionnaire>> getQuestionnaires(String token) async {
    final url = '$baseUrl/questionnaires/questionnaires';
    print('Calling API: $url'); // Debug log
    
    final response = await http.get(
      Uri.parse(url),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    print('Response status: ${response.statusCode}'); // Debug log
    print('Response body: ${response.body}'); // Debug log

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => Questionnaire.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load questionnaires: ${response.statusCode}');
    }
  }

  Future<List<Map<String, dynamic>>> getUserResponses(String token) async {
    final url = '$baseUrl/questionnaires/responses/me';
    print('Calling API: $url'); // Debug log
    
    final response = await http.get(
      Uri.parse(url),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    print('getUserResponses - Response status: ${response.statusCode}'); // Debug log
    print('getUserResponses - Response body: ${response.body}'); // Debug log

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.cast<Map<String, dynamic>>();
    } else {
      throw Exception('Failed to load user responses');
    }
  }

  Future<Map<String, dynamic>> submitResponse(
    String token,
    int questionnaireId,
    List<BinaryAnswer> answers,
  ) async {
    final response = await http.post(
      Uri.parse('$baseUrl/questionnaires/responses'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        'questionnaire_id': questionnaireId,
        'answers': answers.map((a) => a.toJson()).toList(),
      }),
    );

    if (response.statusCode == 200 || response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to submit response: ${response.statusCode}');
    }
  }
}
