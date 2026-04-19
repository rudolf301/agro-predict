import 'package:flutter/material.dart';

import '../theme.dart';
import '../widgets/common.dart';

class HailGuardScreen extends StatefulWidget {
  const HailGuardScreen({super.key});

  @override
  State<HailGuardScreen> createState() => _HailGuardScreenState();
}

class _HailGuardScreenState extends State<HailGuardScreen> {
  bool _autoMode = true;

  final _zones = <_Zone>[
    _Zone(code: 'A', id: 'Zone A-7', crop: 'Corn · 4.2 ha', battery: 92, status: ZoneStatus.deployed),
    _Zone(code: 'B', id: 'Zone B-3', crop: 'Wheat · 6.1 ha', battery: 78, status: ZoneStatus.retracted),
    _Zone(code: 'C', id: 'Zone C-1', crop: 'Soybeans · 3.8 ha', battery: 85, status: ZoneStatus.deploying),
    _Zone(code: 'D', id: 'Zone D-5', crop: 'Barley · 5.5 ha', battery: 14, status: ZoneStatus.error),
  ];

  @override
  Widget build(BuildContext context) {
    final deployed =
        _zones.where((z) => z.status == ZoneStatus.deployed).length;
    final avgBattery =
        _zones.map((z) => z.battery).reduce((a, b) => a + b) ~/ _zones.length;

    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.fromLTRB(20, 16, 20, 24),
        children: [
          const SectionLabel(
              text: 'HAILGUARD PRO', icon: Icons.shield_outlined),
          const SizedBox(height: 14),
          Text('Shield Control',
              style: Theme.of(context).textTheme.headlineLarge),
          const SizedBox(height: 6),
          Text(
            'Automated hail protection · ${_zones.length} field zones',
            style: const TextStyle(
                color: AppColors.textSecondary, fontSize: 14),
          ),
          const SizedBox(height: 22),
          Row(
            children: [
              Expanded(
                child: _topTile(Icons.shield_outlined,
                    '$deployed/${_zones.length}', 'Zones Active'),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: _topTile(Icons.battery_full_rounded,
                    '$avgBattery%', 'Avg Battery'),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: _topTile(Icons.wifi, '4/4', 'Signal'),
              ),
            ],
          ),
          const SizedBox(height: 20),
          CardShell(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.flash_on, color: AppColors.amber, size: 22),
                    const SizedBox(width: 8),
                    const Expanded(
                      child: Text('Global Controls',
                          style: TextStyle(
                            color: AppColors.textPrimary,
                            fontSize: 17,
                            fontWeight: FontWeight.w700,
                          )),
                    ),
                    const Text('Auto Mode',
                        style: TextStyle(
                          color: AppColors.textSecondary,
                          fontSize: 14,
                        )),
                    const SizedBox(width: 10),
                    Switch(
                      value: _autoMode,
                      onChanged: (v) => setState(() => _autoMode = v),
                      activeThumbColor: AppColors.green,
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: AppColors.cardElevated,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        margin: const EdgeInsets.only(top: 5),
                        width: 8,
                        height: 8,
                        decoration: BoxDecoration(
                          color: _autoMode
                              ? AppColors.green
                              : AppColors.textMuted,
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          _autoMode
                              ? 'Auto mode active — shields deploy automatically when hail probability exceeds 60%'
                              : 'Auto mode off — deploy shields manually per zone',
                          style: const TextStyle(
                            color: AppColors.textSecondary,
                            fontSize: 13,
                            height: 1.45,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 14),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () {
                          setState(() {
                            for (final z in _zones) {
                              if (z.status != ZoneStatus.error) {
                                z.status = ZoneStatus.deployed;
                              }
                            }
                          });
                        },
                        icon: const Icon(Icons.shield,
                            color: AppColors.green, size: 18),
                        label: const Text('Deploy All',
                            style: TextStyle(
                              color: AppColors.green,
                              fontWeight: FontWeight.w700,
                            )),
                        style: OutlinedButton.styleFrom(
                          side: const BorderSide(color: AppColors.green),
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(14),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () {
                          setState(() {
                            for (final z in _zones) {
                              if (z.status != ZoneStatus.error) {
                                z.status = ZoneStatus.retracted;
                              }
                            }
                          });
                        },
                        icon: const Icon(Icons.toggle_off,
                            color: AppColors.red, size: 18),
                        label: const Text('Retract All',
                            style: TextStyle(
                              color: AppColors.red,
                              fontWeight: FontWeight.w700,
                            )),
                        style: OutlinedButton.styleFrom(
                          side: const BorderSide(color: AppColors.red),
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(14),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 26),
          const Text('FIELD ZONES',
              style: TextStyle(
                color: AppColors.textSecondary,
                fontSize: 12,
                fontWeight: FontWeight.w700,
                letterSpacing: 1.8,
              )),
          const SizedBox(height: 14),
          ..._zones.map((z) => Padding(
                padding: const EdgeInsets.only(bottom: 14),
                child: _ZoneCard(
                  zone: z,
                  onToggle: () {
                    setState(() {
                      if (z.status == ZoneStatus.deployed) {
                        z.status = ZoneStatus.retracted;
                      } else if (z.status == ZoneStatus.retracted) {
                        z.status = ZoneStatus.deployed;
                      }
                    });
                  },
                ),
              )),
        ],
      ),
    );
  }

  Widget _topTile(IconData icon, String value, String label) {
    return CardShell(
      padding: const EdgeInsets.all(16),
      borderColor: AppColors.green.withValues(alpha: 0.35),
      child: Column(
        children: [
          Icon(icon, color: AppColors.green, size: 20),
          const SizedBox(height: 10),
          Text(value,
              style: const TextStyle(
                color: AppColors.green,
                fontSize: 22,
                fontWeight: FontWeight.w800,
              )),
          const SizedBox(height: 4),
          Text(label,
              style: const TextStyle(
                color: AppColors.textSecondary,
                fontSize: 12,
              )),
        ],
      ),
    );
  }
}

enum ZoneStatus { deployed, retracted, deploying, error }

class _Zone {
  final String code;
  final String id;
  final String crop;
  final int battery;
  ZoneStatus status;
  _Zone({
    required this.code,
    required this.id,
    required this.crop,
    required this.battery,
    required this.status,
  });
}

class _ZoneCard extends StatelessWidget {
  final _Zone zone;
  final VoidCallback onToggle;
  const _ZoneCard({required this.zone, required this.onToggle});

  @override
  Widget build(BuildContext context) {
    final (badgeLabel, badgeColor) = switch (zone.status) {
      ZoneStatus.deployed => ('DEPLOYED', AppColors.green),
      ZoneStatus.retracted => ('RETRACTED', AppColors.textSecondary),
      ZoneStatus.deploying => ('DEPLOYING...', AppColors.amber),
      ZoneStatus.error => ('ERROR', AppColors.red),
    };
    final batteryColor = zone.battery < 20
        ? AppColors.red
        : zone.battery < 50
            ? AppColors.amber
            : AppColors.green;

    return CardShell(
      borderColor: zone.status == ZoneStatus.error
          ? AppColors.red.withValues(alpha: 0.5)
          : null,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: badgeColor.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(
                      color: badgeColor.withValues(alpha: 0.4)),
                ),
                alignment: Alignment.center,
                child: Text(zone.code,
                    style: TextStyle(
                      color: badgeColor,
                      fontSize: 20,
                      fontWeight: FontWeight.w800,
                    )),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(zone.id,
                        style: const TextStyle(
                          color: AppColors.textPrimary,
                          fontSize: 17,
                          fontWeight: FontWeight.w700,
                        )),
                    const SizedBox(height: 2),
                    Text(zone.crop,
                        style: const TextStyle(
                          color: AppColors.textSecondary,
                          fontSize: 13,
                        )),
                  ],
                ),
              ),
              StatusBadge(
                label: badgeLabel,
                color: badgeColor,
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Icon(Icons.battery_full,
                  color: batteryColor, size: 18),
              const SizedBox(width: 8),
              Expanded(
                child: ProgressBar(
                  value: zone.battery / 100,
                  color: batteryColor,
                ),
              ),
              const SizedBox(width: 12),
              Text('${zone.battery}%',
                  style: const TextStyle(
                    color: AppColors.textPrimary,
                    fontWeight: FontWeight.w700,
                  )),
            ],
          ),
          const SizedBox(height: 14),
          if (zone.status == ZoneStatus.error)
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: AppColors.red.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
                border:
                    Border.all(color: AppColors.red.withValues(alpha: 0.4)),
              ),
              child: Row(
                children: const [
                  Icon(Icons.warning_amber_rounded,
                      color: AppColors.red, size: 18),
                  SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Node offline — Check battery & connection',
                      style:
                          TextStyle(color: AppColors.red, fontSize: 13),
                    ),
                  ),
                ],
              ),
            )
          else
            SizedBox(
              width: double.infinity,
              child: OutlinedButton(
                onPressed: onToggle,
                style: OutlinedButton.styleFrom(
                  side: BorderSide(color: badgeColor.withValues(alpha: 0.45)),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      zone.status == ZoneStatus.deployed
                          ? 'Retract Shield'
                          : zone.status == ZoneStatus.deploying
                              ? 'Deploying...'
                              : 'Deploy Shield',
                      style: TextStyle(
                        color: badgeColor,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(width: 6),
                    Icon(Icons.chevron_right,
                        color: badgeColor, size: 18),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
}
