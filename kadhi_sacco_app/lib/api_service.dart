import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  final String baseUrl = "http://10.0.2.2:5000"; 
  // Use 10.0.2.2 if running on Android emulator
  // Use your PC's IP if testing on real phone

  Future<int> fetchMembers() async {
    final response = await http.get(Uri.parse("$baseUrl/members"));
    if (response.statusCode == 200) {
      return jsonDecode(response.body)["total_members"];
    } else {
      throw Exception("Failed to load members");
    }
  }

  Future<double> fetchSavings() async {
    final response = await http.get(Uri.parse("$baseUrl/savings"));
    if (response.statusCode == 200) {
      return (jsonDecode(response.body)["total_savings"] ?? 0).toDouble();
    } else {
      throw Exception("Failed to load savings");
    }
  }

  Future<int> fetchLoans() async {
    final response = await http.get(Uri.parse("$baseUrl/loans"));
    if (response.statusCode == 200) {
      return jsonDecode(response.body)["active_loans"];
    } else {
      throw Exception("Failed to load loans");
    }
  }

  Future<int> fetchFines() async {
    final response = await http.get(Uri.parse("$baseUrl/fines"));
    if (response.statusCode == 200) {
      return jsonDecode(response.body)["fines"];
    } else {
      throw Exception("Failed to load fines");
    }
  }
}
