import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'screens/onboarding_screen.dart';
import 'services/api_service.dart';
import 'state/app_state.dart';
import 'state/provider.dart';
import 'theme.dart';

const _apiBaseUrl = String.fromEnvironment(
  'API_BASE',
  defaultValue: 'http://192.168.1.7:8765',
);

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.light,
    systemNavigationBarColor: AppColors.bg,
  ));
  final api = ApiService(baseUrl: _apiBaseUrl);
  final state = AppState(api);
  runApp(AgroPredictApp(state: state));
}

class AgroPredictApp extends StatelessWidget {
  final AppState state;
  const AgroPredictApp({super.key, required this.state});

  @override
  Widget build(BuildContext context) {
    return AppStateProvider(
      state: state,
      child: MaterialApp(
        title: 'Agro-Predict',
        debugShowCheckedModeBanner: false,
        theme: buildTheme(),
        home: const OnboardingScreen(),
      ),
    );
  }
}
