import React, { useState, useEffect } from "react";
import { View, Text, StyleSheet, ScrollView, Image, TouchableOpacity, ActivityIndicator, Linking } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import * as Progress from "react-native-progress";
import { Leaf, Droplets, Factory, Users, Recycle, ArrowLeft } from "lucide-react-native";
import { OutfitAnalysisResponse, apiService } from "../services/api";

export default function ReportScreen() {
  const { photoUri, analysisData } = useLocalSearchParams<{ 
    photoUri: string; 
    analysisData?: string; 
  }>();
  
  const [analysis, setAnalysis] = useState<OutfitAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    console.log("Report screen - analysisData:", analysisData);
    if (analysisData) {
      try {
        // Check if it's already an object or needs parsing
        const parsedData = typeof analysisData === 'string' ? JSON.parse(analysisData) : analysisData;
        console.log("Report screen - parsed data:", parsedData);
        setAnalysis(parsedData);
      } catch (error) {
        console.error("Error parsing analysis data:", error);
        // If parsing fails, try to use the data as-is
        console.log("Trying to use data as-is:", analysisData);
        if (typeof analysisData === 'object') {
          setAnalysis(analysisData);
        }
      }
    }
  }, [analysisData]);

  console.log("Current analysis state:", analysis);
  
  if (!analysis) {
    console.log("No analysis data, showing loading screen");
    return (
      <View style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <ArrowLeft size={24} color="#fff" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Loading Analysis...</Text>
        </View>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#9E4784" />
          <Text style={styles.loadingText}>Analyzing your clothing...</Text>
        </View>
      </View>
    );
  }

  const { sustainability_report, alternatives, clothing_item } = analysis;
  console.log("Rendering report with data:", { sustainability_report, alternatives, clothing_item });
  console.log("Sustainability report overall_score:", sustainability_report.overall_score, typeof sustainability_report.overall_score);
  console.log("Number of alternatives:", alternatives.length);
  alternatives.forEach((alt, idx) => {
    console.log(`Alternative ${idx + 1}:`, {
      name: alt.name,
      brand: alt.brand,
      image_url: alt.image_url,
      link: alt.link,
      why_sustainable: alt.why_sustainable
    });
  });
  const overallScore = Math.round(Number(sustainability_report.overall_score) * 20); // Convert to 0-100 scale
  console.log("Overall score calculated:", overallScore);

  const metrics = [
    { 
      icon: Leaf, 
      label: "Material Origin", 
      score: Number(sustainability_report.categories.material_origin.score) * 20,
      description: sustainability_report.categories.material_origin.description
    },
    { 
      icon: Droplets, 
      label: "Production Impact", 
      score: Number(sustainability_report.categories.production_impact.score) * 20,
      description: sustainability_report.categories.production_impact.description
    },
    { 
      icon: Factory, 
      label: "Labor Ethics", 
      score: Number(sustainability_report.categories.labor_ethics.score) * 20,
      description: sustainability_report.categories.labor_ethics.description
    },
    { 
      icon: Users, 
      label: "End of Life", 
      score: Number(sustainability_report.categories.end_of_life.score) * 20,
      description: sustainability_report.categories.end_of_life.description
    },
    { 
      icon: Recycle, 
      label: "Brand Transparency", 
      score: Number(sustainability_report.categories.brand_transparency.score) * 20,
      description: sustainability_report.categories.brand_transparency.description
    },
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

        {/* Brand Info */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Brand: {sustainability_report.brand}</Text>
          <Text style={styles.cardDescription}>{sustainability_report.overall_description}</Text>
        </View>

        {/* Overall Score */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Overall Score: {overallScore}/100</Text>
          <Text style={styles.cardDescription}>
            {overallScore > 70
              ? "Great choice! This item has good sustainability credentials."
              : "This item has moderate environmental impact. Consider the alternatives below."}
          </Text>
          <Progress.Bar
            progress={overallScore / 100}
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
                  <Text style={styles.metricDescription}>{metric.description}</Text>
                  <Progress.Bar progress={metric.score / 100} width={null} height={8} color="#D27685" borderRadius={4} />
                </View>
              </View>
            );
          })}
        </View>

        {/* Regional Alerts */}
        {Object.values(sustainability_report.regional_alerts).some(alert => alert) && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Regional Compliance Alerts</Text>
            {Object.entries(sustainability_report.regional_alerts).map(([region, alert]) => 
              alert ? (
                <View key={region} style={styles.alertContainer}>
                  <Text style={styles.alertRegion}>{region}:</Text>
                  <Text style={styles.alertText}>{alert}</Text>
                </View>
              ) : null
            )}
          </View>
        )}

        {/* Alternatives */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Better Alternatives</Text>
          {alternatives.map((alt, idx) => (
            <View key={idx} style={styles.altContainer}>
              {alt.image_url && (
                <Image 
                  source={{ uri: alt.image_url }} 
                  style={styles.altImage}
                  resizeMode="cover"
                  onLoad={() => console.log(`Image loaded: ${alt.name}`)}
                  onError={(e) => console.log(`Image failed to load for ${alt.name}:`, e.nativeEvent.error)}
                />
              )}
              <View style={{ flex: 1 }}>
                <Text style={styles.altBrand}>{alt.brand}</Text>
                <Text style={styles.altItem}>{alt.name}</Text>
                <Text style={styles.altDescription}>{alt.why_sustainable}</Text>
                {alt.link && (
                  <TouchableOpacity 
                    onPress={() => {
                      console.log("Opening link:", alt.link);
                      Linking.openURL(alt.link).catch(err => console.error("Failed to open link:", err));
                    }}
                    style={styles.altLinkButton}
                  >
                    <Text style={styles.altLink}>🔗 View Product</Text>
                  </TouchableOpacity>
                )}
              </View>
              <View style={styles.altScoreContainer}>
                <Text style={styles.altScore}>{Math.round(Number(alt.sustainability_score) * 20)}/100</Text>
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
    alignItems: "center",
    padding: 12,
    borderRadius: 12,
    backgroundColor: "#9E4784",
    marginBottom: 10,
  },
  altImage: {
    width: 60,
    height: 60,
    borderRadius: 8,
    marginRight: 12,
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
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    color: '#fff',
    fontSize: 16,
    marginTop: 10,
  },
  alertContainer: {
    marginBottom: 10,
    padding: 10,
    backgroundColor: '#9E4784',
    borderRadius: 8,
  },
  alertRegion: {
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 5,
  },
  alertText: {
    color: '#fff',
    fontSize: 12,
  },
  altDescription: {
    color: '#e0bcc1ff',
    fontSize: 12,
    marginTop: 4,
    marginBottom: 8,
  },
  altLinkButton: {
    marginTop: 4,
    paddingVertical: 6,
    paddingHorizontal: 10,
    backgroundColor: '#37306B',
    borderRadius: 6,
    alignSelf: 'flex-start',
  },
  altLink: {
    color: '#fff',
    fontSize: 13,
    fontWeight: '600',
  },
});
