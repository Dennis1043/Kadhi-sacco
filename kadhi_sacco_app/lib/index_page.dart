import 'package:flutter/material.dart';
import 'members_page.dart';
import 'savings_page.dart';
import 'loans_page.dart';
import 'fines_page.dart';
import 'admin_summary_page.dart';

class IndexPage extends StatelessWidget {
  const IndexPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Kadhi Sacco")),
      body: GridView.count(
        crossAxisCount: 2,
        padding: const EdgeInsets.all(16),
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
        children: [
          _buildNavCard(context, "Members", const MembersPage()),
          _buildNavCard(context, "Savings", const SavingsPage()),
          _buildNavCard(context, "Loans", const LoansPage()),
          _buildNavCard(context, "Fines", const FinesPage()),
          _buildNavCard(context, "Admin Summary", const AdminSummaryPage()),
        ],
      ),
    );
  }

  Widget _buildNavCard(BuildContext context, String title, Widget page) {
    return GestureDetector(
      onTap: () {
        Navigator.push(context, MaterialPageRoute(builder: (_) => page));
      },
      child: Card(
        elevation: 4,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        child: Center(
          child: Text(title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        ),
      ),
    );
  }
}
