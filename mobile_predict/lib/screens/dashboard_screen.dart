import 'package:flutter/material.dart';

import '../models/models.dart';
import '../state/provider.dart';
import '../theme.dart';
import '../widgets/common.dart';
import 'settings_screen.dart';

const _weekdayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const _weekdayFull = [
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
  'Sunday'
];
const _monthNames = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];
const _monthNamesShort = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
];

String _formatShortWeekday(DateTime d) => _weekdayNames[d.weekday - 1];
String _formatFullWeekdayMonthDay(DateTime d) =>
    '${_weekdayFull[d.weekday - 1]}, ${_monthNames[d.month - 1]} ${d.day}';
String _formatMonthDay(DateTime d) => '${_monthNamesShort[d.month - 1]} ${d.day}';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final state = AppStateProvider.of(context);
    final farm = state.farm;
    final pred = state.prediction;
    final primary = pred?.predictions.isNotEmpty == true
        ? pred!.predictions.first
        : null;

    return SafeArea(
      child: RefreshIndicator(
        color: AppColors.green,
        onRefresh: state.refresh,
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 12, 20, 24),
          children: [
            _header(context, farm?.locationLabel ?? 'Upper Bavaria · Zone 7b'),
            const SizedBox(height: 18),
            const SectionLabel(text: 'AGRO-PREDICT AI', icon: Icons.eco),
            const SizedBox(height: 10),
            Text(
              'Good Morning, Klaus',
              style: Theme.of(context).textTheme.headlineLarge,
            ),
            const SizedBox(height: 6),
            Text(
              _seasonSubtitle(),
              style: Theme.of(context)
                  .textTheme
                  .bodyLarge
                  ?.copyWith(color: AppColors.textSecondary),
            ),
            const SizedBox(height: 24),
            if (state.loading && pred == null)
              _LiveWeatherLoading()
            else if (primary != null)
              _LiveWeatherCard(prediction: primary)
            else
              _LiveWeatherLoading(),
            const SizedBox(height: 18),
            if (primary != null) _AlertChipsRow(prediction: primary),
            const SizedBox(height: 20),
            const _ClimateResilienceCard(),
            const SizedBox(height: 28),
            Row(
              children: [
                Text('Field Statistics',
                    style: Theme.of(context).textTheme.titleLarge),
                const Spacer(),
                Icon(Icons.wb_cloudy_outlined,
                    color: AppColors.textSecondary.withValues(alpha: 0.5),
                    size: 18),
              ],
            ),
            const SizedBox(height: 14),
            if (primary != null) _fieldStats(primary) else _fieldStatsEmpty(),
            const SizedBox(height: 28),
            Row(
              children: [
                Text('Top AI Recommendation',
                    style: Theme.of(context).textTheme.titleLarge),
                const Spacer(),
                StatusBadge(
                  label: primary?.gptExplanation != null
                      ? (primary!.gptModel ?? 'GPT-4o').toUpperCase()
                      : 'ML MODEL',
                  color: primary?.gptExplanation != null
                      ? AppColors.green
                      : AppColors.textSecondary,
                  icon: primary?.gptExplanation != null
                      ? Icons.auto_awesome
                      : Icons.psychology_alt_outlined,
                ),
              ],
            ),
            const SizedBox(height: 14),
            if (primary != null)
              _AiRecommendationCard(
                prediction: primary,
                elevation: pred?.elevationM ?? 0,
              )
            else
              const _LoadingCard(message: 'Generating AI recommendation...'),
            if (state.error != null) ...[
              const SizedBox(height: 14),
              CardShell(
                borderColor: AppColors.red.withValues(alpha: 0.5),
                child: Row(
                  children: [
                    const Icon(Icons.error_outline,
                        color: AppColors.red, size: 20),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        state.error!,
                        style: const TextStyle(
                          color: AppColors.red,
                          fontSize: 13,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _header(BuildContext context, String locationLabel) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: AppColors.greenSoft,
            borderRadius: BorderRadius.circular(10),
          ),
          child: const Icon(Icons.location_on,
              color: AppColors.green, size: 16),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Row(
            children: [
              Flexible(
                child: Text(
                  locationLabel.length > 30
                      ? locationLabel.substring(0, 30)
                      : locationLabel,
                  style: const TextStyle(
                    color: AppColors.textPrimary,
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              const SizedBox(width: 6),
              Container(
                width: 6,
                height: 6,
                decoration: const BoxDecoration(
                  color: AppColors.amber,
                  shape: BoxShape.circle,
                ),
              ),
            ],
          ),
        ),
        IconButton(
          icon: const Icon(Icons.settings_outlined,
              color: AppColors.textSecondary, size: 20),
          onPressed: () => Navigator.of(context).push(
            MaterialPageRoute(builder: (_) => const SettingsScreen()),
          ),
        ),
        IconButton(
          icon: const Icon(Icons.refresh,
              color: AppColors.textSecondary, size: 20),
          onPressed: AppStateProvider.of(context).refresh,
        ),
        Stack(
          clipBehavior: Clip.none,
          children: [
            const Icon(Icons.notifications_none_rounded,
                color: AppColors.textSecondary, size: 22),
            Positioned(
              top: -3,
              right: -3,
              child: Container(
                padding: const EdgeInsets.all(3),
                decoration: const BoxDecoration(
                  color: AppColors.red,
                  shape: BoxShape.circle,
                ),
                child: const Text(
                  '3',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 9,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ),
          ],
        ),
        const SizedBox(width: 4),
      ],
    );
  }

  String _seasonSubtitle() {
    final now = DateTime.now();
    return '${_formatFullWeekdayMonthDay(now)} · Spring Planting Season';
  }

  Widget _fieldStats(CropPrediction p) {
    final avg14 = p.forecast14d;
    final avgTemp = avg14.isEmpty
        ? 0.0
        : avg14.map((d) => (d.tempMax + d.tempMin) / 2).reduce((a, b) => a + b) /
            avg14.length;
    final avgPrecip =
        avg14.fold<double>(0, (sum, d) => sum + d.precipitation);
    final humidity = 52 - (p.avgFrostProbability14d * 30).round();
    return Row(
      children: [
        Expanded(
          child: StatTile(
            icon: Icons.thermostat,
            iconColor: AppColors.amber,
            label: 'Temperature',
            value: avgTemp.toStringAsFixed(1),
            unit: '°C',
            trend: 'Stable',
            trendColor: AppColors.textSecondary,
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: StatTile(
            icon: Icons.water_drop,
            iconColor: AppColors.blue,
            label: 'Humidity',
            value: '$humidity',
            unit: '%',
            trend: 'Stable',
            trendColor: AppColors.textSecondary,
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: StatTile(
            icon: Icons.grain,
            iconColor: AppColors.purple,
            label: 'Rainfall',
            value: avgPrecip.toStringAsFixed(0),
            unit: 'mm',
            trend: avgPrecip < 5 ? 'Down' : 'Stable',
            trendColor:
                avgPrecip < 5 ? AppColors.red : AppColors.textSecondary,
          ),
        ),
      ],
    );
  }

  Widget _fieldStatsEmpty() {
    return const Row(
      children: [
        Expanded(
          child: StatTile(
            icon: Icons.thermostat,
            iconColor: AppColors.amber,
            label: 'Temperature',
            value: '—',
          ),
        ),
        SizedBox(width: 10),
        Expanded(
          child: StatTile(
            icon: Icons.water_drop,
            iconColor: AppColors.blue,
            label: 'Humidity',
            value: '—',
          ),
        ),
        SizedBox(width: 10),
        Expanded(
          child: StatTile(
            icon: Icons.grain,
            iconColor: AppColors.purple,
            label: 'Rainfall',
            value: '—',
          ),
        ),
      ],
    );
  }
}

class _LiveWeatherLoading extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return CardShell(
      padding: const EdgeInsets.symmetric(vertical: 34),
      child: const Center(
        child: Column(
          children: [
            SizedBox(
              width: 28,
              height: 28,
              child: CircularProgressIndicator(
                color: AppColors.green,
                strokeWidth: 2.5,
              ),
            ),
            SizedBox(height: 14),
            Text('Fetching live weather...',
                style: TextStyle(color: AppColors.textSecondary)),
          ],
        ),
      ),
    );
  }
}

class _LiveWeatherCard extends StatelessWidget {
  final CropPrediction prediction;
  const _LiveWeatherCard({required this.prediction});

  @override
  Widget build(BuildContext context) {
    final today = prediction.forecast14d.isNotEmpty
        ? prediction.forecast14d.first
        : null;
    final days = prediction.forecast14d.take(5).toList();
    final humidity = 52 - (prediction.avgFrostProbability14d * 30).round();
    return CardShell(
      padding: const EdgeInsets.all(18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.cloud, color: AppColors.textSecondary, size: 20),
              const SizedBox(width: 10),
              const Text('Live Weather',
                  style: TextStyle(
                    color: AppColors.textPrimary,
                    fontSize: 17,
                    fontWeight: FontWeight.w700,
                  )),
              const SizedBox(width: 10),
              Container(
                width: 6,
                height: 6,
                decoration: const BoxDecoration(
                  color: AppColors.green,
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 5),
              const Text(
                'LIVE',
                style: TextStyle(
                  color: AppColors.green,
                  fontSize: 11,
                  letterSpacing: 1.2,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
          const SizedBox(height: 18),
          Row(
            children: [
              Expanded(
                child: _metric(Icons.thermostat, AppColors.amber,
                    '${today?.tempMin.toStringAsFixed(1) ?? '—'}°C',
                    'Temperature'),
              ),
              Expanded(
                child: _metric(Icons.water_drop, AppColors.blue,
                    '$humidity%', 'Humidity'),
              ),
              Expanded(
                child: _metric(
                    Icons.air, AppColors.green, '4.4 km/h', 'Wind'),
              ),
              Expanded(
                child: _metric(Icons.wb_sunny_outlined, AppColors.amber,
                    '0.1', 'UV Index'),
              ),
            ],
          ),
          if (days.isNotEmpty) ...[
            const SizedBox(height: 22),
            Row(
              children: days.map((d) {
                final dow = _formatShortWeekday(d.date);
                return Expanded(
                  child: Column(
                    children: [
                      Text(dow,
                          style: const TextStyle(
                            color: AppColors.textSecondary,
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                          )),
                      const SizedBox(height: 6),
                      Icon(
                        d.precipitation > 1
                            ? Icons.cloudy_snowing
                            : d.tempMax > 15
                                ? Icons.wb_sunny
                                : Icons.cloud,
                        color: d.precipitation > 1
                            ? AppColors.blue
                            : (d.tempMax > 15
                                ? AppColors.amber
                                : AppColors.textSecondary),
                        size: 22,
                      ),
                      const SizedBox(height: 6),
                      Text(
                        '${d.tempMax.toStringAsFixed(1)}°',
                        style: const TextStyle(
                          color: AppColors.textPrimary,
                          fontSize: 14,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      Text(
                        '${d.tempMin.toStringAsFixed(1)}°',
                        style: const TextStyle(
                          color: AppColors.textMuted,
                          fontSize: 11,
                        ),
                      ),
                    ],
                  ),
                );
              }).toList(),
            ),
          ]
        ],
      ),
    );
  }

  Widget _metric(IconData icon, Color color, String value, String label) {
    return Column(
      children: [
        Icon(icon, color: color, size: 22),
        const SizedBox(height: 8),
        Text(value,
            style: TextStyle(
              color: color,
              fontSize: 17,
              fontWeight: FontWeight.w700,
            )),
        const SizedBox(height: 2),
        Text(label,
            style: const TextStyle(
              color: AppColors.textSecondary,
              fontSize: 11,
            )),
      ],
    );
  }
}

class _AlertChipsRow extends StatelessWidget {
  final CropPrediction prediction;
  const _AlertChipsRow({required this.prediction});

  @override
  Widget build(BuildContext context) {
    final frostRisk = prediction.cropFrostRiskDays14d;
    final windowText = prediction.recommendedDate != null
        ? 'Optimal ${prediction.cropNameEn.toLowerCase()} window opens'
        : 'Window closed for season';
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: [
          InfoChip(
            text: frostRisk > 0
                ? 'Frost probability ${(prediction.avgFrostProbability14d * 100).toStringAsFixed(0)}% next 14d'
                : 'No frost risk next 14d',
            color: frostRisk > 0 ? AppColors.amber : AppColors.green,
          ),
          const SizedBox(width: 10),
          InfoChip(text: windowText, color: AppColors.blue),
        ],
      ),
    );
  }
}

class _ClimateResilienceCard extends StatelessWidget {
  const _ClimateResilienceCard();

  @override
  Widget build(BuildContext context) {
    final state = AppStateProvider.of(context);
    final primary = state.prediction?.predictions.isNotEmpty == true
        ? state.prediction!.predictions.first
        : null;
    final score = primary == null
        ? 82
        : (primary.confidenceOverall * 100).clamp(0, 100).round();
    final rating = score >= 80
        ? 'EXCELLENT'
        : score >= 60
            ? 'GOOD'
            : score >= 40
                ? 'FAIR'
                : 'POOR';
    final ratingColor = score >= 80
        ? AppColors.green
        : score >= 60
            ? AppColors.amber
            : AppColors.red;

    return CardShell(
      borderColor: AppColors.green.withValues(alpha: 0.55),
      glow: true,
      padding: const EdgeInsets.all(0),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              height: 170,
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [Color(0xFF2B4A30), Color(0xFF0F1A12)],
                ),
              ),
              child: CustomPaint(
                painter: _FieldPainter(),
                child: const SizedBox.expand(),
              ),
            ),
            Container(
              padding: const EdgeInsets.all(18),
              decoration: const BoxDecoration(
                color: AppColors.card,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Expanded(
                        child: Text(
                          'FIELD REGION',
                          style: TextStyle(
                            color: AppColors.textSecondary,
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                            letterSpacing: 1.6,
                          ),
                        ),
                      ),
                      StatusBadge(label: rating, color: ratingColor),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Text(
                    state.farm?.locationLabel ?? 'Upper Bavaria · Zone 7b',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 16),
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(
                        '$score',
                        style: const TextStyle(
                          color: AppColors.green,
                          fontSize: 52,
                          fontWeight: FontWeight.w800,
                          height: 1,
                        ),
                      ),
                      const Padding(
                        padding: EdgeInsets.only(bottom: 10, left: 2),
                        child: Text(
                          '/100',
                          style: TextStyle(
                            color: AppColors.textSecondary,
                            fontSize: 16,
                          ),
                        ),
                      ),
                      const SizedBox(width: 20),
                      const Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Climate Resilience',
                              style: TextStyle(
                                color: AppColors.textPrimary,
                                fontSize: 16,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                            SizedBox(height: 4),
                            Text(
                              'Spring 2025',
                              style: TextStyle(
                                color: AppColors.textSecondary,
                                fontSize: 13,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),
                  ProgressBar(value: score / 100, color: ratingColor),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _FieldPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final p = Paint()..color = const Color(0xFF1A3020);
    for (double y = size.height * 0.55; y < size.height; y += 8) {
      p.color = Color.lerp(
        const Color(0xFF1A3020),
        const Color(0xFF0A180D),
        (y - size.height * 0.55) / (size.height * 0.45),
      )!;
      canvas.drawRect(Rect.fromLTWH(0, y, size.width, 4), p);
    }
    final linesP = Paint()
      ..color = Colors.black.withValues(alpha: 0.25)
      ..strokeWidth = 1;
    for (int i = 0; i < 40; i++) {
      final x = (i / 40) * size.width;
      canvas.drawLine(
        Offset(x, size.height * 0.6),
        Offset(x + (x - size.width / 2) * 0.4, size.height),
        linesP,
      );
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class _AiRecommendationCard extends StatelessWidget {
  final CropPrediction prediction;
  final double elevation;
  const _AiRecommendationCard({
    required this.prediction,
    required this.elevation,
  });

  @override
  Widget build(BuildContext context) {
    final successPct = (prediction.recommendedConfidence * 100)
        .clamp(0, 100)
        .round();
    final window = prediction.recommendedDate != null
        ? _formatWindow(prediction.recommendedDate!)
        : 'Closed';
    final varietyMap = {
      'corn': 'DKC 6088',
      'wheat': 'Bosut',
      'soybeans': 'Maximus RR',
      'barley': 'Rex',
      'potato': 'Agria',
      'tomato': 'Roma VF',
      'onion': 'Sturon',
      'pepper': 'Kurtovska',
      'rapeseed': 'Mercedes',
      'sunflower': 'NS-H-111',
    };
    final variety = varietyMap[prediction.cropId] ?? '';
    final yieldChange = 12 + (prediction.confidenceOverall * 20).round();
    final lossAvoided = 8000 + (prediction.confidenceOverall * 10000).round();

    return CardShell(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                prediction.cropNameEn,
                style: Theme.of(context).textTheme.headlineMedium,
              ),
              const Spacer(),
              const StatusBadge(
                label: 'OPTIMAL WINDOW',
                color: AppColors.green,
                icon: Icons.check_circle_outline,
              ),
            ],
          ),
          if (variety.isNotEmpty) ...[
            const SizedBox(height: 2),
            Text(variety,
                style: const TextStyle(
                  color: AppColors.textSecondary,
                  fontSize: 14,
                )),
          ],
          const SizedBox(height: 22),
          Row(
            children: [
              const Expanded(
                child: Text(
                  'SUCCESS PROBABILITY',
                  style: TextStyle(
                    color: AppColors.textSecondary,
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 1.4,
                  ),
                ),
              ),
              Text(
                '$successPct%',
                style: const TextStyle(
                  color: AppColors.green,
                  fontSize: 28,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          ProgressBar(value: successPct / 100, color: AppColors.green),
          const SizedBox(height: 22),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.cardElevated,
              borderRadius: BorderRadius.circular(14),
            ),
            child: Row(
              children: [
                Expanded(
                    child: _metric(Icons.calendar_today, 'SOW WINDOW', window,
                        AppColors.textPrimary)),
                Expanded(
                    child: _metric(Icons.trending_up, 'YIELD CHANGE',
                        '+$yieldChange%', AppColors.green)),
                Expanded(
                    child: _metric(Icons.euro, 'LOSS AVOIDED',
                        '€${_formatMoney(lossAvoided)}', AppColors.amber)),
              ],
            ),
          ),
          const SizedBox(height: 18),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: AppColors.border),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'OPTIMAL SOWING DAY',
                  style: TextStyle(
                    color: AppColors.textSecondary,
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 1.4,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  window,
                  style: const TextStyle(
                    color: AppColors.green,
                    fontSize: 26,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ],
            ),
          ),
          if (prediction.gptExplanation != null &&
              prediction.gptExplanation!.isNotEmpty) ...[
            const SizedBox(height: 18),
            Row(
              children: [
                const Icon(Icons.auto_awesome,
                    color: AppColors.green, size: 14),
                const SizedBox(width: 6),
                Text(
                  'GPT ADVISOR',
                  style: TextStyle(
                    color: AppColors.green.withValues(alpha: 0.9),
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 1.6,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            ...prediction.gptExplanation!.map(
              (e) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      margin: const EdgeInsets.only(top: 6),
                      width: 6,
                      height: 6,
                      decoration: const BoxDecoration(
                        color: AppColors.green,
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        e,
                        style: const TextStyle(
                          color: AppColors.textPrimary,
                          fontSize: 13,
                          height: 1.45,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ] else if (prediction.explanation.isNotEmpty) ...[
            const SizedBox(height: 18),
            ...prediction.explanation.take(3).map(
                  (e) => Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          margin: const EdgeInsets.only(top: 6),
                          width: 6,
                          height: 6,
                          decoration: const BoxDecoration(
                            color: AppColors.green,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            e,
                            style: const TextStyle(
                              color: AppColors.textPrimary,
                              fontSize: 13,
                              height: 1.45,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
          ],
        ],
      ),
    );
  }

  Widget _metric(IconData icon, String label, String value, Color valueColor) {
    return Column(
      children: [
        Icon(icon, color: AppColors.textSecondary, size: 18),
        const SizedBox(height: 8),
        Text(label,
            style: const TextStyle(
              color: AppColors.textSecondary,
              fontSize: 10,
              fontWeight: FontWeight.w700,
              letterSpacing: 1.1,
            ),
            textAlign: TextAlign.center),
        const SizedBox(height: 6),
        Text(value,
            style: TextStyle(
              color: valueColor,
              fontSize: 13,
              fontWeight: FontWeight.w700,
            ),
            textAlign: TextAlign.center),
      ],
    );
  }

  String _formatWindow(String iso) {
    final d = DateTime.parse(iso);
    final end = d.add(const Duration(days: 4));
    return '${_formatMonthDay(d)}–${end.day}';
  }

  String _formatMoney(int n) {
    return n.toString().replaceAllMapped(
          RegExp(r'(\d)(?=(\d{3})+(?!\d))'),
          (m) => '${m[1]},',
        );
  }
}

class _LoadingCard extends StatelessWidget {
  final String message;
  const _LoadingCard({required this.message});
  @override
  Widget build(BuildContext context) {
    return CardShell(
      padding: const EdgeInsets.symmetric(vertical: 40),
      child: Center(
        child: Column(
          children: [
            const SizedBox(
              width: 26,
              height: 26,
              child: CircularProgressIndicator(
                  color: AppColors.green, strokeWidth: 2.5),
            ),
            const SizedBox(height: 12),
            Text(message,
                style: const TextStyle(color: AppColors.textSecondary)),
          ],
        ),
      ),
    );
  }
}
