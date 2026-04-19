import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:location/location.dart';

class LocationResult {
  final double lat;
  final double lon;
  final String label;
  final bool isFallback;
  final String? errorMessage;

  LocationResult({
    required this.lat,
    required this.lon,
    required this.label,
    this.isFallback = false,
    this.errorMessage,
  });
}

class LocationService {
  static const fallbackLat = 48.1351;
  static const fallbackLon = 11.5820;
  static const fallbackLabel = 'Upper Bavaria · Zone 7b';

  final _location = Location();

  Future<LocationResult> getCurrent() async {
    try {
      var serviceOn = await _location.serviceEnabled();
      if (!serviceOn) {
        serviceOn = await _location.requestService();
        if (!serviceOn) {
          return _fallback('Location services disabled');
        }
      }

      var permission = await _location.hasPermission();
      if (permission == PermissionStatus.denied) {
        permission = await _location.requestPermission();
      }
      if (permission != PermissionStatus.granted &&
          permission != PermissionStatus.grantedLimited) {
        return _fallback('Location permission denied');
      }

      _location.changeSettings(
        accuracy: LocationAccuracy.balanced,
        interval: 10000,
      );

      final data = await _location.getLocation().timeout(
            const Duration(seconds: 15),
          );
      final lat = data.latitude;
      final lon = data.longitude;
      if (lat == null || lon == null) {
        return _fallback('GPS returned no coordinates');
      }
      final name = await _reverseGeocode(lat, lon) ??
          '${lat.toStringAsFixed(4)}, ${lon.toStringAsFixed(4)}';
      return LocationResult(lat: lat, lon: lon, label: name);
    } catch (e) {
      return _fallback('GPS unavailable: $e');
    }
  }

  Future<String?> _reverseGeocode(double lat, double lon) async {
    try {
      final uri = Uri.parse(
        'https://api.bigdatacloud.net/data/reverse-geocode-client'
        '?latitude=$lat&longitude=$lon&localityLanguage=en',
      );
      final r = await http.get(uri).timeout(const Duration(seconds: 6));
      if (r.statusCode != 200) return null;
      final d = json.decode(r.body) as Map<String, dynamic>;
      final city = (d['city'] as String?)?.trim();
      final locality = (d['locality'] as String?)?.trim();
      final principal =
          (d['principalSubdivision'] as String?)?.trim();
      final country = (d['countryCode'] as String?)?.trim();
      final name = (city?.isNotEmpty == true
              ? city
              : locality?.isNotEmpty == true
                  ? locality
                  : principal) ??
          '';
      if (name.isEmpty) return null;
      return country != null && country.isNotEmpty
          ? '$name, $country'
          : name;
    } catch (_) {
      return null;
    }
  }

  LocationResult _fallback(String reason) => LocationResult(
        lat: fallbackLat,
        lon: fallbackLon,
        label: fallbackLabel,
        isFallback: true,
        errorMessage: reason,
      );
}
