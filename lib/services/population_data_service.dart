import 'dart:convert';

import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;

import '../models/age_distribution.dart';
import '../utils/app_config.dart';

class PopulationDataService {
  const PopulationDataService();

  Future<AgeDistribution> loadAgeDistribution() async {
    final remoteUrl = AppConfig.ageDistributionUrl.trim();
    if (remoteUrl.isNotEmpty) {
      try {
        final response = await http.get(Uri.parse(remoteUrl));
        if (response.statusCode == 200) {
          final json = jsonDecode(response.body) as Map<String, dynamic>;
          return AgeDistribution.fromJson(json);
        }
      } catch (_) {
        // Fall back to local asset.
      }
    }

    final raw = await rootBundle.loadString(
      'assets/data/age_distribution.json',
    );
    final json = jsonDecode(raw) as Map<String, dynamic>;
    return AgeDistribution.fromJson(json);
  }
}
