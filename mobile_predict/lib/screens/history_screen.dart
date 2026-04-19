import 'package:flutter/material.dart';

import '../theme.dart';
import '../widgets/common.dart';

class HistoryScreen extends StatelessWidget {
  const HistoryScreen({super.key});

  static const _events = [
    (
      year: '2022',
      title: 'Record European Heatwave',
      detail: '+3.4°C · Loss: €2.1B',
      severity: 'Critical',
      color: AppColors.red,
    ),
    (
      year: '2020',
      title: 'Extreme Drought Season',
      detail: '+3.1°C · Loss: €890M',
      severity: 'High',
      color: AppColors.amber,
    ),
    (
      year: '2018',
      title: 'Summer Drought & Wildfire',
      detail: '+2.8°C · Loss: €1.4B',
      severity: 'Critical',
      color: AppColors.red,
    ),
    (
      year: '2012',
      title: 'Spring Frost Anomaly',
      detail: '+1.3°C · Loss: €340M',
      severity: 'Medium',
      color: AppColors.blue,
    ),
    (
      year: '2010',
      title: 'Cold Winter Extreme',
      detail: '-1.1°C · Loss: €670M',
      severity: 'High',
      color: AppColors.amber,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.fromLTRB(20, 16, 20, 24),
        children: [
          const SectionLabel(
              text: 'HISTORY',
              icon: Icons.history,
              color: AppColors.green),
          const SizedBox(height: 14),
          Text('Climate Archive',
              style: Theme.of(context).textTheme.headlineLarge),
          const SizedBox(height: 6),
          const Text(
            '50-year anomaly record · regional scope',
            style: TextStyle(color: AppColors.textSecondary, fontSize: 14),
          ),
          const SizedBox(height: 22),
          Row(
            children: const [
              Expanded(
                child: _StressTile(
                  label: 'Temp Trend',
                  value: '+0.12°C/yr',
                  status: 'Stable',
                  statusColor: AppColors.green,
                ),
              ),
              SizedBox(width: 12),
              Expanded(
                child: _StressTile(
                  label: 'Heat Stress',
                  value: '+0.18°C/yr',
                  status: 'Moderate stress',
                  statusColor: AppColors.amber,
                ),
              ),
            ],
          ),
          const SizedBox(height: 22),
          CardShell(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: const [
                    Icon(Icons.error_outline,
                        color: AppColors.amber, size: 22),
                    SizedBox(width: 10),
                    Text(
                      'Extreme Climate Events',
                      style: TextStyle(
                        color: AppColors.textPrimary,
                        fontSize: 18,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                ..._events.map((e) => _eventRow(e)),
              ],
            ),
          ),
          const SizedBox(height: 22),
          CardShell(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: const [
                    Icon(Icons.trending_up,
                        color: AppColors.red, size: 22),
                    SizedBox(width: 10),
                    Text('2030 Climate Projection',
                        style: TextStyle(
                          color: AppColors.textPrimary,
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                        )),
                  ],
                ),
                const SizedBox(height: 18),
                _projectionRow('Avg Temperature', '14.2°C', '15.8°C',
                    '+1.6°C', AppColors.red),
                const Divider(color: AppColors.border, height: 28),
                _projectionRow('Frost-Free Days', '198 days', '217 days',
                    '+19 days', AppColors.amber),
                const Divider(color: AppColors.border, height: 28),
                _projectionRow('Dry Spell Risk', 'Moderate', 'High',
                    '↑', AppColors.amber),
                const Divider(color: AppColors.border, height: 28),
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Expanded(
                      flex: 2,
                      child: Text('Yield Adaptation',
                          style: TextStyle(
                            color: AppColors.textSecondary,
                            fontSize: 14,
                          )),
                    ),
                    const Expanded(
                      child: Text('Standard',
                          style:
                              TextStyle(color: AppColors.textPrimary)),
                    ),
                    const Icon(Icons.arrow_forward,
                        color: AppColors.textSecondary, size: 16),
                    const SizedBox(width: 8),
                    const Expanded(
                      child: Text('Needed',
                          style: TextStyle(
                            color: AppColors.amber,
                            fontWeight: FontWeight.w700,
                          )),
                    ),
                    const Icon(Icons.warning_amber_rounded,
                        color: AppColors.amber, size: 18),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _eventRow(
      ({String year, String title, String detail, String severity, Color color}) e) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: Row(
        children: [
          Container(
            width: 56,
            padding: const EdgeInsets.symmetric(vertical: 10),
            decoration: BoxDecoration(
              color: e.color.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(8),
              border:
                  Border.all(color: e.color.withValues(alpha: 0.35)),
            ),
            child: Text(
              e.year,
              textAlign: TextAlign.center,
              style: TextStyle(
                color: e.color,
                fontSize: 15,
                fontWeight: FontWeight.w800,
              ),
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  e.title,
                  style: const TextStyle(
                    color: AppColors.textPrimary,
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 3),
                Text(
                  e.detail,
                  style: const TextStyle(
                    color: AppColors.textSecondary,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          StatusBadge(label: e.severity, color: e.color),
        ],
      ),
    );
  }

  Widget _projectionRow(String label, String now, String future, String delta,
      Color deltaColor) {
    return Row(
      children: [
        Expanded(
          flex: 2,
          child: Text(label,
              style: const TextStyle(
                color: AppColors.textSecondary,
                fontSize: 14,
              )),
        ),
        Expanded(
          child: Text(now,
              style: const TextStyle(color: AppColors.textPrimary)),
        ),
        const Icon(Icons.arrow_forward,
            color: AppColors.textSecondary, size: 16),
        const SizedBox(width: 8),
        Expanded(
          child: Text(future,
              style: const TextStyle(
                color: AppColors.amber,
                fontWeight: FontWeight.w700,
              )),
        ),
        Text(delta,
            style: TextStyle(
              color: deltaColor,
              fontSize: 13,
              fontWeight: FontWeight.w700,
            )),
      ],
    );
  }
}

class _StressTile extends StatelessWidget {
  final String label;
  final String value;
  final String status;
  final Color statusColor;
  const _StressTile({
    required this.label,
    required this.value,
    required this.status,
    required this.statusColor,
  });

  @override
  Widget build(BuildContext context) {
    return CardShell(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label.toUpperCase(),
              style: const TextStyle(
                color: AppColors.textSecondary,
                fontSize: 11,
                letterSpacing: 1.2,
                fontWeight: FontWeight.w700,
              )),
          const SizedBox(height: 8),
          Text(value,
              style: const TextStyle(
                color: AppColors.textPrimary,
                fontSize: 20,
                fontWeight: FontWeight.w800,
              )),
          const SizedBox(height: 4),
          Text(status,
              style: TextStyle(color: statusColor, fontSize: 12)),
        ],
      ),
    );
  }
}
