import { getAllPredictions } from '@/src/lib/api/predict_api';
import { PredictionOutPredict } from '@/src/types/predict_types';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { jwtDecode } from 'jwt-decode';
import React, { useCallback, useState } from 'react';
import { useFocusEffect } from '@react-navigation/native';
import { View, Text, StyleSheet, ActivityIndicator, ScrollView } from 'react-native';
import { Image } from 'expo-image';
import { Method } from '@/src/types/predict_types';

export default function PredictScreen() {
    const [predictions, setPredictions] = useState<PredictionOutPredict[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useFocusEffect(
        useCallback(() => {
            fetchPredictions();
        }, [])
    );

    const fetchPredictions = async () => {
        try {
            setLoading(true);
            setError(null);

            const token = await AsyncStorage.getItem('access_token');
            if (!token) return;

            const decoded: any = jwtDecode(token);
            if (!decoded || !decoded.sub) return;

            const user_id = decoded.sub as number;

            const predictions = await getAllPredictions(user_id);
            setPredictions(predictions);
        } catch (error) {
            setError(error instanceof Error ? error.message : 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    return (
        <View style={styles.container}>
            {/* Header Banner */}
            <View style={styles.header}>
                <View style={styles.headerContent}>
                    <Text style={styles.headerText}>Predict</Text>
                </View>
            </View>

            {/* Main Content */}
            <ScrollView style={styles.scrollView}>
                <View style={styles.mainContent}>
                    {loading ? (
                        <ActivityIndicator size="large" color="#000" style={styles.loader} />
                    ) : error ? (
                        <Text style={styles.errorText}>Error: {error}</Text>
                    ) : predictions.length === 0 ? (
                        <Text style={styles.welcomeSubtitle}>No predictions yet.</Text>
                    ) : (
                        Object.entries(groupPredictionsByEvent(predictions)).map(([eventTitle, eventPredictions]) => (
                            <View key={eventTitle} style={styles.eventContainer}>
                                <Text style={styles.eventTitle}>{eventTitle}</Text>

                                {eventPredictions.map((prediction, idx) => (
                                    <View key={idx} style={styles.predictionContainer}>
                                        {/* Fight Text */}
                                        <Text style={styles.fightText}>{`${prediction.fighter_1_name} vs ${prediction.fighter_2_name}`}</Text>

                                        {/* Images Row */}
                                        <View style={styles.imagesRow}>
                                            {/* Winner Image */}
                                            <Image
                                                source={{ uri: prediction.winner_image }}
                                                style={styles.fighterImage}
                                                contentFit="cover"
                                                contentPosition="top"
                                            />

                                            {/* Method Image */}
                                            <Image
                                                source={methodImageMap[prediction.method]}
                                                style={styles.methodImage}
                                                contentFit="cover"
                                                contentPosition="center"
                                            />

                                            {/* Round Image (may be null for decision) */}
                                            {prediction.round !== null && (
                                                <Image
                                                    source={roundImageMap[prediction.round]}
                                                    style={styles.roundImage}
                                                    contentFit="cover"
                                                    contentPosition="center"
                                                />
                                            )}
                                        </View>
                                    </View>
                                ))}
                            </View>
                        ))
                    )}
                </View>
            </ScrollView>
        </View>
    );
}

const methodImageMap: Record<Method, any> = {
    [Method.KO]: require('../../../assets/images/punch.png'),
    [Method.SUBMISSION]: require('../../../assets/images/choke.png'),
    [Method.DECISION]: require('../../../assets/images/law.png'),
};

const roundImageMap: Record<number, any> = {
    1: require('../../../assets/images/one.png'),
    2: require('../../../assets/images/two.png'),
    3: require('../../../assets/images/three.png'),
    4: require('../../../assets/images/four.png'),
    5: require('../../../assets/images/five.png'),
};

function groupPredictionsByEvent(predictions: PredictionOutPredict[]): Record<string, PredictionOutPredict[]> {
    return predictions.reduce((acc, pred) => {
        if (!acc[pred.event_title]) {
            acc[pred.event_title] = [];
        }
        acc[pred.event_title].push(pred);
        return acc;
    }, {} as Record<string, PredictionOutPredict[]>);
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: 'light-grey',
    },
    header: {
        backgroundColor: 'white',
        padding: 10,
    },
    headerContent: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        marginTop: 50,
    },
    headerText: {
        color: 'black',
        fontWeight: 'bold',
        fontSize: 18,
    },
    mainContent: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        paddingHorizontal: 16,
    },
    welcomeTitle: {
        fontSize: 24,
        fontWeight: 'bold',
        marginBottom: 8,
    },
    welcomeSubtitle: {
        fontSize: 16,
        color: '#4b5563',
        textAlign: 'center',
    },
    loader: {
        marginTop: 20,
    },
    scrollView: {
        flex: 1,
    },
    errorText: {
        color: 'red',
        textAlign: 'center',
        marginTop: 20,
    },
    eventContainer: {
        alignSelf: 'stretch',
        backgroundColor: '#fff',
        marginVertical: 8,
        marginHorizontal: 16,
        borderRadius: 12,
        padding: 16,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.06,
        shadowRadius: 4,
        elevation: 2,
    },
    eventTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        marginBottom: 12,
        color: '#222',
        textAlign: 'center',
    },
    predictionContainer: {
        marginBottom: 16,
        alignItems: 'center',
    },
    fightText: {
        fontSize: 15,
        fontWeight: '500',
        marginBottom: 8,
        color: '#444',
        textAlign: 'center',
    },
    imagesRow: {
        flexDirection: 'row',
        justifyContent: 'center',
        alignItems: 'center',
    },
    fighterImage: {
        width: 70,
        height: 70,
        borderRadius: 35,
        marginHorizontal: 8,
        backgroundColor: '#fafafa',
        borderWidth: 2,
        borderColor: '#e0e0e0',
    },
    methodImage: {
        width: 70,
        height: 70,
        borderRadius: 35,
        marginHorizontal: 8,
        backgroundColor: '#fafafa',
        borderWidth: 2,
        borderColor: '#e0e0e0',
    },
    roundImage: {
        width: 70,
        height: 70,
        borderRadius: 35,
        marginHorizontal: 8,
        backgroundColor: '#fafafa',
        borderWidth: 2,
        borderColor: '#e0e0e0',
    },
});