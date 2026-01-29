class AgeBucket {
  const AgeBucket({
    required this.minAge,
    required this.maxAge,
    required this.count,
  });

  final int minAge;
  final int maxAge;
  final double count;

  factory AgeBucket.fromJson(Map<String, dynamic> json) {
    return AgeBucket(
      minAge: json['min'] as int,
      maxAge: json['max'] as int,
      count: (json['count'] as num).toDouble(),
    );
  }
}

class AgeDistribution {
  const AgeDistribution({
    required this.buckets,
    this.deathsByAge,
    this.birthsPerYear,
  });

  final List<AgeBucket> buckets;
  final List<DeathBucket>? deathsByAge;
  final double? birthsPerYear;

  double get totalPopulation =>
      buckets.fold<double>(0.0, (sum, bucket) => sum + bucket.count);

  double get totalDeathsPerYear =>
      deathsByAge?.fold<double>(
        0.0,
        (sum, bucket) => sum + bucket.deathsPerYear,
      ) ??
      0.0;

  factory AgeDistribution.fromJson(Map<String, dynamic> json) {
    final bucketsJson = json['buckets'] as List<dynamic>;
    final buckets =
        bucketsJson
            .map((entry) => AgeBucket.fromJson(entry as Map<String, dynamic>))
            .toList();
    final deathsJson = json['deaths_by_age'] as List<dynamic>?;
    final deathsByAge =
        deathsJson
            ?.map(
              (entry) => DeathBucket.fromJson(entry as Map<String, dynamic>),
            )
            .toList();
    final birthsPerYear = (json['births_per_year'] as num?)?.toDouble();
    return AgeDistribution(
      buckets: buckets,
      deathsByAge: deathsByAge,
      birthsPerYear: birthsPerYear,
    );
  }
}

class DeathBucket {
  const DeathBucket({
    required this.minAge,
    required this.maxAge,
    required this.deathsPerYear,
  });

  final int minAge;
  final int maxAge;
  final double deathsPerYear;

  factory DeathBucket.fromJson(Map<String, dynamic> json) {
    return DeathBucket(
      minAge: json['min'] as int,
      maxAge: json['max'] as int,
      deathsPerYear: (json['deaths_per_year'] as num).toDouble(),
    );
  }
}
