import 'package:flutter/material.dart';

class AppColors {
  static const bg = Color(0xFF050708);
  static const card = Color(0xFF0E1214);
  static const cardElevated = Color(0xFF151A1D);
  static const border = Color(0xFF1F2529);
  static const green = Color(0xFF10D878);
  static const greenDark = Color(0xFF0A9454);
  static const greenSoft = Color(0x3310D878);
  static const amber = Color(0xFFF5A524);
  static const amberSoft = Color(0x33F5A524);
  static const red = Color(0xFFEF4444);
  static const redSoft = Color(0x33EF4444);
  static const blue = Color(0xFF3B82F6);
  static const blueSoft = Color(0x333B82F6);
  static const purple = Color(0xFF8B5CF6);
  static const textPrimary = Color(0xFFF5F7F8);
  static const textSecondary = Color(0xFF8A9499);
  static const textMuted = Color(0xFF5C6A72);
}

ThemeData buildTheme() {
  return ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    scaffoldBackgroundColor: AppColors.bg,
    colorScheme: const ColorScheme.dark(
      surface: AppColors.bg,
      primary: AppColors.green,
      secondary: AppColors.amber,
      error: AppColors.red,
    ),
    textTheme: const TextTheme(
      displayLarge: TextStyle(
        color: AppColors.textPrimary,
        fontSize: 40,
        fontWeight: FontWeight.w700,
        letterSpacing: -0.5,
      ),
      headlineLarge: TextStyle(
        color: AppColors.textPrimary,
        fontSize: 32,
        fontWeight: FontWeight.w700,
        letterSpacing: -0.5,
      ),
      headlineMedium: TextStyle(
        color: AppColors.textPrimary,
        fontSize: 24,
        fontWeight: FontWeight.w700,
      ),
      titleLarge: TextStyle(
        color: AppColors.textPrimary,
        fontSize: 20,
        fontWeight: FontWeight.w700,
      ),
      titleMedium: TextStyle(
        color: AppColors.textPrimary,
        fontSize: 16,
        fontWeight: FontWeight.w600,
      ),
      bodyLarge: TextStyle(color: AppColors.textPrimary, fontSize: 15),
      bodyMedium: TextStyle(color: AppColors.textSecondary, fontSize: 14),
      bodySmall: TextStyle(color: AppColors.textMuted, fontSize: 12),
      labelLarge: TextStyle(
        color: AppColors.textPrimary,
        fontSize: 13,
        fontWeight: FontWeight.w600,
        letterSpacing: 1.2,
      ),
      labelSmall: TextStyle(
        color: AppColors.textSecondary,
        fontSize: 11,
        fontWeight: FontWeight.w600,
        letterSpacing: 1.5,
      ),
    ),
  );
}
