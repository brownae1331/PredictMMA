import { getAllPredictions } from '@/src/lib/api/predict_api';
import { PredictionOutPredict } from '@/src/types/predict_types';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { jwtDecode } from 'jwt-decode';
import React, { useCallback, useState, useMemo } from 'react';
import { useFocusEffect } from '@react-navigation/native';
import { View, Text, StyleSheet, ActivityIndicator, ScrollView, TouchableOpacity, TextInput } from 'react-native';
import { formatFighterName } from '@/src/lib/utils/uiUtils';

type TabType = 'predictions' | 'analytics';
type FilterType = 'all' | 'correct' | 'wrong' | 'pending';
type SortType = 'date-desc' | 'date-asc';

export default function PredictScreen() {
    const [predictions, setPredictions] = useState<PredictionOutPredict[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedTab, setSelectedTab] = useState<TabType>('predictions');
    const [searchQuery, setSearchQuery] = useState('');
    const [filterType, setFilterType] = useState<FilterType>('all');
    const [sortType, setSortType] = useState<SortType>('date-desc');
    const [showFilterOptions, setShowFilterOptions] = useState(false);
    const [showSortOptions, setShowSortOptions] = useState(false);

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

    const filteredPredictions = useMemo(() => {
        let filtered = [...predictions];
        
        // Apply filter by prediction status
        if (filterType !== 'all') {
            filtered = filtered.filter(prediction => {
                if (filterType === 'pending') {
                    return !prediction.result;
                } else if (filterType === 'correct') {
                    return prediction.result && prediction.result.fighter;
                } else if (filterType === 'wrong') {
                    return prediction.result && !prediction.result.fighter;
                }
                return true;
            });
        }
        
        // Apply search filter
        if (searchQuery.trim()) {
            const query = searchQuery.toLowerCase();
            filtered = filtered.filter(prediction => 
                prediction.fighter_1_name.toLowerCase().includes(query) ||
                prediction.fighter_2_name.toLowerCase().includes(query) ||
                prediction.event_title.toLowerCase().includes(query) ||
                prediction.winner_name.toLowerCase().includes(query) ||
                prediction.method.toLowerCase().includes(query)
            );
        }
        
        // Apply sorting by event date
        filtered.sort((a, b) => {
            const dateA = new Date(a.event_date);
            const dateB = new Date(b.event_date);
            
            if (sortType === 'date-desc') {
                return dateB.getTime() - dateA.getTime(); // Most recent first
            } else {
                return dateA.getTime() - dateB.getTime(); // Oldest first
            }
        });
        
        return filtered;
    }, [predictions, filterType, searchQuery, sortType]);

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

            {/* Filter and Sort Bar - Only show on Predictions tab */}
            {selectedTab === 'predictions' && (
                <>
                    <View style={styles.filterSortContainer}>
                        {/* Filter Dropdown */}
                        <View style={styles.dropdownContainer}>
                            <TouchableOpacity 
                                style={[styles.dropdownButton, showFilterOptions && styles.dropdownButtonActive]}
                                onPress={() => {
                                    setShowFilterOptions(!showFilterOptions);
                                    setShowSortOptions(false);
                                }}
                            >
                                <Text style={styles.dropdownButtonText}>
                                    {filterType === 'all' ? 'All Predictions' : 
                                     filterType === 'correct' ? 'Correct Predictions' : 
                                     filterType === 'wrong' ? 'Wrong Predictions' : 'Pending Predictions'}
                                </Text>
                                <Text style={[styles.dropdownArrow, showFilterOptions && styles.dropdownArrowUp]}>
                                    ▼
                                </Text>
                            </TouchableOpacity>
                            
                            {showFilterOptions && (
                                <View style={styles.dropdownMenu}>
                                    <TouchableOpacity 
                                        style={[styles.dropdownItem, filterType === 'all' && styles.selectedDropdownItem]}
                                        onPress={() => {
                                            setFilterType('all');
                                            setShowFilterOptions(false);
                                        }}
                                    >
                                        <Text style={[styles.dropdownItemText, filterType === 'all' && styles.selectedDropdownItemText]}>
                                            All Predictions
                                        </Text>
                                    </TouchableOpacity>
                                    <TouchableOpacity 
                                        style={[styles.dropdownItem, filterType === 'correct' && styles.selectedDropdownItem]}
                                        onPress={() => {
                                            setFilterType('correct');
                                            setShowFilterOptions(false);
                                        }}
                                    >
                                        <Text style={[styles.dropdownItemText, filterType === 'correct' && styles.selectedDropdownItemText]}>
                                            Correct Predictions ✓
                                        </Text>
                                    </TouchableOpacity>
                                    <TouchableOpacity 
                                        style={[styles.dropdownItem, filterType === 'wrong' && styles.selectedDropdownItem]}
                                        onPress={() => {
                                            setFilterType('wrong');
                                            setShowFilterOptions(false);
                                        }}
                                    >
                                        <Text style={[styles.dropdownItemText, filterType === 'wrong' && styles.selectedDropdownItemText]}>
                                            Wrong Predictions ✗
                                        </Text>
                                    </TouchableOpacity>
                                    <TouchableOpacity 
                                        style={[styles.dropdownItem, filterType === 'pending' && styles.selectedDropdownItem]}
                                        onPress={() => {
                                            setFilterType('pending');
                                            setShowFilterOptions(false);
                                        }}
                                    >
                                        <Text style={[styles.dropdownItemText, filterType === 'pending' && styles.selectedDropdownItemText]}>
                                            Pending Predictions
                                        </Text>
                                    </TouchableOpacity>
                                </View>
                            )}
                        </View>
                        
                        {/* Sort Dropdown */}
                        <View style={styles.dropdownContainer}>
                            <TouchableOpacity 
                                style={[styles.dropdownButton, showSortOptions && styles.dropdownButtonActive]}
                                onPress={() => {
                                    setShowSortOptions(!showSortOptions);
                                    setShowFilterOptions(false);
                                }}
                            >
                                <Text style={styles.dropdownButtonText}>
                                    {sortType === 'date-desc' ? 'Newest First' : 'Oldest First'}
                                </Text>
                                <Text style={[styles.dropdownArrow, showSortOptions && styles.dropdownArrowUp]}>
                                    ▼
                                </Text>
                            </TouchableOpacity>
                            
                            {showSortOptions && (
                                <View style={styles.dropdownMenu}>
                                    <TouchableOpacity 
                                        style={[styles.dropdownItem, sortType === 'date-desc' && styles.selectedDropdownItem]}
                                        onPress={() => {
                                            setSortType('date-desc');
                                            setShowSortOptions(false);
                                        }}
                                    >
                                        <Text style={[styles.dropdownItemText, sortType === 'date-desc' && styles.selectedDropdownItemText]}>
                                            Newest First ↓
                                        </Text>
                                    </TouchableOpacity>
                                    <TouchableOpacity 
                                        style={[styles.dropdownItem, sortType === 'date-asc' && styles.selectedDropdownItem]}
                                        onPress={() => {
                                            setSortType('date-asc');
                                            setShowSortOptions(false);
                                        }}
                                    >
                                        <Text style={[styles.dropdownItemText, sortType === 'date-asc' && styles.selectedDropdownItemText]}>
                                            Oldest First ↑
                                        </Text>
                                    </TouchableOpacity>
                                </View>
                            )}
                        </View>
                    </View>
                    
                    {/* Search Bar */}
                    <View style={styles.searchContainer}>
                        <TextInput
                            style={styles.searchInput}
                            placeholder="Search predictions..."
                            value={searchQuery}
                            onChangeText={setSearchQuery}
                            placeholderTextColor="#9ca3af"
                        />
                    </View>
                </>
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
                                    <Text style={[styles.headerCell, styles.predictionColumn]}>Fighter</Text>
                                    <Text style={[styles.headerCell, styles.methodColumn]}>Method</Text>
                                    <Text style={[styles.headerCell, styles.roundColumn]}>Round</Text>
                                </View>

                                {/* Table Body */}
                                {filteredPredictions.map((prediction, idx) => {
                                    const fighter1Name = formatFighterName(prediction.fighter_1_name);
                                    const fighter2Name = formatFighterName(prediction.fighter_2_name);
                                    
                                    return (
                                        <View key={idx} style={[styles.tableRow, idx % 2 === 0 && styles.evenRow]}>
                                            <View style={[styles.tableCell, styles.fightColumn]}>
                                                <View style={styles.fighterNamesContainer}>
                                                    <View style={styles.fighterNameWrapper}>
                                                        <Text style={styles.fighterFirstName}>{fighter1Name.firstName}</Text>
                                                        {fighter1Name.lastName && (
                                                            <Text style={styles.fighterLastName}>{fighter1Name.lastName}</Text>
                                                        )}
                                                    </View>
                                                    <Text style={styles.vsText}>vs</Text>
                                                    <View style={styles.fighterNameWrapper}>
                                                        <Text style={styles.fighterFirstName}>{fighter2Name.firstName}</Text>
                                                        {fighter2Name.lastName && (
                                                            <Text style={styles.fighterLastName}>{fighter2Name.lastName}</Text>
                                                        )}
                                                    </View>
                                                </View>
                                            </View>
                                            <View style={[styles.tableCell, styles.eventColumn]}>
                                                <Text style={styles.cellText} numberOfLines={2}>
                                                    {prediction.event_title.split(' - ')[0]}
                                                </Text>
                                            </View>
                                        <View style={[styles.tableCell, styles.predictionColumn]}>
                                            <View style={styles.predictionNameContainer}>
                                                {(() => {
                                                    const winnerName = formatFighterName(prediction.winner_name);
                                                    return (
                                                        <>
                                                            <Text style={styles.fighterFirstName}>
                                                                {winnerName.firstName}
                                                            </Text>
                                                            {winnerName.lastName && (
                                                                <Text style={styles.fighterLastName}>
                                                                    {winnerName.lastName}
                                                                </Text>
                                                            )}
                                                        </>
                                                    );
                                                })()}
                                            </View>
                                            {prediction.result && (
                                                <Text style={[styles.indicator, prediction.result.fighter ? styles.correct : styles.incorrect]}>
                                                    {prediction.result.fighter ? '✓' : '✗'}
                                                </Text>
                                            )}
                                        </View>
                                        <View style={[styles.tableCell, styles.methodColumn]}>
                                            <Text style={styles.cellText} numberOfLines={2}>
                                                {prediction.method === 'SUBMISSION' ? 'SUB' : prediction.method === 'DECISION' ? 'DEC' : prediction.method}
                                            </Text>
                                            {prediction.result && (
                                                <Text style={[styles.indicator, prediction.result.method ? styles.correct : styles.incorrect]}>
                                                    {prediction.result.method ? '✓' : '✗'}
                                                </Text>
                                            )}
                                        </View>
                                            <View style={[styles.tableCell, styles.roundColumn]}>
                                                <Text style={styles.cellText} numberOfLines={1}>
                                                    {prediction.round ? `R${prediction.round}` : '-'}
                                                </Text>
                                                {prediction.result && (
                                                    <Text style={[styles.indicator, prediction.result.round ? styles.correct : styles.incorrect]}>
                                                        {prediction.result.round ? '✓' : '✗'}
                                                    </Text>
                                                )}
                                            </View>
                                        </View>
                                    );
                                })}
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
        paddingVertical: 10,
        paddingHorizontal: 6,
        borderBottomWidth: 1,
        borderBottomColor: '#e9ecef',
        minHeight: 80,
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
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
    },
    cellText: {
        fontSize: 12,
        color: '#212529',
        textAlign: 'center',
    },
    indicator: {
        fontSize: 14,
        fontWeight: 'bold',
        marginTop: 2,
    },
    correct: {
        color: '#22c55e',
    },
    incorrect: {
        color: '#ef4444',
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
    roundColumn: {
        flex: 1.5,
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
    fighterNamesContainer: {
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
    },
    fighterNameWrapper: {
        alignItems: 'center',
        justifyContent: 'center',
    },
    fighterFirstName: {
        fontSize: 11,
        fontWeight: '600',
        color: '#212529',
        textAlign: 'center',
    },
    fighterLastName: {
        fontSize: 11,
        fontWeight: '600',
        color: '#212529',
        textAlign: 'center',
    },
    vsText: {
        fontSize: 10,
        color: '#6c757d',
        fontStyle: 'italic',
        marginVertical: 2,
    },
    predictionNameContainer: {
        alignItems: 'center',
        justifyContent: 'center',
    },
    filterSortContainer: {
        flexDirection: 'row',
        marginHorizontal: 8,
        marginTop: 8,
        marginBottom: 4,
        gap: 8,
    },
    dropdownContainer: {
        flex: 1,
        position: 'relative',
        zIndex: 1000,
    },
    dropdownButton: {
        backgroundColor: '#fff',
        borderRadius: 8,
        paddingHorizontal: 16,
        paddingVertical: 12,
        borderWidth: 1,
        borderColor: '#e9ecef',
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.05,
        shadowRadius: 2,
        elevation: 1,
    },
    dropdownButtonActive: {
        borderColor: '#007bff',
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 2,
    },
    dropdownButtonText: {
        fontSize: 14,
        fontWeight: '500',
        color: '#495057',
        flex: 1,
    },
    dropdownArrow: {
        fontSize: 12,
        color: '#6c757d',
        marginLeft: 8,
        transform: [{ rotate: '0deg' }],
    },
    dropdownArrowUp: {
        transform: [{ rotate: '180deg' }],
    },
    dropdownMenu: {
        position: 'absolute',
        top: '100%',
        left: 0,
        right: 0,
        backgroundColor: '#fff',
        borderRadius: 8,
        borderWidth: 1,
        borderColor: '#e9ecef',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.15,
        shadowRadius: 8,
        elevation: 8,
        marginTop: 4,
        overflow: 'hidden',
        zIndex: 1001,
    },
    dropdownItem: {
        paddingHorizontal: 16,
        paddingVertical: 12,
        borderBottomWidth: 1,
        borderBottomColor: '#f1f3f4',
    },
    selectedDropdownItem: {
        backgroundColor: '#f8f9fa',
    },
    dropdownItemText: {
        fontSize: 14,
        color: '#495057',
    },
    selectedDropdownItemText: {
        color: '#007bff',
        fontWeight: '600',
    },
});