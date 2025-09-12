import { Stack } from "expo-router";

export default function RootLayout() {
  return (
    <Stack>
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      <Stack.Screen name="(auth)" options={{ headerShown: false }} />
      <Stack.Screen name="event-fights" options={{ headerShown: false }} />
      <Stack.Screen name="make-prediction" options={{ headerShown: false }} />
      <Stack.Screen name="fighter-detail" options={{ headerShown: false }} />
    </Stack>
  );
}
