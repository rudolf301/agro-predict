import 'package:flutter/foundation.dart';

import '../models/models.dart';
import '../services/api_service.dart';

class FarmConfig {
  final double lat;
  final double lon;
  final String locationLabel;
  final List<String> selectedCropIds;
  final String farmSize;

  FarmConfig({
    required this.lat,
    required this.lon,
    required this.locationLabel,
    required this.selectedCropIds,
    required this.farmSize,
  });
}

class AppState extends ChangeNotifier {
  ApiService api;
  AppState(this.api);

  FarmConfig? farm;
  PredictionResponse? prediction;
  bool loading = false;
  String? error;

  void setFarm(FarmConfig cfg) {
    farm = cfg;
    notifyListeners();
  }

  Future<void> refresh() async {
    if (farm == null) return;
    loading = true;
    error = null;
    notifyListeners();
    try {
      prediction = await api.predict(
        lat: farm!.lat,
        lon: farm!.lon,
        cropIds: farm!.selectedCropIds,
        lang: 'bs',
      );
    } catch (e) {
      error = e.toString();
    } finally {
      loading = false;
      notifyListeners();
    }
  }
}
