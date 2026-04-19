import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/models.dart';

class ApiService {
  final String baseUrl;
  String? openAiKey;
  String gptModel;

  ApiService({
    this.baseUrl = 'http://192.168.1.7:8765',
    this.openAiKey,
    this.gptModel = 'gpt-4o-mini',
  });

  Future<List<Crop>> listCrops() async {
    final r = await http.get(Uri.parse('$baseUrl/crops'));
    if (r.statusCode != 200) {
      throw Exception('Failed to load crops: ${r.statusCode}');
    }
    final data = json.decode(r.body) as Map<String, dynamic>;
    return (data['crops'] as List)
        .map((e) => Crop.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<PredictionResponse> predict({
    required double lat,
    required double lon,
    required List<String> cropIds,
    String lang = 'bs',
  }) async {
    final params = <String, String>{
      'lat': lat.toString(),
      'lon': lon.toString(),
      'crop': cropIds.join(','),
      'lang': lang,
    };
    if (openAiKey != null && openAiKey!.isNotEmpty) {
      params['gpt_model'] = gptModel;
    }
    final uri = Uri.parse('$baseUrl/predict').replace(queryParameters: params);

    final headers = <String, String>{};
    if (openAiKey != null && openAiKey!.isNotEmpty) {
      headers['X-OpenAI-Key'] = openAiKey!;
    }

    final r = await http
        .get(uri, headers: headers)
        .timeout(const Duration(seconds: 90));
    if (r.statusCode != 200) {
      throw Exception('Predict failed (${r.statusCode}): ${r.body}');
    }
    return PredictionResponse.fromJson(
      json.decode(r.body) as Map<String, dynamic>,
    );
  }

  Future<Map<String, dynamic>> health() async {
    final r = await http.get(Uri.parse('$baseUrl/health'));
    return json.decode(r.body) as Map<String, dynamic>;
  }
}
