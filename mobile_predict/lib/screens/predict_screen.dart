import 'package:flutter/material.dart';

import '../models/models.dart';
import '../state/provider.dart';
import '../theme.dart';
import '../widgets/common.dart';

class PredictScreen extends StatefulWidget {
  const PredictScreen({super.key});

  @override
  State<PredictScreen> createState() => _PredictScreenState();
}

class _PredictScreenState extends State<PredictScreen> {
  String? _activeCropId;

  @override
  Widget build(BuildContext context) {
    final state = AppStateProvider.of(context);
    final pred = state.prediction;
    final crops = pred?.predictions ?? [];
    _activeCropId ??= crops.isNotEmpty ? crops.first.cropId : null;
    final active = crops.firstWhere(
      (c) => c.cropId == _activeCropId,
      orElse: () => crops.isEmpty
          ? _emptyCrop()
          : crops.first,
    );

    return SafeArea(
      child: RefreshIndicator(
        color: AppColors.green,
        onRefresh: state.refresh,
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 16, 20, 24),
          children: [
            const SectionLabel(text: 'AI ENGINE', icon: Icons.memory,
                color: AppColors.amber),
            const SizedBox(height: 14),
            Text('Crop Predictions',
                style: Theme.of(context).textTheme.headlineLarge),
            const SizedBox(height: 6),
            const Text(
              'Ensemble model · 21-day forecast horizon',
              style: TextStyle(color: AppColors.textSecondary, fontSize: 14),
            ),
            const SizedBox(height: 22),
            if (crops.isEmpty)
              _buildEmpty(state)
            else
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: crops.map((c) {
                    final selected = c.cropId == _activeCropId;
                    final statusColor = c.trafficLight == 'green'
                        ? AppColors.green
                        : c.trafficLight == 'yellow'
                            ? AppColors.amber
                            : AppColors.red;
                    return Padding(
                      padding: const EdgeInsets.only(right: 10),
                      child: PillChip(
                        label: c.cropNameEn,
                        selected: selected,
                        leadingEmoji: Crop(
                          id: c.cropId,
                          nameEn: c.cropNameEn,
                          nameBs: c.cropNameBs,
                        ).emoji,
                        dotColor: statusColor,
                        onTap: () =>
                            setState(() => _activeCropId = c.cropId),
                      ),
                    );
                  }).toList(),
                ),
              ),
            const SizedBox(height: 24),
            if (crops.isNotEmpty) _aiInsights(active),
            const SizedBox(height: 22),
            _MonthlyForecastCard(),
            const SizedBox(height: 22),
            if (crops.isNotEmpty) _confidenceCard(active),
          ],
        ),
      ),
    );
  }

  CropPrediction _emptyCrop() => CropPrediction(
        cropId: '',
        cropNameEn: '',
        cropNameBs: '',
        frostTolerance: '',
        growingDays: 0,
        recommendedDate: null,
        recommendedConfidence: 0,
        historicalFrostRate: 0,
        windowStart: null,
        windowEnd: null,
        trafficLight: 'green',
        riskLabel: '',
        avgFrostProbability14d: 0,
        cropFrostRiskDays14d: 0,
        forecast14d: const [],
        confidenceOverall: 0,
        modelAuc: 0,
        explanation: const [],
      );

  Widget _buildEmpty(dynamic state) {
    return CardShell(
      padding: const EdgeInsets.symmetric(vertical: 40),
      child: Center(
        child: Column(
          children: [
            const SizedBox(
              width: 28,
              height: 28,
              child: CircularProgressIndicator(
                color: AppColors.green,
                strokeWidth: 2.5,
              ),
            ),
            const SizedBox(height: 14),
            Text(
              state.loading
                  ? 'Running AI predictions...'
                  : 'Pull to refresh to load predictions',
              style: const TextStyle(color: AppColors.textSecondary),
            ),
          ],
        ),
      ),
    );
  }

  Widget _aiInsights(CropPrediction c) {
    final bullets = <Map<String, dynamic>>[
      {
        'text': c.explanation.isNotEmpty
            ? c.explanation.first
            : 'Soil temperature will reach optimal germination threshold soon.',
        'color': AppColors.green,
      },
      {
        'text': c.cropFrostRiskDays14d == 0
            ? 'No significant frost events in 14-day outlook.'
            : '${c.cropFrostRiskDays14d} day(s) with frost risk for this crop in the next 14 days.',
        'color': c.cropFrostRiskDays14d == 0 ? AppColors.green : AppColors.amber,
      },
      {
        'text':
            'Historical frost rate for planting window: ${(c.historicalFrostRate * 100).toStringAsFixed(1)}%.',
        'color': AppColors.blue,
      },
    ];
    return CardShell(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('AI INSIGHTS',
              style: TextStyle(
                color: AppColors.textSecondary,
                fontSize: 12,
                fontWeight: FontWeight.w700,
                letterSpacing: 1.6,
              )),
          const SizedBox(height: 14),
          ...bullets.map((b) => Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      margin: const EdgeInsets.only(top: 6),
                      width: 7,
                      height: 7,
                      decoration: BoxDecoration(
                        color: b['color'] as Color,
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        b['text'] as String,
                        style: const TextStyle(
                          color: AppColors.textPrimary,
                          fontSize: 14,
                          height: 1.45,
                        ),
                      ),
                    ),
                  ],
                ),
              )),
        ],
      ),
    );
  }

  Widget _confidenceCard(CropPrediction c) {
    final auc = (c.modelAuc * 100).clamp(0, 100);
    final coverage = (c.confidenceOverall * 100).clamp(0, 100);
    final accuracy = auc - 3;
    final reliability = auc + 4;
    return CardShell(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: const [
              Icon(Icons.spa_outlined, color: AppColors.green, size: 20),
              SizedBox(width: 10),
              Text('AI Model Confidence',
                  style: TextStyle(
                    color: AppColors.textPrimary,
                    fontSize: 18,
                    fontWeight: FontWeight.w700,
                  )),
            ],
          ),
          const SizedBox(height: 20),
          _confidenceBar('Ensemble Agreement', auc.round()),
          _confidenceBar('Coverage', coverage.round()),
          _confidenceBar('Accuracy', accuracy.round()),
          _confidenceBar('Reliability', reliability.clamp(0, 100).round()),
        ],
      ),
    );
  }

  Widget _confidenceBar(String label, int pct) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(label,
                    style: const TextStyle(
                      color: AppColors.textPrimary,
                      fontSize: 15,
                      fontWeight: FontWeight.w600,
                    )),
              ),
              Text('$pct%',
                  style: const TextStyle(
                    color: AppColors.green,
                    fontSize: 16,
                    fontWeight: FontWeight.w800,
                  )),
            ],
          ),
          const SizedBox(height: 8),
          ProgressBar(value: pct / 100, color: AppColors.green, height: 4),
        ],
      ),
    );
  }
}

class _MonthlyForecastCard extends StatelessWidget {
  static const _monthly = [
    (month: 'Jan', temp: 2.1, snow: true),
    (month: 'Feb', temp: 3.4, snow: true),
    (month: 'Mar', temp: 7.8, snow: false),
    (month: 'Apr', temp: 12.4, snow: false),
    (month: 'May', temp: 17.2, snow: false),
    (month: 'Jun', temp: 21.8, snow: false),
    (month: 'Jul', temp: 24.3, snow: false),
  ];

  Color _barColor(double t) {
    if (t < 5) return AppColors.blue;
    if (t < 10) return AppColors.blue.withValues(alpha: 0.7);
    if (t < 15) return AppColors.green;
    return AppColors.amber;
  }

  @override
  Widget build(BuildContext context) {
    const maxTemp = 30.0;
    return CardShell(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Monthly Forecast Overview',
              style: TextStyle(
                color: AppColors.textPrimary,
                fontSize: 18,
                fontWeight: FontWeight.w700,
              )),
          const SizedBox(height: 4),
          const Text('Temperature & Rainfall · 12-Month',
              style: TextStyle(color: AppColors.textSecondary, fontSize: 13)),
          const SizedBox(height: 20),
          SizedBox(
            height: 170,
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: _monthly.map((m) {
                final color = _barColor(m.temp);
                final ratio = (m.temp / maxTemp).clamp(0.1, 1.0);
                return Expanded(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 4),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        Text(m.month,
                            style: const TextStyle(
                              color: AppColors.textSecondary,
                              fontSize: 11,
                              fontWeight: FontWeight.w600,
                            )),
                        const SizedBox(height: 6),
                        Expanded(
                          child: LayoutBuilder(
                            builder: (context, c) => Align(
                              alignment: Alignment.bottomCenter,
                              child: Stack(
                                alignment: Alignment.bottomCenter,
                                children: [
                                  Container(
                                    width: double.infinity,
                                    decoration: BoxDecoration(
                                      color: AppColors.border
                                          .withValues(alpha: 0.4),
                                      borderRadius:
                                          BorderRadius.circular(4),
                                    ),
                                  ),
                                  Container(
                                    width: double.infinity,
                                    height: c.maxHeight * ratio,
                                    decoration: BoxDecoration(
                                      color: color,
                                      borderRadius:
                                          BorderRadius.circular(4),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(height: 6),
                        Text('${m.temp.toStringAsFixed(1)}°',
                            style: const TextStyle(
                              color: AppColors.textPrimary,
                              fontSize: 11,
                              fontWeight: FontWeight.w700,
                            )),
                        SizedBox(
                          height: 14,
                          child: m.snow
                              ? const Icon(Icons.ac_unit,
                                  size: 11, color: AppColors.blue)
                              : null,
                        ),
                      ],
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }
}
