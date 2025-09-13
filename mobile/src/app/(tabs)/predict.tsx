import { getAllPredictions } from '@/src/lib/api/predict_api';
import { PredictionOutPredict } from '@/src/types/predict_types';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { jwtDecode } from 'jwt-decode';
import React, { useCallback, useState } from 'react';
import { useFocusEffect } from '@react-navigation/native';
import { View, Text, StyleSheet, ActivityIndicator, ScrollView } from 'react-native';
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
                        <View style={styles.tableContainer}>
                            {/* Table Header */}
                            <View style={styles.tableHeader}>
                                <Text style={[styles.headerCell, styles.fightColumn]}>Fight</Text>
                                <Text style={[styles.headerCell, styles.eventColumn]}>Event</Text>
                                <Text style={[styles.headerCell, styles.predictionColumn]}>Prediction</Text>
                                <Text style={[styles.headerCell, styles.methodColumn]}>Method</Text>
                                <Text style={[styles.headerCell, styles.resultColumn]}>Status</Text>
                            </View>

                            {/* Table Body */}
                            {predictions.map((prediction, idx) => (
                                <View key={idx} style={[styles.tableRow, idx % 2 === 0 && styles.evenRow]}>
                                    <Text style={[styles.tableCell, styles.fightColumn]} numberOfLines={2}>
                                        {`${prediction.fighter_1_name} vs ${prediction.fighter_2_name}`}
                                    </Text>
                                    <Text style={[styles.tableCell, styles.eventColumn]} numberOfLines={2}>
                                        {prediction.event_title.split(' - ')[0]}
                                    </Text>
                                    <Text style={[styles.tableCell, styles.predictionColumn]} numberOfLines={2}>
                                        {prediction.winner_name}
                                    </Text>
                                    <Text style={[styles.tableCell, styles.methodColumn]} numberOfLines={2}>
                                        {prediction.method}{prediction.round ? ` R${prediction.round}` : ''}
                                    </Text>
                                    <Text style={[
                                        styles.tableCell,
                                        styles.resultColumn,
                                        styles.resultText,
                                        prediction.result === 'win' && styles.resultWin,
                                        prediction.result === 'loss' && styles.resultLoss,
                                        prediction.result === 'pending' && styles.resultPending
                                    ]}>
                                        {prediction.result === 'win' ? 'W' : prediction.result === 'loss' ? 'L' : 'P'}
                                    </Text>
                                </View>
                            ))}
                        </View>
                    )}
                </View>
            </ScrollView>
        </View>
    );
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
        paddingHorizontal: 4,
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
    tableContainer: {
        alignSelf: 'stretch',
        backgroundColor: '#fff',
        marginVertical: 8,
        marginHorizontal: 4,
        borderRadius: 8,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.06,
        shadowRadius: 4,
        elevation: 2,
        overflow: 'hidden',
    },
    tableHeader: {
        flexDirection: 'row',
        backgroundColor: '#f8f9fa',
        paddingVertical: 10,
        paddingHorizontal: 6,
        borderBottomWidth: 2,
        borderBottomColor: '#dee2e6',
    },
    headerCell: {
        fontSize: 13,
        fontWeight: 'bold',
        color: '#495057',
        textAlign: 'center',
        paddingHorizontal: 2,
    },
    tableRow: {
        flexDirection: 'row',
        paddingVertical: 8,
        paddingHorizontal: 6,
        borderBottomWidth: 1,
        borderBottomColor: '#e9ecef',
        minHeight: 45,
        alignItems: 'center',
    },
    evenRow: {
        backgroundColor: '#f8f9fa',
    },
    tableCell: {
        fontSize: 12,
        color: '#212529',
        textAlign: 'center',
        paddingHorizontal: 1,
        flexWrap: 'wrap',
    },
    fightColumn: {
        flex: 3.5,
    },
    eventColumn: {
        flex: 3,
    },
    predictionColumn: {
        flex: 2.5,
    },
    methodColumn: {
        flex: 1.8,
    },
    resultColumn: {
        flex: 1.5,
    },
    resultText: {
        fontWeight: 'bold',
        fontSize: 12,
    },
    resultWin: {
        color: '#28a745',
    },
    resultLoss: {
        color: '#dc3545',
    },
    resultPending: {
        color: '#ffc107',
    },
});