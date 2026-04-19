import 'package:flutter/material.dart';

import '../theme.dart';
import '../widgets/common.dart';
import 'farm_setup_screen.dart';

class _Slide {
  final String label;
  final IconData labelIcon;
  final Color labelColor;
  final String title;
  final String subtitle;
  final List<Color> bgGradient;
  final IconData heroIcon;

  const _Slide({
    required this.label,
    required this.labelIcon,
    required this.labelColor,
    required this.title,
    required this.subtitle,
    required this.bgGradient,
    required this.heroIcon,
  });
}

const _slides = <_Slide>[
  _Slide(
    label: 'SMART FARMING',
    labelIcon: Icons.location_on,
    labelColor: AppColors.green,
    title: "Know Your\nField's Future",
    subtitle:
        'AI-powered climate analysis tailored to your exact field location and crop variety.',
    bgGradient: [Color(0xFF1E3A1E), Color(0xFF050708)],
    heroIcon: Icons.landscape,
  ),
  _Slide(
    label: 'AI ENGINE',
    labelIcon: Icons.memory,
    labelColor: AppColors.amber,
    title: 'Predict Before\nRisks Arrive',
    subtitle:
        'Ensemble models trained on 20 years of regional data deliver 91% forecast accuracy.',
    bgGradient: [Color(0xFF1A3020), Color(0xFF050708)],
    heroIcon: Icons.analytics,
  ),
  _Slide(
    label: 'HAILGUARD',
    labelIcon: Icons.shield,
    labelColor: AppColors.green,
    title: 'Automated\nPlant Protection',
    subtitle:
        'Hardware deploys hail shields the moment we detect incoming storm cells.',
    bgGradient: [Color(0xFF1F2429), Color(0xFF050708)],
    heroIcon: Icons.umbrella,
  ),
];

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final _pageController = PageController();
  int _page = 0;

  void _next() {
    if (_page == _slides.length - 1) {
      _goToSetup();
    } else {
      _pageController.nextPage(
        duration: const Duration(milliseconds: 280),
        curve: Curves.easeOut,
      );
    }
  }

  void _goToSetup() {
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(builder: (_) => const FarmSetupScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          PageView.builder(
            controller: _pageController,
            itemCount: _slides.length,
            onPageChanged: (i) => setState(() => _page = i),
            itemBuilder: (_, i) => _SlideView(slide: _slides[i]),
          ),
          SafeArea(
            child: Align(
              alignment: Alignment.bottomCenter,
              child: Padding(
                padding:
                    const EdgeInsets.symmetric(horizontal: 24, vertical: 24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: List.generate(_slides.length, (i) {
                        final active = i == _page;
                        return AnimatedContainer(
                          duration: const Duration(milliseconds: 220),
                          margin: const EdgeInsets.symmetric(horizontal: 4),
                          width: active ? 22 : 6,
                          height: 6,
                          decoration: BoxDecoration(
                            color: active
                                ? AppColors.green
                                : AppColors.textMuted,
                            borderRadius: BorderRadius.circular(100),
                          ),
                        );
                      }),
                    ),
                    const SizedBox(height: 24),
                    SizedBox(
                      width: double.infinity,
                      height: 56,
                      child: ElevatedButton(
                        onPressed: _next,
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
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(_page == _slides.length - 1
                                ? 'Start'
                                : 'Continue'),
                            const SizedBox(width: 8),
                            const Icon(Icons.chevron_right, size: 22),
                          ],
                        ),
                      ),
                    ),
                    TextButton(
                      onPressed: _goToSetup,
                      child: const Text(
                        'Skip',
                        style: TextStyle(
                          color: AppColors.textSecondary,
                          fontSize: 15,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _SlideView extends StatelessWidget {
  final _Slide slide;
  const _SlideView({required this.slide});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: slide.bgGradient,
        ),
      ),
      child: Stack(
        children: [
          Positioned.fill(
            child: CustomPaint(
              painter: _HeroPainter(
                icon: slide.heroIcon,
                color: slide.labelColor,
              ),
            ),
          ),
          Align(
            alignment: Alignment.bottomLeft,
            child: Padding(
              padding: const EdgeInsets.fromLTRB(24, 0, 24, 180),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  SectionLabel(
                    text: slide.label,
                    icon: slide.labelIcon,
                    color: slide.labelColor,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    slide.title,
                    style: Theme.of(context).textTheme.displayLarge?.copyWith(
                          height: 1.05,
                        ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    slide.subtitle,
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                          color: AppColors.textSecondary,
                          height: 1.4,
                        ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _HeroPainter extends CustomPainter {
  final IconData icon;
  final Color color;
  _HeroPainter({required this.icon, required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final iconSize = size.width * 0.75;
    final textPainter = TextPainter(
      text: TextSpan(
        text: String.fromCharCode(icon.codePoint),
        style: TextStyle(
          fontSize: iconSize,
          fontFamily: icon.fontFamily,
          color: color.withValues(alpha: 0.08),
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout();
    textPainter.paint(
      canvas,
      Offset(
        (size.width - textPainter.width) / 2,
        size.height * 0.25,
      ),
    );
  }

  @override
  bool shouldRepaint(covariant _HeroPainter oldDelegate) =>
      oldDelegate.icon != icon || oldDelegate.color != color;
}
