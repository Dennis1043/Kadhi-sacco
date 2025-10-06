import 'package:flutter/material.dart';

class FinesPage extends StatelessWidget {
  const FinesPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Fines")),
      body: const Center(
        child: Text("Fines Page", style: TextStyle(fontSize: 20)),
      ),
    );
  }
}
