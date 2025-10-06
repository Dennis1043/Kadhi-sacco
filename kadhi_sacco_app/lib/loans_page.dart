import 'package:flutter/material.dart';

class LoansPage extends StatelessWidget {
  const LoansPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Loans")),
      body: const Center(
        child: Text("Loans Page", style: TextStyle(fontSize: 20)),
      ),
    );
  }
}
