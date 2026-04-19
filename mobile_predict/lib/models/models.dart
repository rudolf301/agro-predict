class Crop {
  final String id;
  final String nameEn;
  final String nameBs;
  Crop({required this.id, required this.nameEn, required this.nameBs});

  factory Crop.fromJson(Map<String, dynamic> j) => Crop(
        id: j['id'] as String,
        nameEn: j['name_en'] as String,
        nameBs: j['name_bs'] as String,
      );

  String get emoji => switch (id) {
        'corn' => '\u{1F33D}',
        'wheat' => '\u{1F33E}',
        'soybeans' => '\u{1FAD8}',
        'barley' => '\u{1F33E}',
        'rapeseed' => '\u{1F33C}',
        'potato' => '\u{1F954}',
        'tomato' => '\u{1F345}',
        'onion' => '\u{1F9C5}',
        'pepper' => '\u{1F336}',
        'sunflower' => '\u{1F33B}',
        _ => '\u{1F331}',
      };
}

class DailyForecast {
  final DateTime date;
  final double tempMin;
  final double tempMax;
  final double precipitation;
  final double frostProbability;
  final bool cropFrostRisk;

  DailyForecast({
    required this.date,
    required this.tempMin,
    required this.tempMax,
    required this.precipitation,
    required this.frostProbability,
    required this.cropFrostRisk,
  });

  factory DailyForecast.fromJson(Map<String, dynamic> j) => DailyForecast(
        date: DateTime.parse(j['date'] as String),
        tempMin: (j['temp_min_c'] as num).toDouble(),
        tempMax: (j['temp_max_c'] as num).toDouble(),
        precipitation: (j['precipitation_mm'] as num).toDouble(),
        frostProbability: (j['frost_probability'] as num).toDouble(),
        cropFrostRisk: j['crop_frost_risk'] as bool,
      );
}

class CropPrediction {
  final String cropId;
  final String cropNameEn;
  final String cropNameBs;
  final String frostTolerance;
  final int growingDays;

  final String? recommendedDate;
  final double recommendedConfidence;
  final double historicalFrostRate;
  final String? windowStart;
  final String? windowEnd;

  final String trafficLight;
  final String riskLabel;
  final double avgFrostProbability14d;
  final int cropFrostRiskDays14d;

  final List<DailyForecast> forecast14d;
  final double confidenceOverall;
  final double modelAuc;

  final List<String> explanation;
  final List<String>? gptExplanation;
  final String? gptModel;

  CropPrediction({
    required this.cropId,
    required this.cropNameEn,
    required this.cropNameBs,
    required this.frostTolerance,
    required this.growingDays,
    required this.recommendedDate,
    required this.recommendedConfidence,
    required this.historicalFrostRate,
    required this.windowStart,
    required this.windowEnd,
    required this.trafficLight,
    required this.riskLabel,
    required this.avgFrostProbability14d,
    required this.cropFrostRiskDays14d,
    required this.forecast14d,
    required this.confidenceOverall,
    required this.modelAuc,
    required this.explanation,
    this.gptExplanation,
    this.gptModel,
  });

  factory CropPrediction.fromJson(Map<String, dynamic> j) {
    final crop = j['crop'] as Map<String, dynamic>;
    final rec = j['recommended_planting'] as Map<String, dynamic>;
    final risk = j['risk'] as Map<String, dynamic>;
    final conf = j['confidence'] as Map<String, dynamic>;
    return CropPrediction(
      cropId: crop['id'] as String,
      cropNameEn: crop['name_en'] as String,
      cropNameBs: crop['name_bs'] as String,
      frostTolerance: crop['frost_tolerance'] as String,
      growingDays: crop['growing_days'] as int,
      recommendedDate: rec['date'] as String?,
      recommendedConfidence: ((rec['confidence'] as num?) ?? 0).toDouble(),
      historicalFrostRate:
          ((rec['historical_frost_rate'] as num?) ?? 0).toDouble(),
      windowStart: rec['window_start'] as String?,
      windowEnd: rec['window_end'] as String?,
      trafficLight: risk['traffic_light'] as String,
      riskLabel: risk['label'] as String,
      avgFrostProbability14d:
          (risk['avg_frost_probability_14d'] as num).toDouble(),
      cropFrostRiskDays14d: risk['crop_frost_risk_days_14d'] as int,
      forecast14d: (j['forecast_14d'] as List)
          .map((e) => DailyForecast.fromJson(e as Map<String, dynamic>))
          .toList(),
      confidenceOverall: (conf['overall'] as num).toDouble(),
      modelAuc: (conf['model_auc'] as num).toDouble(),
      explanation:
          (j['explanation'] as List).map((e) => e.toString()).toList(),
      gptExplanation: (j['gpt_explanation'] as List?)
          ?.map((e) => e.toString())
          .toList(),
      gptModel: j['gpt_model'] as String?,
    );
  }
}

class PredictionResponse {
  final double latitude;
  final double longitude;
  final double elevationM;
  final List<CropPrediction> predictions;
  final bool gptEnabled;

  PredictionResponse({
    required this.latitude,
    required this.longitude,
    required this.elevationM,
    required this.predictions,
    this.gptEnabled = false,
  });

  factory PredictionResponse.fromJson(Map<String, dynamic> j) {
    final loc = j['location'] as Map<String, dynamic>;
    return PredictionResponse(
      latitude: (loc['latitude'] as num).toDouble(),
      longitude: (loc['longitude'] as num).toDouble(),
      elevationM: (loc['elevation_m'] as num).toDouble(),
      predictions: (j['predictions'] as List)
          .map((e) => CropPrediction.fromJson(e as Map<String, dynamic>))
          .toList(),
      gptEnabled: j['gpt_enabled'] as bool? ?? false,
    );
  }
}
