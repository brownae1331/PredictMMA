import { getAllPredictions } from '@/src/lib/api/predict_api';
import { PredictionOutPredict } from '@/src/types/predict_types';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { jwtDecode } from 'jwt-decode';
import React, { useCallback, useState } from 'react';
import { useFocusEffect } from '@react-navigation/native';
import { View, Text, StyleSheet, ActivityIndicator, ScrollView, TouchableOpacity, TextInput } from 'react-native';
import { Method } from '@/src/types/predict_types';

type TabType = 'predictions' | 'analytics';

export default function PredictScreen() {
    const [predictions, setPredictions] = useState<PredictionOutPredict[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedTab, setSelectedTab] = useState<TabType>('predictions');
    const [searchQuery, setSearchQuery] = useState('');

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

    const filteredPredictions = predictions.filter(prediction => {
        if (!searchQuery.trim()) return true;
        
        const query = searchQuery.toLowerCase();
        return (
            prediction.fighter_1_name.toLowerCase().includes(query) ||
            prediction.fighter_2_name.toLowerCase().includes(query) ||
            prediction.event_title.toLowerCase().includes(query) ||
            prediction.winner_name.toLowerCase().includes(query) ||
            prediction.method.toLowerCase().includes(query)
        );
    });

    const renderAnalytics = () => {
        if (loading) {
            return <ActivityIndicator size="large" color="#000" style={styles.loader} />;
        }
        
        if (error) {
            return <Text style={styles.errorText}>Error: {error}</Text>;
        }
        
        if (filteredPredictions.length === 0) {
            return <Text style={styles.welcomeSubtitle}>
                {searchQuery ? 'No predictions match your search.' : 'No predictions data available for analytics.'}
            </Text>;
        }

        const totalPredictions = filteredPredictions.length;
        const winCount = filteredPredictions.filter(p => p.result === 'win').length;
        const lossCount = filteredPredictions.filter(p => p.result === 'loss').length;
        const pendingCount = filteredPredictions.filter(p => p.result === 'pending').length;
        const accuracy = totalPredictions > 0 && (winCount + lossCount) > 0 ? 
            ((winCount / (winCount + lossCount)) * 100).toFixed(1) : '0.0';

        const methodStats = filteredPredictions.reduce((acc, pred) => {
            acc[pred.method] = (acc[pred.method] || 0) + 1;
            return acc;
        }, {} as Record<string, number>);

        return (
            <View style={styles.analyticsContainer}>
                <View style={styles.statsCard}>
                    <Text style={styles.cardTitle}>Overall Statistics</Text>
                    <View style={styles.statRow}>
                        <Text style={styles.statLabel}>Total Predictions:</Text>
                        <Text style={styles.statValue}>{totalPredictions}</Text>
                    </View>
                    <View style={styles.statRow}>
                        <Text style={styles.statLabel}>Accuracy:</Text>
                        <Text style={styles.statValue}>{accuracy}%</Text>
                    </View>
                    <View style={styles.statRow}>
                        <Text style={[styles.statLabel, styles.resultWin]}>Wins:</Text>
                        <Text style={[styles.statValue, styles.resultWin]}>{winCount}</Text>
                    </View>
                    <View style={styles.statRow}>
                        <Text style={[styles.statLabel, styles.resultLoss]}>Losses:</Text>
                        <Text style={[styles.statValue, styles.resultLoss]}>{lossCount}</Text>
                    </View>
                    <View style={styles.statRow}>
                        <Text style={[styles.statLabel, styles.resultPending]}>Pending:</Text>
                        <Text style={[styles.statValue, styles.resultPending]}>{pendingCount}</Text>
                    </View>
                </View>

                <View style={styles.statsCard}>
                    <Text style={styles.cardTitle}>Method Breakdown</Text>
                    {Object.entries(methodStats).map(([method, count]) => (
                        <View key={method} style={styles.statRow}>
                            <Text style={styles.statLabel}>{method === 'SUBMISSION' ? 'SUB' : method === 'DECISION' ? 'DEC' : method}:</Text>
                            <Text style={styles.statValue}>{count}</Text>
                        </View>
                    ))}
                </View>
            </View>
        );
    };

    return (
        <View style={styles.container}>
            {/* Header Banner */}
            <View style={styles.header}>
                <View style={styles.headerContent}>
                    <Text style={styles.headerText}>Predict</Text>
                </View>
            </View>

            {/* Tab Selector */}
            <View style={styles.tabContainer}>
                <TouchableOpacity 
                    style={[styles.tab, selectedTab === 'predictions' && styles.activeTab]}
                    onPress={() => setSelectedTab('predictions')}
                >
                    <Text style={[styles.tabText, selectedTab === 'predictions' && styles.activeTabText]}>
                        Predictions
                    </Text>
                </TouchableOpacity>
                <TouchableOpacity 
                    style={[styles.tab, selectedTab === 'analytics' && styles.activeTab]}
                    onPress={() => setSelectedTab('analytics')}
                >
                    <Text style={[styles.tabText, selectedTab === 'analytics' && styles.activeTabText]}>
                        Analytics
                    </Text>
                </TouchableOpacity>
            </View>

            {/* Search Bar - Only show on Predictions tab */}
            {selectedTab === 'predictions' && (
                <View style={styles.searchContainer}>
                    <TextInput
                        style={styles.searchInput}
                        placeholder="Search predictions..."
                        value={searchQuery}
                        onChangeText={setSearchQuery}
                        placeholderTextColor="#9ca3af"
                    />
                </View>
            )}

            {/* Main Content */}
            <ScrollView style={styles.scrollView}>
                <View style={styles.mainContent}>
                    {selectedTab === 'predictions' ? (
                        loading ? (
                            <ActivityIndicator size="large" color="#000" style={styles.loader} />
                        ) : error ? (
                            <Text style={styles.errorText}>Error: {error}</Text>
                        ) : filteredPredictions.length === 0 ? (
                            <Text style={styles.welcomeSubtitle}>
                                {searchQuery ? 'No predictions match your search.' : 'No predictions yet.'}
                            </Text>
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
                                {filteredPredictions.map((prediction, idx) => (
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
                                            {prediction.method === 'SUBMISSION' ? 'SUB' : prediction.method === 'DECISION' ? 'DEC' : prediction.method}{prediction.round ? ` R${prediction.round}` : ''}
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
                        )
                    ) : (
                        renderAnalytics()
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
    tabContainer: {
        flexDirection: 'row',
        backgroundColor: '#f8f9fa',
        marginHorizontal: 4,
        marginVertical: 8,
        borderRadius: 8,
        padding: 4,
    },
    tab: {
        flex: 1,
        paddingVertical: 8,
        paddingHorizontal: 16,
        borderRadius: 6,
        alignItems: 'center',
    },
    activeTab: {
        backgroundColor: '#fff',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.1,
        shadowRadius: 2,
        elevation: 2,
    },
    tabText: {
        fontSize: 14,
        fontWeight: '500',
        color: '#6c757d',
    },
    activeTabText: {
        color: '#000',
        fontWeight: '600',
    },
    analyticsContainer: {
        alignSelf: 'stretch',
        paddingHorizontal: 4,
    },
    statsCard: {
        backgroundColor: '#fff',
        marginVertical: 8,
        marginHorizontal: 4,
        borderRadius: 12,
        padding: 20,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.06,
        shadowRadius: 4,
        elevation: 2,
    },
    cardTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#222',
        marginBottom: 16,
        textAlign: 'center',
    },
    statRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingVertical: 8,
        borderBottomWidth: 1,
        borderBottomColor: '#f1f3f4',
    },
    statLabel: {
        fontSize: 16,
        color: '#495057',
        fontWeight: '500',
    },
    statValue: {
        fontSize: 16,
        color: '#212529',
        fontWeight: '600',
    },
    searchContainer: {
        marginHorizontal: 8,
        marginVertical: 8,
    },
    searchInput: {
        backgroundColor: '#fff',
        borderRadius: 8,
        paddingHorizontal: 16,
        paddingVertical: 12,
        fontSize: 16,
        borderWidth: 1,
        borderColor: '#e9ecef',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.05,
        shadowRadius: 2,
        elevation: 1,
    },
});