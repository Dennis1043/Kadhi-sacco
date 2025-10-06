import 'package:flutter/material.dart';

class AdminSummaryPage extends StatelessWidget {
  const AdminSummaryPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Admin Summary")),
      body: const Center(
        child: Text("Admin Summary Page", style: TextStyle(fontSize: 20)),
      ),
    );
  }
}
