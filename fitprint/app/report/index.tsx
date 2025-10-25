import React from "react";
import { View, Text, StyleSheet, ScrollView, Image, TouchableOpacity } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import * as Progress from "react-native-progress";
import { Leaf, Droplets, Factory, Users, Recycle, ArrowLeft } from "lucide-react-native";

export default function ReportScreen() {
  const { photoUri } = useLocalSearchParams<{ photoUri: string }>();

  // Mock data - replace with AI analysis
  const sustainabilityScore = 65;
  const metrics = [
    { 
        icon: Leaf, 
        label: "Material Origin", 
        value: "Organic Cotton", 
        score: 85, 
        description: "Made from organically grown cotton, reducing pesticide and fertilizer use." 
    },
    { 
        icon: Droplets, 
        label: "Water Usage", 
        value: "Moderate", 
        score: 60, 
        description: "Uses an average amount of water compared to conventional production." 
    },
    { 
        icon: Factory, 
        label: "Production Impact", 
        value: "Medium", 
        score: 55, 
        description: "Emissions and energy use are moderate; some room for improvement." 
    },
    { 
        icon: Users, 
        label: "Labor Ethics", 
        value: "Fair Trade", 
        score: 90, 
        description: "Workers receive fair wages and safe working conditions." 
    },
    { 
        icon: Recycle, 
        label: "Recyclability", 
        value: "High", 
        score: 75, 
        description: "Materials are mostly recyclable or biodegradable at end-of-life." 
    },
  ];

  const alternatives = [
    { brand: "Patagonia", item: "Organic Cotton T-Shirt", score: 92, price: "$45" },
    { brand: "Reformation", item: "Eco Denim Jeans", score: 88, price: "$128" },
    { brand: "Allbirds", item: "Wool Runners", score: 85, price: "$95" },
  ];

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: 40 }}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <ArrowLeft size={24} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Sustainability Report</Text>
      </View>

      <View style={styles.content}>
        {/* Photo */}
        {photoUri && (
          <Image source={{ uri: photoUri }} style={styles.photo} resizeMode="cover" />
        )}

        {/* Overall Score */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Overall Score: {sustainabilityScore}/100</Text>
          <Text style={styles.cardDescription}>
            {sustainabilityScore > 70
              ? "Great choice! This item has good sustainability credentials."
              : "This item has moderate environmental impact. Consider the alternatives below."}
          </Text>
          <Progress.Bar
            progress={sustainabilityScore / 100}
            width={null}
            height={12}
            color="#9E4784"
            borderRadius={6}
            style={{ marginTop: 10 }}
          />
        </View>

        {/* Metrics */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Sustainability Breakdown</Text>
          {metrics.map((metric, idx) => {
            const Icon = metric.icon;
            return (
              <View key={idx} style={styles.metricContainer}>
                <View style={styles.metricIcon}>
                  <Icon size={20} color="#37306B" />
                </View>
                <View style={{ flex: 1 }}>
                  <View style={styles.metricHeader}>
                    <Text style={styles.metricLabel}>{metric.label}</Text>
                    <Text style={styles.metricScore}>{metric.score}/100</Text>
                  </View>
                  <Text style={styles.metricValue}>{metric.value}</Text>
                  <Text style={styles.metricDescription}>{metric.description}</Text>
                  <Progress.Bar progress={metric.score / 100} width={null} height={8} color="#D27685" borderRadius={4} />
                </View>
              </View>
            );
          })}
        </View>

        {/* Alternatives */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Better Alternatives</Text>
          {alternatives.map((alt, idx) => (
            <View key={idx} style={styles.altContainer}>
              <View style={{ flex: 1 }}>
                <Text style={styles.altBrand}>{alt.brand}</Text>
                <Text style={styles.altItem}>{alt.item}</Text>
                <Text style={styles.altPrice}>{alt.price}</Text>
              </View>
              <View style={styles.altScoreContainer}>
                <Text style={styles.altScore}>{alt.score}/100</Text>
              </View>
            </View>
          ))}
        </View>

        {/* Scan Another Button */}
        <TouchableOpacity
          style={styles.scanButton}
          onPress={() => router.push("/capture")}
        >
          <Text style={styles.scanButtonText}>Scan Another Item</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#37306B" },
  header: {
    flexDirection: "row",
    alignItems: "center",
    padding: 20,
    backgroundColor: "#66347F",
  },
  backButton: { marginRight: 15 },
  headerTitle: { fontSize: 20, fontWeight: "700", color: "#fff" },
  content: { padding: 20 },
  photo: { width: "100%", height: 220, borderRadius: 16, marginBottom: 20 },
  card: { backgroundColor: "#66347F", padding: 15, borderRadius: 16, marginBottom: 20 },
  cardTitle: { fontSize: 18, fontWeight: "700", color: "#fff", marginBottom: 5 },
  cardDescription: { fontSize: 14, color: "#e0bcc1ff", marginBottom: 10 },
  metricContainer: { flexDirection: "row", alignItems: "center", marginBottom: 15 },
  metricIcon: {
    width: 40,
    height: 40,
    borderRadius: 10,
    backgroundColor: "#9E4784",
    alignItems: "center",
    justifyContent: "center",
    marginRight: 10,
  },
  metricHeader: { flexDirection: "row", justifyContent: "space-between", marginBottom: 2 },
  metricLabel: { fontWeight: "600", color: "#fff" },
  metricScore: { color: "#e0bcc1ff", fontWeight: "600" },
  metricValue: { color: "#fff", fontSize: 12, marginBottom: 4 },
  altContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
    padding: 12,
    borderRadius: 12,
    backgroundColor: "#9E4784",
    marginBottom: 10,
  },
  altBrand: { fontWeight: "700", color: "#fff" },
  altItem: { color: "#e0bcc1ff" },
  altPrice: { marginTop: 4, fontWeight: "600", color: "#fff" },
  altScoreContainer: {
    backgroundColor: "#37306B",
    borderRadius: 8,
    paddingHorizontal: 8,
    justifyContent: "center",
    alignItems: "center",
  },
  altScore: { color: "#fff", fontWeight: "700" },
  scanButton: {
    backgroundColor: "#9E4784",
    borderRadius: 12,
    paddingVertical: 14,
    marginTop: 10,
  },
  scanButtonText: { color: "#fff", fontWeight: "700", fontSize: 16, textAlign: "center" },
  metricDescription: {
    color: "#fff",
    fontSize: 12,
    marginBottom: 4,
    fontStyle: "italic", // optional for visual distinction
  },
});
