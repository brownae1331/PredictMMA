import React from 'react';
import { View, Text, SafeAreaView } from 'react-native';

export default function HomeScreen() {
    return (
        <SafeAreaView className="flex-1 justify-center items-center bg-white">
            <Text className="text-2xl font-bold mb-2">Welcome Fighters</Text>
            <Text className="text-base text-gray-600">This is your fighters screen</Text>
        </SafeAreaView>
    );
}
