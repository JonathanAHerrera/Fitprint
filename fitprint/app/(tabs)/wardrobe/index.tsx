import { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  Image,
  TouchableOpacity,
  Modal,
  Alert,
  Dimensions,
} from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import DraggableFlatList, { RenderItemParams } from "react-native-draggable-flatlist";

const WARDROBE_KEY = "WARDROBE_IMAGES";

export default function WardrobeScreen() {
  const [images, setImages] = useState<string[]>([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);

  useEffect(() => {
    loadWardrobe();
  }, []);

  const loadWardrobe = async () => {
    try {
      const stored = await AsyncStorage.getItem(WARDROBE_KEY);
      if (stored) setImages(JSON.parse(stored));
    } catch (err) {
      console.error("Failed to load wardrobe:", err);
    }
  };

  const saveWardrobe = async (newImages: string[]) => {
    setImages(newImages);
    await AsyncStorage.setItem(WARDROBE_KEY, JSON.stringify(newImages));
  };

  const deleteImage = (uri: string) => {
    Alert.alert("Delete Image", "Are you sure you want to remove this item?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Delete",
        style: "destructive",
        onPress: async () => {
          const updated = images.filter((i) => i !== uri);
          await saveWardrobe(updated);
          setModalVisible(false);
        },
      },
    ]);
  };

  const renderItem = ({ item, drag, isActive }: RenderItemParams<string>) => (
    <TouchableOpacity
      style={[styles.imageContainer, isActive && { opacity: 0.8 }]}
      onPress={() => {
        setSelectedImage(item);
        setModalVisible(true);
      }}
      onLongPress={drag}
    >
      <Image source={{ uri: item }} style={styles.image} />
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>My Wardrobe</Text>
      {images.length === 0 ? (
        <Text style={styles.emptyText}>No items yet. Add some from Capture!</Text>
      ) : (
        <DraggableFlatList
          data={images}
          keyExtractor={(item) => item}
          renderItem={renderItem}
          numColumns={2}
          onDragEnd={({ data }) => saveWardrobe(data)}
          contentContainerStyle={{ paddingBottom: 20 }}
        />
      )}

      {/* Full-screen Modal */}
      <Modal visible={modalVisible} transparent={true}>
        <View style={styles.modalBackground}>
          <Image source={{ uri: selectedImage! }} style={styles.fullImage} />
          <View style={styles.modalButtons}>
            <TouchableOpacity
              style={[styles.button, { backgroundColor: "#9E4784" }]}
              onPress={() => setModalVisible(false)}
            >
              <Text style={styles.buttonText}>Close</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.button, { backgroundColor: "#D27685" }]}
              onPress={() => selectedImage && deleteImage(selectedImage)}
            >
              <Text style={styles.buttonText}>Delete</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const { width } = Dimensions.get("window");
const IMAGE_SIZE = width / 2 - 30;

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: "#37306B" },
  title: {
    fontSize: 28,
    fontWeight: "700",
    color: "white",
    marginBottom: 20,
    textAlign: "center",
  },
  emptyText: { color: "#D27685", textAlign: "center", marginTop: 50 },
  imageContainer: { marginBottom: 15, width: IMAGE_SIZE, height: IMAGE_SIZE },
  image: { width: "100%", height: "100%", borderRadius: 12 },
  modalBackground: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.95)",
    justifyContent: "center",
    alignItems: "center",
    padding: 20,
  },
  fullImage: { width: "100%", height: "70%", borderRadius: 12, marginBottom: 20 },
  modalButtons: { flexDirection: "row", gap: 20 },
  button: { padding: 14, borderRadius: 12, alignItems: "center", flex: 1 },
  buttonText: { color: "white", fontWeight: "600", fontSize: 16, textAlign: "center" },
});
