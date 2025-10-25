import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  ActivityIndicator,
  Platform,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { router } from "expo-router";
import * as WebBrowser from "expo-web-browser";
import * as Google from "expo-auth-session/providers/google";
import Constants from "expo-constants";
import { makeRedirectUri } from "expo-auth-session";

WebBrowser.maybeCompleteAuthSession();

type ExpoExtra = {
  googleAndroidClientId?: string;
  googleIosClientId?: string;
  googleWebClientId?: string;
  backendBaseUrl?: string;
  expoAuthRedirect?: string;
};

type ResolvedExtra = {
  googleAndroidClientId?: string;
  googleIosClientId?: string;
  googleWebClientId: string;
  backendBaseUrl: string;
  expoAuthRedirect?: string;
};
const FALLBACK_BACKEND_BASE_URL = "http://localhost:8000";
const FALLBACK_EXPO_AUTH_REDIRECT = "https://auth.expo.io/@rainsuds/fitprint";

const sanitizeBaseUrl = (value: string) => value.replace(/\/$/, "");

export default function LoginScreen() {
  const configExtra = Constants.expoConfig?.extra as ExpoExtra | undefined;
  const legacyExtra = (Constants as any).manifest?.extra as ExpoExtra | undefined; // eslint-disable-line @typescript-eslint/no-explicit-any
  const manifest2Extra = ((Constants as any).manifest2?.extra ?? {}) as ExpoExtra;

  const extra = useMemo<ExpoExtra>(() => {
    return {
      ...legacyExtra,
      ...manifest2Extra,
      ...configExtra,
      googleAndroidClientId:
        configExtra?.googleAndroidClientId ??
        manifest2Extra.googleAndroidClientId ??
        legacyExtra?.googleAndroidClientId ??
        process.env.EXPO_PUBLIC_GOOGLE_ANDROID_CLIENT_ID,
      googleIosClientId:
        configExtra?.googleIosClientId ??
        manifest2Extra.googleIosClientId ??
        legacyExtra?.googleIosClientId ??
        process.env.EXPO_PUBLIC_GOOGLE_IOS_CLIENT_ID,
      googleWebClientId:
        configExtra?.googleWebClientId ??
        manifest2Extra.googleWebClientId ??
        legacyExtra?.googleWebClientId ??
        process.env.EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID,
      backendBaseUrl:
        configExtra?.backendBaseUrl ??
        manifest2Extra.backendBaseUrl ??
        legacyExtra?.backendBaseUrl ??
        process.env.EXPO_PUBLIC_BACKEND_BASE_URL ??
        FALLBACK_BACKEND_BASE_URL,
      expoAuthRedirect:
        configExtra?.expoAuthRedirect ??
        manifest2Extra.expoAuthRedirect ??
        legacyExtra?.expoAuthRedirect ??
        process.env.EXPO_PUBLIC_EXPO_AUTH_REDIRECT ??
        FALLBACK_EXPO_AUTH_REDIRECT,
    };
  }, [configExtra, legacyExtra, manifest2Extra]);

  useEffect(() => {
    console.log("Expo extra sources", {
      platform: Platform.OS,
      configExtra,
      legacyExtra,
      manifest2Extra,
      env: {
        EXPO_PUBLIC_GOOGLE_ANDROID_CLIENT_ID: process.env.EXPO_PUBLIC_GOOGLE_ANDROID_CLIENT_ID,
        EXPO_PUBLIC_GOOGLE_IOS_CLIENT_ID: process.env.EXPO_PUBLIC_GOOGLE_IOS_CLIENT_ID,
        EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID: process.env.EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID,
        EXPO_PUBLIC_BACKEND_BASE_URL: process.env.EXPO_PUBLIC_BACKEND_BASE_URL,
      },
      combinedExtra: extra,
    });
  }, [configExtra, legacyExtra, manifest2Extra, extra]);

  const { resolvedExtra, missingClientIds } = useMemo(() => {
    const missing: string[] = [];
    if (!extra.googleWebClientId) {
      missing.push("googleWebClientId");
    }
    if (Platform.OS === "android" && !extra.googleAndroidClientId) {
      missing.push("googleAndroidClientId");
    }
    if (Platform.OS === "ios" && !extra.googleIosClientId) {
      missing.push("googleIosClientId");
    }

    if (missing.length > 0) {
      return {
        resolvedExtra: null,
        missingClientIds: missing,
      };
    }

    return {
      resolvedExtra: {
        googleAndroidClientId: extra.googleAndroidClientId,
        googleIosClientId: extra.googleIosClientId,
        googleWebClientId: extra.googleWebClientId!,
        backendBaseUrl: sanitizeBaseUrl(extra.backendBaseUrl ?? FALLBACK_BACKEND_BASE_URL),
        expoAuthRedirect: extra.expoAuthRedirect,
      },
      missingClientIds: missing,
    };
  }, [
    extra.backendBaseUrl,
    extra.expoAuthRedirect,
    extra.googleAndroidClientId,
    extra.googleIosClientId,
    extra.googleWebClientId,
  ]);

  useEffect(() => {
    if (missingClientIds.length > 0) {
      console.error(
        `Google OAuth client IDs are missing: ${missingClientIds.join(", ")}. Define them in app.json 'extra' or EXPO_PUBLIC environment variables, then restart Expo.`
      );
    }
  }, [missingClientIds]);

  if (!resolvedExtra) {
    return (
      <View style={styles.container}>
        <Text style={styles.title}>FitPrint</Text>
        <Text style={styles.configurationWarning}>
          Configure Google OAuth client IDs before attempting to sign in.
          {missingClientIds.length ? ` Missing: ${missingClientIds.join(", ")}.` : ""}
        </Text>
      </View>
    );
  }

  return <ConfiguredLoginScreen extra={resolvedExtra} />;
}

function ConfiguredLoginScreen({ extra }: { extra: ResolvedExtra }) {
  const [isLoading, setIsLoading] = useState(false);
  const [authMode, setAuthMode] = useState<"login" | "signup" | null>(null);

  const redirectUri = useMemo(() => {
    if (Platform.OS === "web") {
      if (extra.expoAuthRedirect && !extra.expoAuthRedirect.includes("auth.expo.io")) {
        return extra.expoAuthRedirect;
      }

      return makeRedirectUri();
    }

    return (
      extra.expoAuthRedirect ??
      makeRedirectUri({
        scheme: Array.isArray(Constants.expoConfig?.scheme)
          ? Constants.expoConfig?.scheme?.[0]
          : Constants.expoConfig?.scheme ?? "fitprint",
      })
    );
  }, [extra.expoAuthRedirect]);

  const authRequestConfig = useMemo(
    () => ({
      clientId: extra.googleWebClientId,
      webClientId: extra.googleWebClientId,
      redirectUri,
      scopes: ["profile", "email"],
      responseType: "id_token" as const,
      ...(extra.googleAndroidClientId ? { androidClientId: extra.googleAndroidClientId } : {}),
      ...(extra.googleIosClientId ? { iosClientId: extra.googleIosClientId } : {}),
    }),
    [extra.googleAndroidClientId, extra.googleIosClientId, extra.googleWebClientId, redirectUri]
  );

  const [request, response, promptAsync] = Google.useAuthRequest(authRequestConfig);

  useEffect(() => {
    console.log("Google redirect URI", redirectUri);
  }, [redirectUri]);

  useEffect(() => {
    const handleAuthResponse = async () => {
      if (!authMode || !response) {
        return;
      }

      if (response.type !== "success") {
        console.warn("Google auth response", response);
        if (response.type === "error") {
          Alert.alert(
            "Login failed",
            response.error?.message ?? "Google sign-in was cancelled or failed."
          );
        }
        setIsLoading(false);
        setAuthMode(null);
        return;
      }

      const idToken = response.authentication?.idToken ?? (response.params as Record<string, string>)?.id_token;
      if (!idToken) {
        setIsLoading(false);
        setAuthMode(null);
        Alert.alert("Login failed", "Google response did not include an ID token.");
        return;
      }

      try {
        let result: Response;

        if (authMode === "login") {
          result = await fetch(`${extra.backendBaseUrl}/auth/me`, {
            method: "GET",
            headers: {
              Authorization: `Bearer ${idToken}`,
            },
          });

          if (result.status === 404) {
            result = await fetch(`${extra.backendBaseUrl}/auth/google`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ id_token: idToken }),
            });
          }
        } else {
          result = await fetch(`${extra.backendBaseUrl}/auth/google`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id_token: idToken }),
          });
        }

        if (!result.ok) {
          const errorPayload = await result.text();
          throw new Error(`Backend rejected Google auth (${result.status}): ${errorPayload}`);
        }

        const user = await result.json();
        console.log(`${authMode.toUpperCase()} user`, user);
        router.replace("/capture" as never);
      } catch (error) {
        console.error("Google sign-in failed", error);
        Alert.alert(
          "Login failed",
          error instanceof Error ? error.message : "Could not authenticate with the Fitprint server."
        );
      } finally {
        setIsLoading(false);
        setAuthMode(null);
      }
    };

    void handleAuthResponse();
  }, [authMode, extra.backendBaseUrl, response]);

  const handleGoogleLogin = async (mode: "login" | "signup") => {
    if (!request) {
      Alert.alert("Not ready", "Google login is still configuring. Please try again in a moment.");
      return;
    }

    setAuthMode(mode);
    setIsLoading(true);
    const promptResult = await promptAsync();
    console.log("Google prompt result", promptResult);
    if (!promptResult || promptResult.type !== "success") {
      setIsLoading(false);
      setAuthMode(null);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>FitPrint</Text>
      <View style={styles.buttonGroup}>
        <TouchableOpacity
          style={[styles.button, styles.googleButton, request ? null : styles.buttonDisabled]}
          disabled={!request || isLoading}
          onPress={() => handleGoogleLogin("login")}
        >
          {isLoading && authMode === "login" ? (
            <ActivityIndicator color="#37306B" />
          ) : (
            <Text style={[styles.buttonText, styles.googleButtonText]}>Log In with Google</Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, styles.googleButton, request ? null : styles.buttonDisabled]}
          disabled={!request || isLoading}
          onPress={() => handleGoogleLogin("signup")}
        >
          {isLoading && authMode === "signup" ? (
            <ActivityIndicator color="#37306B" />
          ) : (
            <Text style={[styles.buttonText, styles.googleButtonText]}>Sign Up with Google</Text>
          )}
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#37306B", justifyContent: "center", padding: 30 },
  title: { color: "white", fontSize: 36, textAlign: "center", marginBottom: 40 },
  configurationWarning: { color: "white", fontSize: 16, textAlign: "center" },
  buttonGroup: { gap: 16 },
  button: {
    padding: 14,
    borderRadius: 8,
    alignItems: "center",
    justifyContent: "center",
    minHeight: 52,
  },
  googleButton: { backgroundColor: "#fff" },
  googleButtonText: { color: "#37306B" },
  buttonText: { fontSize: 18, textAlign: "center" },
  buttonDisabled: { opacity: 0.6 },
});
