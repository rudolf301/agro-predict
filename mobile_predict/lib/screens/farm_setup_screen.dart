import 'package:flutter/material.dart';

import '../services/location_service.dart';
import '../state/app_state.dart';
import '../state/provider.dart';
import '../theme.dart';
import '../widgets/common.dart';
import 'home_scaffold.dart';

const _availableCrops = <Map<String, String>>[
  {'id': 'corn', 'en': 'Corn', 'bs': 'Kukuruz'},
  {'id': 'wheat', 'en': 'Wheat', 'bs': 'P\u0161enica'},
  {'id': 'soybeans', 'en': 'Soybeans', 'bs': 'Soja'},
  {'id': 'barley', 'en': 'Barley', 'bs': 'Je\u010dam'},
  {'id': 'rapeseed', 'en': 'Rapeseed', 'bs': 'Uljana repica'},
  {'id': 'potato', 'en': 'Potatoes', 'bs': 'Krompir'},
];

const _farmSizes = ['< 5 ha', '5-20 ha', '20-50 ha', '50-100 ha', '> 100 ha'];

class FarmSetupScreen extends StatefulWidget {
  const FarmSetupScreen({super.key});

  @override
  State<FarmSetupScreen> createState() => _FarmSetupScreenState();
}

class _FarmSetupScreenState extends State<FarmSetupScreen> {
  final Set<String> _crops = {'wheat'};
  String _size = '5-20 ha';
  final _locationService = LocationService();
  bool _submitting = false;

  Future<void> _submit(AppState state) async {
    if (_crops.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Select at least one crop')),
      );
      return;
    }
    setState(() => _submitting = true);
    final loc = await _locationService.getCurrent();
    state.setFarm(FarmConfig(
      lat: loc.lat,
      lon: loc.lon,
      locationLabel: loc.label,
      selectedCropIds: _crops.toList(),
      farmSize: _size,
    ));
    unawaited(state.refresh());
    if (!mounted) return;
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(builder: (_) => const HomeScaffold()),
    );
  }

  @override
  Widget build(BuildContext context) {
    final appState = AppStateProvider.of(context);
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(24, 20, 24, 32),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppColors.greenSoft,
                  borderRadius: BorderRadius.circular(14),
                ),
                child: const Icon(Icons.location_on,
                    color: AppColors.green, size: 24),
              ),
              const SizedBox(height: 28),
              const SectionLabel(text: 'FARM SETUP'),
              const SizedBox(height: 12),
              Text(
                'Tell us about\nyour farm',
                style: Theme.of(context).textTheme.displayLarge,
              ),
              const SizedBox(height: 14),
              Text(
                "We'll personalise predictions for your specific field conditions.",
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: AppColors.textSecondary,
                    ),
              ),
              const SizedBox(height: 36),
              const _LabelSmall('SELECT YOUR CROPS'),
              const SizedBox(height: 14),
              Wrap(
                spacing: 10,
                runSpacing: 12,
                children: _availableCrops.map((c) {
                  final id = c['id']!;
                  return PillChip(
                    label: c['en']!,
                    selected: _crops.contains(id),
                    onTap: () => setState(() {
                      if (_crops.contains(id)) {
                        _crops.remove(id);
                      } else {
                        _crops.add(id);
                      }
                    }),
                  );
                }).toList(),
              ),
              const SizedBox(height: 32),
              const _LabelSmall('FARM SIZE'),
              const SizedBox(height: 14),
              Wrap(
                spacing: 10,
                runSpacing: 12,
                children: _farmSizes
                    .map((s) => PillChip(
                          label: s,
                          selected: _size == s,
                          onTap: () => setState(() => _size = s),
                        ))
                    .toList(),
              ),
              const SizedBox(height: 28),
              const _LabelSmall('FIELD MAPPING'),
              const SizedBox(height: 14),
              CardShell(
                padding: const EdgeInsets.all(0),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(20),
                  child: Stack(
                    children: [
                      Container(
                        height: 220,
                        color: const Color(0xFF0A0F0B),
                        child: CustomPaint(
                          painter: _GridPainter(),
                          child: const SizedBox.expand(),
                        ),
                      ),
                      const Positioned(
                        left: 16,
                        top: 14,
                        child: Row(
                          children: [
                            Icon(Icons.eco,
                                color: AppColors.green, size: 16),
                            SizedBox(width: 8),
                            Text(
                              'Field Mapping',
                              style: TextStyle(
                                color: AppColors.textPrimary,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const Positioned(
                        right: 14,
                        top: 12,
                        child: StatusBadge(
                          label: 'SATELLITE',
                          color: AppColors.green,
                        ),
                      ),
                      const Positioned(
                        bottom: 14,
                        left: 0,
                        right: 0,
                        child: Center(
                          child: Text(
                            'Tap map to set boundary',
                            style: TextStyle(
                              color: AppColors.textSecondary,
                              fontSize: 13,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 32),
              SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton(
                  onPressed: _submitting ? null : () => _submit(appState),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.green,
                    foregroundColor: Colors.black,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(100),
                    ),
                    textStyle: const TextStyle(
                      fontSize: 17,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  child: _submitting
                      ? const SizedBox(
                          width: 22,
                          height: 22,
                          child: CircularProgressIndicator(
                            color: Colors.black,
                            strokeWidth: 2.5,
                          ),
                        )
                      : const Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text('Continue'),
                            SizedBox(width: 8),
                            Icon(Icons.chevron_right, size: 22),
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

class _LabelSmall extends StatelessWidget {
  final String text;
  const _LabelSmall(this.text);
  @override
  Widget build(BuildContext context) {
    return Text(
      text,
      style: const TextStyle(
        color: AppColors.textSecondary,
        fontSize: 12,
        fontWeight: FontWeight.w700,
        letterSpacing: 2,
      ),
    );
  }
}

class _GridPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final p = Paint()
      ..color = AppColors.green.withValues(alpha: 0.08)
      ..strokeWidth = 1;
    const step = 28.0;
    for (double x = 0; x < size.width; x += step) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), p);
    }
    for (double y = 0; y < size.height; y += step) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), p);
    }
    final centerP = Paint()..color = AppColors.green.withValues(alpha: 0.35);
    canvas.drawCircle(
      Offset(size.width / 2, size.height / 2),
      8,
      centerP,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

void unawaited(Future<void> future) {
  future.catchError((_) {});
}
