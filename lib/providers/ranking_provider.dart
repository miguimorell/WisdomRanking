import 'dart:async';

import 'package:flutter/foundation.dart';

import '../models/age_distribution.dart';
import '../services/population_data_service.dart';

class RankingProvider extends ChangeNotifier {
  RankingProvider() {
    _timer = Timer.periodic(const Duration(seconds: 1), (_) => _tick());
    _loadDistribution();
    _tick();
  }

  final DateTime _birthDate = DateTime(1997, 3, 9);
  double _totalPopulation = 8_100_000_000;

  final PopulationDataService _populationService =
      const PopulationDataService();
  AgeDistribution? _distribution;

  double birthsPerSecond = 4.3;
  double deathsPerSecond = 1.8;

  Timer? _timer;

  int get totalPopulation => _totalPopulation.floor();

  double get ageYears {
    final ageSeconds =
        DateTime.now().difference(_birthDate).inSeconds.toDouble();
    return ageSeconds / (365.25 * 24 * 60 * 60);
  }

  int get olderCount {
    final distribution = _distribution;
    if (distribution == null) {
      return _fallbackOlderCount();
    }

    final age = ageYears;
    double older = 0;
    for (final bucket in distribution.buckets) {
      if (age <= bucket.minAge) {
        older += bucket.count;
      } else if (age > bucket.maxAge) {
        continue;
      } else {
        final span = (bucket.maxAge - bucket.minAge + 1).toDouble();
        final olderSpan = (bucket.maxAge - age + 1).clamp(0.0, span);
        older += bucket.count * (olderSpan / span);
      }
    }
    final scale = _totalPopulation / distribution.totalPopulation;
    return (older * scale).floor();
  }

  int get youngerCount =>
      (_totalPopulation - olderCount - 1).clamp(0, double.infinity).floor();

  int get ranking => olderCount + 1;

  Future<void> _loadDistribution() async {
    try {
      _distribution = await _populationService.loadAgeDistribution();
      _totalPopulation = _distribution!.totalPopulation;
      if (_distribution!.birthsPerYear != null) {
        birthsPerSecond = _distribution!.birthsPerYear! / _secondsPerYear;
      }
      if (_distribution!.totalDeathsPerYear > 0) {
        deathsPerSecond = _distribution!.totalDeathsPerYear / _secondsPerYear;
      }
      notifyListeners();
    } catch (_) {
      // Keep fallback values if asset load fails.
    }
  }

  int _fallbackOlderCount() {
    const maxAge = 100.0;
    final value = (maxAge - ageYears) / maxAge;
    final percentOlder = value.clamp(0.0, 1.0);
    return (_totalPopulation * percentOlder).floor();
  }

  static const double _secondsPerYear = 365.25 * 24 * 60 * 60;

  void _tick() {
    _totalPopulation += birthsPerSecond - deathsPerSecond;
    notifyListeners();
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }
}
