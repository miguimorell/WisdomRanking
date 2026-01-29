import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/ranking_provider.dart';
import '../providers/theme_provider.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final rankingProvider = context.watch<RankingProvider>();
    return Scaffold(
      appBar: AppBar(
        title: const Text('Wisdom Ranking'),
        actions: [
          Switch.adaptive(
            value: context.watch<ThemeProvider>().isDarkMode,
            onChanged: (value) {
              context.read<ThemeProvider>().toggleMode(value);
            },
          ),
          const SizedBox(width: 12),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            const Spacer(),
            Text(
              '${rankingProvider.ranking}',
              style: Theme.of(
                context,
              ).textTheme.displayLarge?.copyWith(fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 8),
            Text(
              'Tu ranking de vejez en el mundo',
              style: Theme.of(context).textTheme.titleMedium,
              textAlign: TextAlign.center,
            ),
            const Spacer(),
            _StatLine(
              label: 'Población total',
              value: rankingProvider.totalPopulation,
            ),
            const SizedBox(height: 8),
            _StatLine(
              label: 'Mayores que yo',
              value: rankingProvider.olderCount,
            ),
            const SizedBox(height: 8),
            _StatLine(
              label: 'Menores que yo',
              value: rankingProvider.youngerCount,
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }
}

class _StatLine extends StatelessWidget {
  const _StatLine({required this.label, required this.value});

  final String label;
  final int value;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: Theme.of(context).textTheme.bodyMedium),
        Text(
          value.toString(),
          style: Theme.of(
            context,
          ).textTheme.bodyLarge?.copyWith(fontWeight: FontWeight.w600),
        ),
      ],
    );
  }
}
