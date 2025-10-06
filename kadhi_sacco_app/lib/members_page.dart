import 'package:flutter/material.dart';

class MembersPage extends StatelessWidget {
  const MembersPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Members")),
      body: const Center(
        child: Text("Members Page", style: TextStyle(fontSize: 20)),
      ),
    );
  }
}
