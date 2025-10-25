import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import { router } from "expo-router";

export default function ReportScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Sustainability Report</Text>

      <Text style={styles.body}>
        Material: Organic Cotton {"\n"}
        Production Impact: Low Water Usage {"\n"}
        Labor Ethics: Fair Trade Certified
      </Text>

      <TouchableOpacity style={styles.button} onPress={() => router.push("/wardrobe")}>
        <Text style={styles.buttonText}>Save to Wardrobe</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { padding: 20 },
  title: { fontSize: 26, marginBottom: 15 },
  body: { fontSize: 16, marginBottom: 20 },
  button: { backgroundColor: "#9E4784", padding: 14, borderRadius: 8 },
  buttonText: { color: "white", textAlign: "center" }
});
